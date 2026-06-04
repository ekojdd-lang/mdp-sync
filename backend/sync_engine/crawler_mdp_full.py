import asyncio
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime
from typing import Set

from playwright.async_api import (
    async_playwright,
    Page,
    Browser,
    Playwright,
    BrowserContext
)

from core.database import DatabaseManager
from models.article import Article
from sync_engine.excel_loader import ExcelPricingLoader
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from core.database import DatabaseManager

BASE = "https://www.maisondelapressegabon.com"
BASE_GESTION = f"{BASE}/gestion"
API_ENDPOINT = f"{BASE_GESTION}/api/articles.php"
RAYONS_PAGE = f"{BASE_GESTION}/rayons_catalogue.php"
SEARCH_PAGE = f"{BASE}/listeliv.php"

TYPE_PRODUITS = {
    "paper": 1,
}

SEEN_CODES_SAVE_INTERVAL = 50

# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger("mdp-crawler")


# =========================================================
# API
# =========================================================
class MaisonPresseAPI:
    def __init__(self, page: Page):
        self.page = page

    def is_valid_article(self, article: Any) -> bool:
        return (
            isinstance(article, dict)
            and (article.get("gencod") or article.get("ean") or article.get("isbn"))
            and article.get("titre")
        )

    async def get_article(self, gencod: str) -> Dict:
        TYPE_PRIORITY = [1, 6, 5]

        for type_produit in TYPE_PRIORITY:
            url = (
                f"{API_ENDPOINT}?action=getArticle"
                f"&gencod={gencod}&typeProduit={type_produit}"
            )

            try:
                data = await self.page.evaluate(
                    """async (url) => {
                        const r = await fetch(url, { credentials: 'include' });
                        return await r.json();
                    }""",
                    url
                )

                article = (data or {}).get("article")

                if self.is_valid_article(article):
                    return {
                        "success": True,
                        "article": article
                    }

            except Exception:
                continue

        return {"success": False, "article": None}


# =========================================================
# PARSER
# =========================================================
class SearchResultsParser:
    @staticmethod
    def extract_gencods_from_html(html: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        results = set()

        for el in soup.find_all(attrs={"data-gencod": True}):
            v = el.get("data-gencod")
            if v and str(v).isdigit():
                results.add(str(v))

        return list(results)


class RayonsParser:
    @staticmethod
    def extract_rayons_from_html(html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"id": "rayonsMedialog"})
        if not table:
            return []

        rayons = []
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 3:
                rayons.append({
                    "code": cols[0].get_text(strip=True),
                    "libelle": cols[1].get_text(strip=True),
                    "nombre": int(cols[2].get_text(strip=True) or 0)
                })

        return rayons


# =========================================================
# CRAWLER PRO
# =========================================================
class MDPCrawlerFull:

    def __init__(self, excel_loader: Optional[ExcelPricingLoader] = None):
        

        self.db = DatabaseManager(Path("data/mdp.db"))
        self.api: Optional[MaisonPresseAPI] = None

        self.excel_loader = excel_loader or ExcelPricingLoader()

        self.gencods_from_excel = (
            self.excel_loader.get_all_gencods_by_type("5")
            | self.excel_loader.get_all_gencods_by_type("6")
        )

        self.seen_codes = set()
        self.seen_rayons = set()
        self.seen_lock = asyncio.Lock()

        self.push_queue = asyncio.Queue()

        self.articles_saved = 0
        self.errors = 0
        
    def get_all_gencods_by_type(
            self,
            type_produit: str
        ) -> Set[str]:

            return {
                article.gencod
                for article in self.all_articles.values()
                if str(article.type_produit).strip() == str(type_produit)
            }
        
    

    # =====================================================
    async def init(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)

        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

        self.api = MaisonPresseAPI(self.page)

        self.push_task = asyncio.create_task(self.push_worker())

    # =====================================================
    async def push_worker(self):
        while True:
            article = await self.push_queue.get()

            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    await client.post(
                        "http://127.0.0.1:8000/internal/crawler/article",
                        json=article
                    )

            except Exception as e:
                log.error(f"PUSH ERROR → {e}")

            finally:
                self.push_queue.task_done()

    # =====================================================
    def save(self, article_dict: dict):
        if not isinstance(article_dict, dict):
            return

        try:
            article = Article(article_dict).to_dict()


            self.articles_saved += 1

            # push API async
            self.push_queue.put_nowait(article)

        except Exception as e:
            self.errors += 1
            log.error(f"SAVE ERROR → {e}")

    # =====================================================
    async def get_article_from_api(self, gencod: str):
        return await self.api.get_article(gencod)

    # =====================================================
    async def crawl_by_rayons(self, base="paper"):
        await self.page.goto(f"{RAYONS_PAGE}?base={base}")
        html = await self.page.content()

        rayons = RayonsParser.extract_rayons_from_html(html)

        for rayon in rayons:
            code = rayon["code"]

            async with self.seen_lock:
                if code in self.seen_rayons:
                    continue
                self.seen_rayons.add(code)

            await self.page.goto(f"{SEARCH_PAGE}?coderayonmag={code}")
            html = await self.page.content()

            gencods = SearchResultsParser.extract_gencods_from_html(html)

            for g in gencods:

                if g in self.gencods_from_excel:
                    continue

                async with self.seen_lock:
                    if g in self.seen_codes:
                        continue
                    self.seen_codes.add(g)

                result = await self.get_article_from_api(g)

                if result.get("success"):
                    self.save(result["article"])

                await asyncio.sleep(0.2)

    # =====================================================
    async def run(self):
        await self.crawl_by_rayons("paper")

        await self.push_queue.join()

        log.info("DONE")

    # =====================================================
    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        if hasattr(self, "push_task"):
            self.push_task.cancel()

        try:
            await self.push_task
        except asyncio.CancelledError:
            pass