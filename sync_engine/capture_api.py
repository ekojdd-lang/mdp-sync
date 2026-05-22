from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    # =========================
    # LOG REQUESTS
    # =========================

    def log_request(request):

        try:

            if request.resource_type in ["xhr", "fetch"]:

                print("\n========================")
                print("REQUETE AJAX")
                print("========================")
                print("URL :", request.url)
                print("METHOD :", request.method)

                if request.post_data:
                    print("POST DATA :", request.post_data)

        except Exception as e:
            print("Erreur :", e)

    page.on("request", log_request)

    # =========================
    # LOGIN
    # =========================

    print("Ouverture login...")
    page.goto("https://www.maisondelapressegabon.com/gestion/")

    input("Connecte-toi puis ENTREE...")

    # =========================
    # ARTICLES
    # =========================

    print("Ouverture articles...")
    page.goto("https://www.maisondelapressegabon.com/gestion/articles.php")

    page.wait_for_timeout(3000)

    # =========================
    # TEST GENCOD
    # =========================

    print("\nInjection GENCOD...")

    gencod_input = page.locator("#search-gencod")

    gencod_input.fill("9782017253709")

    page.keyboard.press("Enter")

    page.wait_for_timeout(5000)

    print("\nObserve ce qui se passe.")
    print("Puis ENTREE pour fermer.")

    input()

    browser.close()