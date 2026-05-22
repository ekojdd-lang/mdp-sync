from io import BytesIO
from typing import List
import ssl

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from playwright.sync_api import sync_playwright

from reportlab.platypus import (
    SimpleDocTemplate,
    Image,
    Paragraph,
    Spacer,TableStyle, Table
)

from reportlab.platypus.flowables import HRFlowable

from core.database import DatabaseManager
from fastapi.middleware.cors import CORSMiddleware
from urllib.request import urlopen

# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="MDP Sync API",
    version="2.0.0",
    description="API ERP Maison de la Presse"
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.1.65:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# MODELS
# =========================================================

class DevisArticle(BaseModel):

    gencod: str | None = None

    isbn: str | None = None

    titre: str

    auteurs: str | None = None

    editeur: str | None = None

    prix: float

    disponibilite: str | None = None

    image_url: str | None = None

    presentation: str | None = None

    categorie: str | None = None

    langue: str | None = None

    nombre_pages: int | None = None

    date_parution: str | None = None

    stock: int | None = 0

    quantity: int


class DevisRequest(BaseModel):

    client: str

    articles: List[DevisArticle]


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "MDP Sync API",
        "status": "online",
        "version": "2.0.0"
    }


# =========================================================
# ARTICLES PAGINÉS
# =========================================================

