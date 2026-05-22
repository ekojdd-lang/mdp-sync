from backend.core.playwright_manager import PlaywrightManager


class BrowserManager:

    def __init__(self):

        self.browser = None

        self.context = None

        self.page = None

    async def init(self):

        self.browser = await PlaywrightManager.get_browser()

        self.context = await self.browser.new_context(
            storage_state="state.json"
        )

        self.page = await self.context.new_page()

    async def close(self):

        # ==========================================
        # CLOSE PAGE
        # ==========================================

        try:

            if self.page:

                await self.page.close()

                self.page = None

        except Exception as e:

            print("Erreur fermeture page:", e)

        # ==========================================
        # CLOSE CONTEXT
        # ==========================================

        try:

            if self.context:

                await self.context.close()

                self.context = None

        except Exception as e:

            print("Erreur fermeture context:", e)

        # ==========================================
        # RESET BROWSER REF
        # ==========================================

        self.browser = None