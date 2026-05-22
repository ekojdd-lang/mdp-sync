import os

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
)

from backend.core.playwright_manager import PlaywrightManager


BASE_URL = "https://www.maisondelapressegabon.com/gestion"

STATE_FILE = "state.json"

USERNAME = "ipc369@yahoo.fr"
PASSWORD = "Libreville963@"


class AuthManager:

    def __init__(self):

        self.browser: Browser | None = None

        self.context: BrowserContext | None = None

        self.page: Page | None = None

    # ==================================================
    # INIT PLAYWRIGHT
    # ==================================================

    async def init(self):

        await PlaywrightManager.init()

        self.browser = await PlaywrightManager.get_browser()

    # ==================================================
    # CONTEXT SAFE RESET
    # ==================================================

    async def _new_context(self, storage=None):

        if self.context:
            await self.context.close()

        assert self.browser is not None

        self.context = await self.browser.new_context(
            storage_state=storage if storage else None
        )

        assert self.context is not None

        self.page = await self.context.new_page()

    # ==================================================
    # SESSION CHECK
    # ==================================================

    async def is_session_valid(self):

        if not os.path.exists(STATE_FILE):
            return False

        try:

            await self._new_context(
                storage=STATE_FILE
            )

            assert self.page is not None

            await self.page.goto(
                BASE_URL,
                wait_until="domcontentloaded"
            )

            await self.page.wait_for_timeout(
                2000
            )

            url = self.page.url.lower()

            print("URL:", url)

            if (
                "login" in url
                or "connexion" in url
            ):
                return False

            if await self.page.locator(
                "input[name='login']"
            ).count() > 0:
                return False

            return True

        except Exception as e:

            print(
                "Session check error:",
                e
            )

            return False

    # ==================================================
    # LOGIN
    # ==================================================

    async def login(self):

        print("Connexion automatique...")

        await self._new_context()

        assert self.page is not None

        await self.page.goto(
            BASE_URL,
            wait_until="domcontentloaded"
        )

        await self.page.wait_for_timeout(
            3000
        )

        print(
            "URL après goto:",
            self.page.url
        )

        # ==================================================
        # DEJA CONNECTE
        # ==================================================

        if "index_ventes" in self.page.url:

            print("Déjà connecté")

            return

        await self.page.wait_for_load_state(
            "domcontentloaded"
        )

        # ==================================================
        # INPUTS
        # ==================================================

        login_input = self.page.locator(
            "input[name='login'], input[type='text']"
        ).first

        password_input = self.page.locator(
            "input[type='password']"
        ).first

        if (
            await login_input.count() == 0
            or await password_input.count() == 0
        ):

            print(
                "❌ Champs login/password introuvables"
            )

            await self.page.screenshot(
                path="debug_login.png",
                full_page=True
            )

            return

        print("Remplissage credentials...")

        await login_input.fill(
            USERNAME
        )

        await password_input.fill(
            PASSWORD
        )

        print(
            "👉 Clique manuellement sur 'Se connecter'"
        )

        await self.page.pause()

        await self.page.wait_for_load_state(
            "networkidle"
        )

        # ==================================================
        # SAVE SESSION
        # ==================================================

        if "gestion" in self.page.url:

            assert self.context is not None

            await self.context.storage_state(
                path=STATE_FILE
            )

            print(
                "SESSION SAUVEGARDEE"
            )

        else:

            print(
                "❌ Login non confirmé"
            )

            await self.page.screenshot(
                path="login_failed.png",
                full_page=True
            )

    # ==================================================
    # INIT SESSION
    # ==================================================

    async def init_session(self):

        await self.init()

        if await self.is_session_valid():

            print("Session valide")

        else:

            print("Session expirée")

            await self.login()

    # ==================================================
    # CLOSE
    # ==================================================

    async def close(self):

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()