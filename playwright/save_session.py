from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context()

    page = context.new_page()

    # Ouvre la page login
    page.goto("https://www.maisondelapressegabon.com/gestion")

    # Connexion manuelle
    input("Connecte-toi puis ENTREE...")

    # Sauvegarde session
    context.storage_state(path="state.json")

    print("SESSION SAUVEGARDEE")

    input("ENTREE pour fermer...")

    browser.close()