from playwright.sync_api import sync_playwright
import json

URL = "https://www.maisondelapressegabon.com/gestion/api/articles.php?action=getArticle&gencod=9782017253709&typeProduit=1"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context()

    page = context.new_page()

    # ouverture login
    page.goto("https://www.maisondelapressegabon.com/gestion/index_ventes.php")

    input("Connecte-toi puis ENTREE...")

    # appel DIRECT dans le navigateur connecté
    page.goto(URL)

    # attendre chargement
    page.wait_for_timeout(3000)

    # récupérer contenu brut
    content = page.locator("body").inner_text()

    print("\n===== CONTENU =====\n")
    print(content)

    # tentative parsing JSON
    try:
        data = json.loads(content)

        print("\n===== TITRE =====")
        print(data["article"]["titre"])

    except Exception as e:
        print("\nERREUR JSON :", e)

    input("\nENTREE pour fermer...")

    browser.close()