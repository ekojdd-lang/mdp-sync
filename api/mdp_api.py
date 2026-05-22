from models.article import Article

from backend.core.browser import BrowserManager

from playwright.async_api import Page

import asyncio


class MaisonPresseAPI:

    def __init__(self):

        self.browser_manager = BrowserManager()

        self.page: Page | None = None

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

        retries = 3

        for attempt in range(retries):

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

                print(
                    f"Tentative {attempt + 1} échouée : {e}"
                )

                await asyncio.sleep(3)

        raise Exception(
            "IMPOSSIBLE DE SE CONNECTER AU SITE MDP"
        )

    # ==================================================
    # GET ARTICLE
    # ==================================================
    async def get_article(self, gencod):

        if self.page is None:
            raise Exception("PAGE NON INITIALISÉE")

        try:

            url = (
                "https://www.maisondelapressegabon.com/"
                f"gestion/api/articles.php?action=getArticle"
                f"&gencod={gencod}&typeProduit=1"
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

                        return {
                            success: false,
                            error: String(e)
                        };
                    }
                }
                """,
                url
            )

            # ==========================================
            # VALIDATION
            # ==========================================

            if not isinstance(data, dict):

                return {
                    "success": False,
                    "gencod": gencod,
                    "message": "REPONSE API INVALIDE",
                    "article": None
                }

            article_data = data.get("article")

            if not article_data:

                return {
                    "success": False,
                    "gencod": gencod,
                    "message": "ARTICLE INTROUVABLE",
                    "article": None
                }

            if not article_data.get("titre"):

                return {
                    "success": False,
                    "gencod": gencod,
                    "message": "ARTICLE SANS TITRE",
                    "article": None
                }

            # ==========================================
            # CREATE MODEL
            # ==========================================

            article = Article(article_data)

            return {
                "success": True,
                "gencod": gencod,
                "message": "ARTICLE TROUVÉ",
                "article": article
            }

        except Exception as e:

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