@app.get("/api/articles")
def get_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = ""
):

    db = DatabaseManager()

    try:

        offset = (page - 1) * limit

        articles = db.get_articles_paginated(
            limit=limit,
            offset=offset,
            search=search
        )

        total_articles = db.count_articles(
            search=search
        )

        total_pages = (
            total_articles + limit - 1
        ) // limit

        return {

            "items": [
                dict(article)
                for article in articles
            ],

            "total": total_articles,

            "page": page,

            "limit": limit,

            "pages": total_pages
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()


# =========================================================
# ARTICLE DETAIL
# =========================================================

@app.get("/api/articles/{gencod}")
def get_article(gencod: str):

    db = DatabaseManager()

    try:

        article = db.get_article(gencod)

        if not article:

            raise HTTPException(
                status_code=404,
                detail="Article introuvable"
            )

        return {
            "id": article["id"],
            "gencod": article["gencod"],
            "isbn": article["isbn"],
            "titre": article["titre"],
            "auteurs": article["auteurs"],
            "editeur": article["editeur"],
            "prix": float(article["prix"] or 0),
            "disponibilite": article["disponibilite"],
            "image_url": article["image_url"],
            "presentation": article["presentation"],
            "categorie": article["categorie"],
            "langue": article["langue"],
            "nombre_pages": article["nombre_pages"],
            "date_parution": article["date_parution"],
            "stock": article["stock"],
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()


# =========================================================
# STATS
# =========================================================

@app.get("/api/stats")
def get_stats():

    db = DatabaseManager()

    try:

        articles = db.get_all_articles()

        total_articles = len(articles)

        total_disponibles = sum(
            1
            for article in articles
            if str(article["disponibilite"]) == "1"
        )

        valeur_catalogue = sum(
            float(article["prix"] or 0)
            for article in articles
        )

        valeur_stock = db.get_total_stock_value()

        total_stock = sum(
            int(article["stock"] or 0)
            for article in articles
        )

        return {

            "total_articles": total_articles,

            "articles_disponibles": total_disponibles,

            "valeur_catalogue": valeur_catalogue,

            "valeur_stock": valeur_stock,

            "stock_total": total_stock
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()


# =========================================================
# DELETE ARTICLE
# =========================================================

@app.delete("/api/articles/{gencod}")
def delete_article(gencod: str):

    db = DatabaseManager()

    try:

        article = db.get_article(gencod)

        if not article:

            raise HTTPException(
                status_code=404,
                detail="Article introuvable"
            )

        db.delete_article(gencod)

        return {
            "success": True,
            "message": "Article supprimé"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()


# =========================================================
# PDF DEVIS STYLE DOCUMENT
# =========================================================

@app.post("/api/devis/pdf")
def generate_devis_pdf(
    data: DevisRequest
):

    db = DatabaseManager()

    try:

        from urllib.request import Request, urlopen

        from reportlab.lib.styles import (
            ParagraphStyle
        )

        from reportlab.platypus import (
            Table,
            TableStyle
        )

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "BookTitle",
            parent=styles["BodyText"],
            fontSize=18,
            leading=22,
            spaceAfter=12
        )

        elements = []

        # =====================================================
        # HEADER
        # =====================================================

        title = Paragraph(
            "<font size='24'><b>DEVIS</b></font>",
            styles["Title"]
        )

        elements.append(title)

        elements.append(
            Spacer(1, 10)
        )

        company = Paragraph(
            (
                "<b>Maison de la Presse Gabon</b><br/>"

                "boulevard de la République<br/>"

                "01 Libreville<br/>"

                "Fixe: 00 241 1 72 21 31<br/>"

                "Whatsapp: 066 05 60 27<br/>"

                "Mail: ipc369@yahoo.fr<br/>"

                "Site Web: https://www.maisondelapressegabon.com<br/>"
            ),
            styles["BodyText"]
        )

        elements.append(company)

        elements.append(
            Spacer(1, 20)
        )

        client = Paragraph(
            f"<b>Client :</b> {data.client}",
            styles["BodyText"]
        )

        elements.append(client)

        elements.append(
            Spacer(1, 25)
        )

        total_general = 0

        # =====================================================
        # ARTICLES
        # =====================================================

        for article_request in data.articles:

            # =================================================
            # RECUPERATION COMPLETE DEPUIS DB
            # =================================================

            article_db = None

            if article_request.gencod:

                article_db = db.get_article(
                    article_request.gencod
                )

            if article_db:

                article = dict(article_db)

            else:

                article = {
                    "gencod": article_request.gencod,
                    "isbn": article_request.isbn,
                    "titre": article_request.titre,
                    "auteurs": article_request.auteurs,
                    "editeur": article_request.editeur,
                    "prix": article_request.prix,
                    "disponibilite": article_request.disponibilite,
                    "image_url": article_request.image_url,
                    "presentation": article_request.presentation,
                    "categorie": article_request.categorie,
                    "langue": article_request.langue,
                    "nombre_pages": article_request.nombre_pages,
                    "date_parution": article_request.date_parution,
                    "stock": article_request.stock,
                }

            quantity = article_request.quantity

            prix = float(
                article.get("prix") or 0
            )

            total = prix * quantity

            total_general += total

            # =================================================
            # IMAGE
            # =================================================

            image_element = None

            image_url = article.get(
                "image_url"
            )

            if image_url:

                try:

                    request = Request(
                        image_url,
                        headers={
                            "User-Agent": "Mozilla/5.0"
                        }
                    )

                    ssl_context = (
                        ssl._create_unverified_context()
                    )

                    with urlopen(
                        request,
                        timeout=15,
                        context=ssl_context
                    ) as response:

                        image_data = response.read()

                        image_buffer = BytesIO(
                            image_data
                        )

                        image_element = Image(
                            image_buffer,
                            width=5 * cm,
                            height=7 * cm
                        )

                except Exception as e:

                    print(
                        "Erreur image:",
                        e
                    )

            if not image_element:

                image_element = Paragraph(
                    "<i>Image non disponible</i>",
                    styles["BodyText"]
                )

            # =================================================
            # TITRE
            # =================================================

            titre = Paragraph(
                (
                    f"<b>"
                    f"{article.get('titre') or ''}"
                    f"</b>"
                ),
                title_style
            )

            # =================================================
            # DETAILS
            # =================================================

            disponibilite = article.get(
                "disponibilite"
            )

            if str(disponibilite) == "1":

                disponibilite_text = (
                    "Disponible"
                )

            else:

                disponibilite_text = (
                    "Indisponible"
                )

            details = f"""
            <b>Gencod :</b> {article.get('gencod') or ''}<br/>
            <b>ISBN :</b> {article.get('isbn') or ''}<br/>
            <b>Auteur(s) :</b> {article.get('auteurs') or ''}<br/>
            <b>Éditeur :</b> {article.get('editeur') or ''}<br/>
            <b>Catégorie :</b> {article.get('categorie') or ''}<br/>
            <b>Langue :</b> {article.get('langue') or ''}<br/>
            <b>Nombre de pages :</b> {article.get('nombre_pages') or ''}<br/>
            <b>Date de parution :</b> {article.get('date_parution') or ''}<br/>
            <b>Disponibilité :</b> {disponibilite_text}<br/>
            <b>Stock :</b> {article.get('stock') or 0}<br/>
            <b>Prix unitaire :</b> {prix:,.0f} FCFA<br/>
            <b>Quantité :</b> {quantity}<br/>
            <b>Total :</b> {total:,.0f} FCFA
            """

            info_details = Paragraph(
                details,
                styles["BodyText"]
            )

            info = [
                titre,
                Spacer(1, 6),
                info_details
            ]

            # =================================================
            # TABLE IMAGE + INFOS
            # =================================================

            table = Table(
                [
                    [
                        image_element,
                        info
                    ]
                ],
                colWidths=[
                    6 * cm,
                    10 * cm
                ]
            )

            table.setStyle(
                TableStyle([
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        0
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        0
                    ),
                ])
            )

            elements.append(table)

            elements.append(
                Spacer(1, 15)
            )

            # =================================================
            # PRESENTATION
            # =================================================

            presentation = article.get(
                "presentation"
            )

            if presentation:

                resume_title = Paragraph(
                    "<b>Présentation</b>",
                    styles["Heading3"]
                )

                elements.append(
                    resume_title
                )

                elements.append(
                    Spacer(1, 5)
                )

                resume = Paragraph(
                    presentation,
                    styles["BodyText"]
                )

                elements.append(
                    resume
                )

                elements.append(
                    Spacer(1, 20)
                )

            # =================================================
            # SEPARATEUR
            # =================================================

            line = HRFlowable(
                width="100%",
                thickness=1,
                color=colors.grey
            )

            elements.append(line)

            elements.append(
                Spacer(1, 25)
            )

        # =====================================================
        # TOTAL GENERAL
        # =====================================================

        total_text = Paragraph(
            (
                f"<font size='20'>"
                f"<b>Total Général : "
                f"{total_general:,.0f} FCFA"
                f"</b></font>"
            ),
            styles["Heading1"]
        )

        elements.append(
            total_text
        )

        elements.append(
            Spacer(1, 30)
        )

        # =====================================================
        # FOOTER
        # =====================================================

        footer = Paragraph(
            (
                "Merci pour votre confiance.<br/>"
                "Maison de la Presse Gabon"
            ),
            styles["BodyText"]
        )

        elements.append(
            footer
        )

        # =====================================================
        # BUILD PDF
        # =====================================================

        doc.build(elements)

        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                (
                    "attachment; "
                    "filename=devis_mdp.pdf"
                )
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()
        

@app.get("/test-browser")
def test_browser():

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )

            page = browser.new_page()

            page.goto("https://example.com")

            title = page.title()

            browser.close()

            return {
                "success": True,
                "title": title
            }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }