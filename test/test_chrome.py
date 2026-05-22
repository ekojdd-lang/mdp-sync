from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        channel="chrome",
        headless=False
    )

    page = browser.new_page()

    print("Ouverture Google...")

    page.goto("https://google.com")

    print("GOOGLE OK")

    input("ENTREE...")

    browser.close()