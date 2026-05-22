from playwright.sync_api import sync_playwright

URL = (
    "https://www.maisondelapressegabon.com/"
    "gestion/api/articles.php"
    "?action=getArticle"
    "&gencod=9782017253709"
    "&typeProduit=1"
)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        storage_state="playwright/state.json"
    )

    page = context.new_page()

    # IMPORTANT
    # ouvrir une page du site AVANT fetch
    page.goto(
        "https://www.maisondelapressegabon.com/gestion/articles.php"
    )

    page.wait_for_timeout(3000)

    print("Requête API...")

    data = page.evaluate(
        """
        async (url) => {

            const response = await fetch(url, {
                method: 'GET',
                credentials: 'include'
            });

            return await response.json();
        }
        """,
        URL
    )

    print("\n===== ARTICLE =====")
    print(data["article"]["titre"])

    input("\nENTREE pour fermer...")

    browser.close()