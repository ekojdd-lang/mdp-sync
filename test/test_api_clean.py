from playwright.sync_api import sync_playwright
import json

URL = (
    "https://www.maisondelapressegabon.com/"
    "gestion/api/articles.php"
    "?action=getArticle"
    "&gencod=8422084042219"
    "&typeProduit=5"
)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        storage_state="../playwright/state.json"
    )

    page = context.new_page()

    page.goto(
        "https://www.maisondelapressegabon.com/gestion/articles.php",
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(3000)

    print("Requête API...")

    content = page.evaluate(
        """
        async (url) => {

            const response = await fetch(url, {
                method: 'GET',
                credentials: 'include'
            });

            return await response.text();
        }
        """,
        URL
    )

    data = json.loads(content)

    article = data["article"]

    print("\n===== CLES ARTICLE =====\n")

    for key in sorted(article.keys()):
        print(key)

    print("\n===== ARTICLE COMPLET =====\n")

    print(
        json.dumps(
            article,
            indent=2,
            ensure_ascii=False
        )
    )

    browser.close()