from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        channel="chrome",
        headless=False
    )

    page = browser.new_page()

    print("Test HTTP simple...")

    page.goto("http://example.com")

    print("OK")

    input("ENTREE...")

    browser.close()