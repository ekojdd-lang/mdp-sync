from playwright.sync_api import sync_playwright
import time


class MDPCrawler:

    def __init__(self):
        self.hits = set()

    # ==========================================
    # FULL NETWORK LOGGER (IMPORTANT)
    # ==========================================
    def log_request(self, request):

        try:
            if request.resource_type not in ["xhr", "fetch"]:
                return

            url = request.url

            print("\n🔥 XHR:", url)

            self.hits.add(url)

        except Exception:
            pass

    # ==========================================
    # SAFE CLICK TRIGGER
    # ==========================================
    def trigger_ui(self, page):

        try:
            # champs recherche possibles
            inputs = [
                "input",
                "#search",
                "#search-gencod",
                "input[type='text']"
            ]

            for selector in inputs:
                if page.locator(selector).count() > 0:
                    page.locator(selector).first.click()
                    page.keyboard.type("test")
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(2000)
                    break

        except:
            pass

    # ==========================================
    # RUN
    # ==========================================
    def run(self):

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.on("request", self.log_request)

            print("LOGIN...")
            page.goto("https://www.maisondelapressegabon.com/gestion/")
            input("LOGIN puis ENTER...")

            bases = ["paper", "jouet", "papeterie", "divers"]

            for base in bases:

                print("\n========================")
                print("BASE:", base)
                print("========================")

                page.goto(
                    f"https://www.maisondelapressegabon.com/gestion/rayons_catalogue.php?base={base}"
                )

                page.wait_for_timeout(3000)

                # 🔥 TRIGGER REAL AJAX
                self.trigger_ui(page)

                # scroll massif
                for i in range(20):
                    page.mouse.wheel(0, 5000)
                    page.wait_for_timeout(700)

                # clique zones pour déclencher filtres dynamiques
                for _ in range(3):
                    page.mouse.click(500, 400)
                    page.wait_for_timeout(1500)

            print("\n========================")
            print("FIN")
            print("TOTAL XHR:", len(self.hits))
            print("========================")

            input("ENTER")
            browser.close()


if __name__ == "__main__":
    MDPCrawler().run()