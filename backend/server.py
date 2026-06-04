from io import BytesIO
from typing import List, Optional
import asyncio
import logging
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, Body, Query, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from apscheduler.schedulers.background import BackgroundScheduler

from core.database import DatabaseManager
from sync_engine.crawler_mdp_full import MDPCrawlerFull
from sync_engine.excel_loader import ExcelPricingLoader


# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger("mdp-api")


# =========================================================
# APP
# =========================================================
app = FastAPI(
    title="MDP Sync API",
    version="3.0.0",
    description="ERP Maison de la Presse - PRODUCTION"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.1.65:3000",
        "https://mdp-sync.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CONFIG
# =========================================================
DB_PATH = Path("data/mdp.db")

scheduler = BackgroundScheduler()
clients: list[WebSocket] = []

# Singleton database instance
_db: Optional[DatabaseManager] = None

def get_db() -> DatabaseManager:
    """Get singleton database instance"""
    global _db
    if _db is None:
        _db = DatabaseManager(DB_PATH)
    return _db


# =========================================================
# EXCEL LOADER (LAZY)
# =========================================================
_excel_loader = None

def get_excel_loader():
    """Lazy load Excel loader"""
    global _excel_loader
    if _excel_loader is None:
        _excel_loader = ExcelPricingLoader()
    return _excel_loader


# =========================================================
# WEBSOCKET BROADCAST
# =========================================================
async def broadcast(message: dict):
    """Broadcast message to all connected clients"""
    dead = []
    for client in clients:
        try:
            await client.send_json(message)
        except Exception as e:
            log.warning(f"WebSocket error: {e}")
            dead.append(client)

    for d in dead:
        try:
            clients.remove(d)
        except ValueError:
            pass


# =========================================================
# CRAWLER TASK
# =========================================================
async def run_crawler_task():
    """Run crawler asynchronously"""
    log.info("🔄 CRAWLER STARTED")
    try:
        crawler = MDPCrawlerFull(excel_loader=get_excel_loader())
        await crawler.init()
        await crawler.run()
        await crawler.close()
        log.info("✅ CRAWLER COMPLETED")
        
        # Notify all clients of sync completion
        await broadcast({
            "type": "sync_completed",
            "timestamp": asyncio.get_event_loop().time()
        })
        
    except Exception as e:
        log.error(f"❌ CRAWLER ERROR: {e}")
        await broadcast({
            "type": "sync_error",
            "error": str(e)
        })


def schedule_crawler():
    """Wrapper for scheduler"""
    asyncio.run(run_crawler_task())


# =========================================================
# STARTUP/SHUTDOWN
# =========================================================
@app.on_event("startup")
async def startup():
    try:

        if not scheduler.get_job("crawler_daily"):
            scheduler.add_job(
                schedule_crawler,
                "cron",
                hour=12,
                minute=0,
                id="crawler_daily"
            )

        if not scheduler.running:
            scheduler.start()

        log.info("✅ Scheduler started")

        db = get_db()

        log.info(
            f"✅ Database ready ({db.get_total_articles()} articles)"
        )

    except Exception as e:
        log.error(f"❌ STARTUP ERROR: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event"""
    try:
        scheduler.shutdown()
    except:
        pass

    try:
        get_db().close()
    except:
        pass


# =========================================================
# PYDANTIC MODELS
# =========================================================
class DevisArticle(BaseModel):
    """Article dans un devis"""
    gencod: Optional[str] = None
    isbn: Optional[str] = None
    ean: Optional[str] = None
    code_article: Optional[str] = None
    titre: str = Field(..., min_length=1, max_length=200)
    prix: float = Field(..., ge=0, le=999999)
    quantity: int = Field(..., ge=1, le=10000)

    @validator('titre')
    def titre_not_empty(cls, v):
        if not v.strip():
            raise ValueError("titre cannot be empty")
        return v.strip()


class DevisRequest(BaseModel):
    """Request pour créer un devis"""
    client: str = Field(..., min_length=1, max_length=100)
    articles: List[DevisArticle] = Field(..., min_items=1, max_items=500)


class SaleRequest(BaseModel):
    """Request pour enregistrer une vente"""
    articles: List[DevisArticle] = Field(..., min_items=1, max_items=500)
    total: float = Field(..., ge=0, le=999999)


# =========================================================
# HOME
# =========================================================
@app.get("/")
def home():
    """Health check"""
    return {"status": "online", "version": "3.0.0"}


@app.get("/health")
def health():
    """Detailed health check"""
    try:
        db = get_db()
        count = db.get_total_articles()
        total_stock = db.get_total_stock()
        return {
            "status": "healthy",
            "database": "connected",
            "articles_count": count,
            "total_stock": total_stock,
            "websocket_clients": len(clients)
        }
    except Exception as e:
        log.error(f"Health check error: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# =========================================================
# ARTICLES (CACHED + VALIDATED)
# =========================================================
@app.get("/api/articles")
def get_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=100),
    type_produit: str = Query(""),
    editeur: str = Query("")
):
    try:
        db = get_db()

        offset = (page - 1) * limit

        items = db.get_articles_paginated(
            limit=limit,
            offset=offset,
            search=search,
            type_produit=type_produit,
            editeur=editeur
        )

        total = db.count_articles(
            search=search,
            type_produit=type_produit,
            editeur=editeur
        )

        available = len([
            a for a in items
            if int(a.get("stock", 0)) > 0
        ])

        return {
            "items": items,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "total": total,
            "available": available
        }

    except Exception as e:
        log.error(f"❌ Get articles error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/api/articles/{gencod}")
def get_article(gencod: str = PathParam(..., max_length=50)):
    """Get single article by gencod"""
    try:
        if not gencod.strip():
            raise HTTPException(400, "Invalid gencod")

        db = get_db()
        article = db.get_article(gencod)

        if not article:
            raise HTTPException(404, "Article not found")

        return article

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Get article error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# =========================================================
# CRAWLER ENDPOINTS (INTERNAL)
# =========================================================
@app.post("/internal/crawler/article")
async def crawler_article(article: dict = Body(...)):
    """Save article from crawler"""
    try:
        db = get_db()

        if not db.save_article(article):
            raise HTTPException(500, "Failed to save article")

        await broadcast({
            "type": "new_article",
            "article": article
        })

        return {"success": True}

    except Exception as e:
        log.error(f"❌ Crawler article error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/internal/crawler/start")
async def start_crawler():
    """Manually trigger crawler"""
    try:
        await run_crawler_task()
        return {"success": True}

    except Exception as e:
        log.error(f"❌ Start crawler error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# POS - SALES
# =========================================================
@app.post("/api/pos/sale")
async def sale(req: SaleRequest):
    """Record sale transaction"""
    try:
        db = get_db()

        db.begin_batch()

        try:
            for article in req.articles:
                code = (
                    article.code_article
                    or article.gencod
                    or article.isbn
                    or article.ean
                )

                if not code:
                    raise ValueError("No valid article code found")

                db.decrease_stock(code, article.quantity)

            db.end_batch()

            # Broadcast to all clients
            await broadcast({
                "type": "stock_updated",
                "total": len(req.articles),
                "timestamp": asyncio.get_event_loop().time()
            })

            return {"success": True, "articles_updated": len(req.articles)}

        except Exception as e:
            db.rollback_batch()
            raise

    except Exception as e:
        log.error(f"❌ Sale error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# STATS
# =========================================================
@app.get("/api/stats")
def stats():
    try:
        db = get_db()

        total_articles = db.get_total_articles()
        available_articles = db.get_available_articles()
        total_stock = db.get_total_stock()
        inventory_value = db.get_inventory_value()

        return {
            "total_articles": total_articles,
            "available_articles": available_articles,
            "inventory_value": round(inventory_value, 2),
            "total_stock": total_stock
        }

    except Exception as e:
        log.error(f"❌ Stats error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# =========================================================
# FILTERS
# =========================================================
@app.get("/api/filters")
def filters():
    """Get available filter options"""
    try:
        db = get_db()

        return {
            "type_produits": db.get_distinct_type_produits(),
            "publishers": db.get_distinct_publishers()
        }

    except Exception as e:
        log.error(f"❌ Filters error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/internal/excel/sync-type56")
def sync_type56():
    """Sync Type 5/6 articles from Excel"""
    try:
        excel = get_excel_loader()
        articles = excel.get_all_type6_articles()

        count = 0
        for article in articles:
            article_dict = article.to_dict()
            # Initialize stock
            if article_dict.get("stock") is None or article_dict.get("stock") == 0:
                article_dict["stock"] = 1
                
            if get_db().save_article(article_dict):
                count += 1

        return {
            "success": True,
            "count": count,
            "total": len(articles)
        }

    except Exception as e:
        log.error(f"❌ Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# WEBSOCKET - REAL-TIME SYNC
# =========================================================
@app.websocket("/ws/catalog")
async def ws(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    clients.append(websocket)
    
    log.info(f"✅ WebSocket connected. Total clients: {len(clients)}")

    try:
        # Send initial status
        db = get_db()
        await websocket.send_json({
            "type": "connected",
            "articles_count": db.get_total_articles(),
            "total_stock": db.get_total_stock()
        })
        
        while True:
            # Keep connection alive
            await websocket.receive_text()

    except Exception as e:
        log.warning(f"❌ WebSocket disconnected: {e}")
    finally:
        try:
            clients.remove(websocket)
            log.info(f"WebSocket removed. Total clients: {len(clients)}")
        except ValueError:
            pass


# =========================================================
# PDF DEVIS
# =========================================================
@app.post("/api/devis/pdf")
def pdf(data: DevisRequest):
    """Generate PDF devis"""
    try:
        db = get_db()
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        styles = getSampleStyleSheet()
        elements = []

        # Header
        elements.append(Paragraph(f"DEVIS - {data.client}", styles["Heading1"]))
        elements.append(Spacer(1, 20))

        total = 0

        for article in data.articles:
            db_article = db.get_article(article.gencod) if article.gencod else None
            art = db_article if db_article else article.dict()

            prix = float(art.get("prix", article.prix))
            line_total = prix * article.quantity
            total += line_total

            titre = art.get("titre", article.titre)
            elements.append(
                Paragraph(
                    f"{titre} x{article.quantity} @ {prix:.2f}€ = {line_total:.2f}€",
                    styles["Normal"]
                )
            )
            elements.append(Spacer(1, 10))

        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"TOTAL: {total:.2f}€", styles["Heading2"]))

        doc.build(elements)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=devis.pdf"}
        )

    except Exception as e:
        log.error(f"❌ PDF error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")