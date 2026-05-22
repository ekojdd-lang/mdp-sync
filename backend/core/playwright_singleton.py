from playwright.async_api import async_playwright


class PlaywrightSingleton:

    _playwright = None
    _browser = None

    @classmethod
    async def get_browser(cls):

        if cls._playwright is None:
            cls._playwright = await async_playwright().start()

        if cls._browser is None:
            cls._browser = await cls._playwright.chromium.launch(
                headless=False
            )

        return cls._browser

    @classmethod
    async def stop(cls):

        try:

            if cls._browser:

                await cls._browser.close()

                cls._browser = None

        except Exception as e:

            print("Erreur browser.close():", e)

        try:

            if cls._playwright:

                await cls._playwright.stop()

                cls._playwright = None

        except Exception as e:

            print("Erreur playwright.stop():", e)