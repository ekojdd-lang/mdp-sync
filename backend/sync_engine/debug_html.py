import asyncio
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

BASE = "https://www.maisondelapressegabon.com/gestion"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("debug-html")


async def debug_html():
    """Capture et analyse le HTML avec un navigateur existant."""
    
    try:
        print("\n" + "="*80)
        print("📱 ATTACH À UN NAVIGATEUR EXISTANT")
        print("="*80)
        print("\n1. Ouvre le navigateur Chrome/Chromium manuellement")
        print("2. Va sur: https://www.maisondelapressegabon.com/gestion/")
        print("3. Connecte-toi")
        print("4. Lance ce script (il se connectera au navigateur ouvert)")
        print("\nLe script va utiliser ta session existante!")
        
        # Créer l'instance Playwright AVEC les args de débogage
        playwright = await async_playwright().start()
        
        print("\n⏳ Connexion au navigateur Chrome...")
        
        try:
            # Se connecter au navigateur existant via le port de debug
            browser = await playwright.chromium.connect_over_cdp(
                "http://127.0.0.1:9222",  # Port de debug Chrome par défaut
                timeout=10000
            )
            print("✅ Connecté au navigateur existant!")
            
        except Exception as e:
            print(f"\n❌ Impossible de se connecter au navigateur existant: {e}")
            print("\n💡 Pour utiliser un navigateur existant:")
            print("   Windows: chrome.exe --remote-debugging-port=9222")
            print("   Mac:     /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
            print("   Linux:   google-chrome --remote-debugging-port=9222")
            print("\n⚠️ Ou utilise un navigateur contrôlé par Playwright (plus simple)...\n")
            
            # Fallback : lancer un navigateur neuf
            print("Lancement d'un navigateur automatique...")
            browser = await playwright.chromium.launch(headless=False, slow_mo=100)
        
        # Créer un contexte
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        print(f"\n👉 Navigue jusqu'à une page de recherche d'articles")
        print(f"   Puis appuie sur ENTER ici...")
        
        # Aller sur la page d'accueil
        await page.goto(f"{BASE}/", wait_until="domcontentloaded", timeout=60000)
        
        # Attendre l'input utilisateur
        input()
        
        # L'utilisateur devrait être sur une page de résultats maintenant
        await asyncio.sleep(1)
        
        # Capturer le HTML
        html = await page.content()
        
        # Sauvegarder
        debug_file = Path("debug_search.html")
        debug_file.write_text(html, encoding="utf-8")
        log.info(f"✅ HTML SAVED → {debug_file}")
        log.info(f"HTML SIZE → {len(html)} chars")
        
        # Analyser
        soup = BeautifulSoup(html, "html.parser")
        
        # ===================================
        # DEBUG: Afficher la structure
        # ===================================
        print("\n" + "="*80)
        print("🔍 HTML ANALYSIS")
        print("="*80)
        
        # 1. Chercher tous les éléments avec data-* attributes
        print("\n1️⃣ ELEMENTS AVEC data-* ATTRIBUTES:")
        data_elements = soup.find_all(attrs={"data-gencod": True})
        print(f"   [data-gencod] → {len(data_elements)} trouvés")
        if data_elements:
            print(f"   Exemple:\n{str(data_elements[0])[:300]}\n")
        
        data_elements = soup.find_all(attrs={"data-id": True})
        print(f"   [data-id] → {len(data_elements)} trouvés")
        
        # 2. Chercher les conteneurs article/product
        print("\n2️⃣ CLASSES article/product:")
        selectors_to_try = [
            ".article", ".product", ".item", 
            "[class*='article']", "[class*='product']",
            "tr[data-id]", "tr[data-gencod]",
            ".row", ".col", ".card",
            "table tbody tr"
        ]
        
        found_any = False
        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements:
                found_any = True
                print(f"   ✅ {selector} → {len(elements)} trouvés")
                if len(elements) <= 3:
                    print(f"      Exemple:\n{str(elements[0])[:400]}\n")
        
        if not found_any:
            print(f"   ❌ Aucun sélecteur standard trouvé")
        
        # 3. Chercher les tables
        print("\n3️⃣ TABLES:")
        tables = soup.find_all("table")
        print(f"   Tables trouvées: {len(tables)}")
        if tables:
            rows = tables[0].find_all("tr")
            print(f"   Première table: {len(rows)} lignes")
            if rows and len(rows) > 1:
                print(f"   Header (ligne 1):\n{str(rows[0])[:400]}\n")
                print(f"   Data (ligne 2):\n{str(rows[1])[:400]}\n")
        
        # 4. Chercher les divs
        print("\n4️⃣ DIV CLASSES (TOP 10):")
        div_classes = {}
        for div in soup.find_all("div", class_=True):
            if len(div.get_text(strip=True)) > 10:
                classes = " ".join(sorted(div.get("class", [])))
                div_classes[classes] = div_classes.get(classes, 0) + 1
        
        sorted_classes = sorted(div_classes.items(), key=lambda x: x[1], reverse=True)
        for classes, count in sorted_classes[:10]:
            print(f"   .{classes.replace(' ', '.')} → {count}x")
        
        # 5. Scripts
        print("\n5️⃣ SCRIPTS AVEC DATA:")
        scripts = soup.find_all("script")
        print(f"   Scripts trouvés: {len(scripts)}")
        script_count = 0
        for i, script in enumerate(scripts):
            if script.string and len(script.string) > 50:
                if any(x in script.string.lower() for x in ["article", "product", "data", "{"]):
                    script_count += 1
                    content = script.string[:250]
                    print(f"\n   Script {i} ({len(script.string)} chars): {content}...\n")
                    if script_count >= 3:
                        break
        
        # 6. Liens
        print("\n6️⃣ LIENS ARTICLE (TOP 5):")
        links = soup.find_all("a", href=True)
        article_links = [
            l for l in links 
            if any(x in l.get("href", "").lower() for x in ["article", "gencod", "detail", "product"])
        ]
        print(f"   Liens trouvés: {len(article_links)}")
        if article_links:
            for link in article_links[:5]:
                print(f"   href: {link.get('href')}")
                print(f"   text: {link.get_text(strip=True)[:40]}\n")
        
        # 7. Images
        print("\n7️⃣ IMAGES (TOP 5):")
        images = soup.find_all("img")
        print(f"   Images trouvées: {len(images)}")
        if images:
            for img in images[:5]:
                src = img.get('src', 'N/A')
                alt = img.get('alt', 'N/A')
                print(f"   src: {src}")
                print(f"   alt: {alt}\n")
        
        # 8. Attributs data
        print("\n8️⃣ ATTRIBUTS data-*:")
        all_elements = soup.find_all(True)
        data_attrs = {}
        for elem in all_elements:
            for attr in elem.attrs:
                if attr.startswith("data-"):
                    data_attrs[attr] = data_attrs.get(attr, 0) + 1
        
        if data_attrs:
            for attr, count in sorted(data_attrs.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {attr} → {count}x")
        else:
            print(f"   ❌ Aucun attribut data-*")
        
        print("\n" + "="*80)
        print(f"✅ HTML complet sauvegardé → {debug_file}")
        print("="*80 + "\n")
        
        # Fermer
        await browser.close()
        await playwright.stop()
        
    except Exception as e:
        log.error(f"ERROR → {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_html())
