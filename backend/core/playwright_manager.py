from playwright.async_api import async_playwright


class PlaywrightManager:

    _instance = None

    playwright = None

    browser = None

    @classmethod
    async def init(cls):

        if cls._instance is None:

            cls._instance = cls()

            cls.playwright = await async_playwright().start()

            cls.browser = await cls.playwright.chromium.launch(
                headless=False
            )

        return cls._instance

    @classmethod
    async def get_browser(cls):

        if cls.browser is None:

            await cls.init()

        return cls.browser

    @classmethod
    async def close(cls):

        try:

            if cls.browser:

                await cls.browser.close()

                cls.browser = None

        except Exception as e:

            print("browser close error:", e)

        try:

            if cls.playwright:

                await cls.playwright.stop()

                cls.playwright = None

        except Exception as e:

            print("playwright stop error:", e)

        cls._instance = None