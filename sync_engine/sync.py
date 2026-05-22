from playwright.sync_api import sync_playwright
import os

SAVE_DIR = "captures"

os.makedirs(SAVE_DIR, exist_ok=True)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context()

    page = context.new_page()

    # =========================
    # INTERCEPTION REQUETES
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
            print("Erreur request:", e)

    # =========================
    # INTERCEPTION REPONSES
    # =========================

    def log_response(response):

        try:

            request = response.request

            if request.resource_type in ["xhr", "fetch"]:

                content_type = response.headers.get("content-type", "")

                print("\n------------------------")
                print("REPONSE AJAX")
                print("------------------------")
                print("URL :", response.url)
                print("STATUS :", response.status)
                print("CONTENT TYPE :", content_type)

                # Sauvegarde JSON
                if "application/json" in content_type:

                    body = response.text()

                    filename = response.url.split("/")[-1]
                    filename = filename.replace("?", "_")
                    filename = filename + ".json"

                    path = os.path.join(SAVE_DIR, filename)

                    with open(path, "w", encoding="utf-8") as f:
                        f.write(body)

                    print("JSON sauvegardé :", path)

                # Sauvegarde HTML
                elif "text/html" in content_type:

                    body = response.text()

                    if len(body) > 500:

                        filename = response.url.split("/")[-1]
                        filename = filename.replace("?", "_")

                        if filename == "":
                            filename = "index"

                        filename += ".html"

                        path = os.path.join(SAVE_DIR, filename)

                        with open(path, "w", encoding="utf-8") as f:
                            f.write(body)

                        print("HTML sauvegardé :", path)

        except Exception as e:
            print("Erreur response:", e)

    page.on("request", log_request)
    page.on("response", log_response)

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

    print("\nFAIS CECI :")
    print("- recherche produit")
    print("- change page")
    print("- filtre")
    print("- trie colonnes")
    print("- ouvre produit")

    input("\nPuis ENTREE pour fermer...")

    browser.close()