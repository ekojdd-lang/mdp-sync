from models.article import Article
from backend.core.browser import BrowserManager
from playwright.async_api import Page

import asyncio
import json
import traceback
from typing import Any, Optional


class MaisonPresseAPI:

    def __init__(self):
        self.browser_manager = BrowserManager()
        self.page: Optional[Page] = None

    # ==================================================
    # INIT
    # ==================================================
    async def init(self):

        await self.browser_manager.init()
        self.page = self.browser_manager.page

        if self.page is None:
            raise Exception("PAGE PLAYWRIGHT INTROUVABLE")

        print("Ouverture session MDP...")
        await self.connect()

    # ==================================================
    # CONNECT
    # ==================================================
    async def connect(self):

        if self.page is None:
            raise Exception("PAGE NON INITIALISÉE")

        for attempt in range(3):

            try:
                await self.page.goto(
                    "https://www.maisondelapressegabon.com/gestion/articles.php",
                    timeout=60000,
                    wait_until="domcontentloaded"
                )

                await self.page.wait_for_timeout(3000)
                print("Connexion OK")
                return

            except Exception as e:
                print(f"Tentative {attempt + 1} échouée : {e}")
                await asyncio.sleep(3)

        raise Exception("IMPOSSIBLE DE SE CONNECTER AU SITE MDP")

    # ==================================================
    # VALIDATION ARTICLE (ALIGNÉ MODELE)
    # ==================================================
    def is_valid_article(self, article: Any) -> bool:
        return (
            isinstance(article, dict)
            and bool(article.get("gencod") or article.get("ean") or article.get("isbn"))
            and bool(article.get("titre"))
        )

    # ==================================================
    # GET ARTICLE
    # ==================================================
    async def get_article(self, gencod: str):

        if self.page is None:
            raise Exception("PAGE NON INITIALISÉE")

        try:

            TYPE_PRIORITY = [1, 6, 5]
            article_data: Optional[dict] = None
            used_type: Optional[int] = None

            for type_produit in TYPE_PRIORITY:

                url = (
                    "https://www.maisondelapressegabon.com/"
                    f"gestion/api/articles.php?action=getArticle"
                    f"&gencod={gencod}&typeProduit={type_produit}"
                )

                data = await self.page.evaluate(
                    """
                    async (url) => {
                        try {
                            const response = await fetch(url, {
                                method: 'GET',
                                credentials: 'include'
                            });
                            return await response.json();
                        } catch (e) {
                            return { success: false, error: String(e) };
                        }
                    }
                    """,
                    url
                )

                candidate = (data or {}).get("article")

                if self.is_valid_article(candidate):
                    article_data = candidate
                    used_type = type_produit
                    break

            # DEBUG
            print("\n==== ARTICLE BRUT ====\n")
            print(json.dumps(article_data, indent=4, ensure_ascii=False) if article_data else "AUCUN ARTICLE")
            print("\n======================\n")

            # VALIDATION FINALE (ALIGNÉE MODÈLE)
            if not isinstance(article_data, dict):
                return {
                    "success": False,
                    "gencod": gencod,
                    "message": "ARTICLE INTROUVABLE",
                    "article": None
                }

            if not (article_data.get("gencod") or article_data.get("ean") or article_data.get("isbn")):
                return {
                    "success": False,
                    "gencod": gencod,
                    "message": "ARTICLE SANS IDENTIFIANT",
                    "article": None
                }

            if not article_data.get("titre"):
                return {
                    "success": False,
                    "gencod": gencod,
                    "message": "ARTICLE SANS TITRE",
                    "article": None
                }

            article = Article(article_data)

            return {
                "success": True,
                "gencod": gencod,
                "message": f"ARTICLE TROUVÉ (typeProduit={used_type})",
                "article": article.to_dict()
            }

        except Exception as e:
            traceback.print_exc()

            return {
                "success": False,
                "gencod": gencod,
                "message": f"ERREUR API : {str(e)}",
                "article": None
            }

    # ==================================================
    # CLOSE
    # ==================================================
    async def close(self):
        await self.browser_manager.close()