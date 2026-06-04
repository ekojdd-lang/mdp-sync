from playwright.async_api import async_playwright


class PlaywrightManager:

    _playwright = None
    _browser = None
    _lock = False

    # ==========================================
    # INIT SAFE
    # ==========================================
    @classmethod
    async def init(cls, headless: bool = False):

        if cls._browser:
            return cls._browser

        if cls._lock:
            raise Exception("Playwright en cours d'initialisation")

        cls._lock = True

        try:
            cls._playwright = await async_playwright().start()

            cls._browser = await cls._playwright.chromium.launch(
                headless=headless
            )

            return cls._browser

        finally:
            cls._lock = False

    # ==========================================
    # GET BROWSER
    # ==========================================
    @classmethod
    async def get_browser(cls):

        if cls._browser is None:
            await cls.init()

        return cls._browser

    # ==========================================
    # CLOSE SAFE
    # ==========================================
    @classmethod
    async def close(cls):

        if cls._browser:
            try:
                await cls._browser.close()
            except Exception as e:
                print("browser close error:", e)
            finally:
                cls._browser = None

        if cls._playwright:
            try:
                await cls._playwright.stop()
            except Exception as e:
                print("playwright stop error:", e)
            finally:
                cls._playwright = None