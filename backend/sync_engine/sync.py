from playwright.sync_api import sync_playwright


def log_request(request):
    try:
        if request.resource_type in ["xhr", "fetch"]:
            print("\nAJAX:", request.url)
    except:
        pass


def main():

    bases = ["paper", "jouet", "papeterie", "divers"]

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.on("request", log_request)

        print("Login...")
        page.goto("https://www.maisondelapressegabon.com/gestion/")
        input("LOGIN puis ENTER...")

        for base in bases:

            print(f"\n=== BASE : {base} ===")

            page.goto(
                f"https://www.maisondelapressegabon.com/gestion/rayons_catalogue.php?base={base}"
            )

            page.wait_for_timeout(3000)

            # 🔥 FORCE INTERACTION UI
            page.keyboard.press("Enter")
            page.wait_for_timeout(2000)

            page.mouse.click(300, 300)
            page.wait_for_timeout(1000)

            # 🔥 SCROLL POUR CHARGEMENT AJAX
            for i in range(20):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(800)

        input("FIN")
        browser.close()


if __name__ == "__main__":
    main()