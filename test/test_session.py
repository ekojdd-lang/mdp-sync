from playwright.sync_api import sync_playwright
import json

URL = "https://www.maisondelapressegabon.com/gestion/api/articles.php?action=getArticle&gencod=9782017253709&typeProduit=1"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    # Recharge session sauvegardée
    context = browser.new_context(
       storage_state="playwright/state.json"
    )

    page = context.new_page()

    print("Ouverture API...")

    page.goto(URL)

    page.wait_for_timeout(2000)

    content = page.locator("body").inner_text()

    print("\n===== CONTENU =====\n")
    print(content)

    # lecture JSON
    data = json.loads(content)

    print("\n===== ARTICLE =====")
    print(data["article"]["titre"])

    input("\nENTREE pour fermer...")

    browser.close()