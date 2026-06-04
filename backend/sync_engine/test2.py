#!/usr/bin/env python3
"""
Script d'exploration pour trouver la bonne structure API
"""
import asyncio
import json
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

BASE = "https://www.maisondelapressegabon.com/gestion"
API_ENDPOINT = f"{BASE}/api/articles.php"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger("explore")


async def explore():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(
        ignore_https_errors=True,
        extra_http_headers={
            "Referer": f"{BASE}/articles.php",
            "X-Requested-With": "XMLHttpRequest"
        }
    )
    page = await context.new_page()
    request = context.request
    
    try:
        await page.goto(f"{BASE}/", wait_until="domcontentloaded")
        
        input("\n👉 Login et va sur Articles. Puis ENTER...\n")
        
        # =====================================
        # 1. Chercher les gencods dans le DOM
        # =====================================
        log.info("=" * 80)
        log.info("ÉTAPE 1 : Chercher les gencods dans le DOM")
        log.info("=" * 80)
        
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Chercher les attributs data-*
        elements_with_data = soup.find_all(attrs={"data-gencod": True})
        log.info(f"\nÉléments avec data-gencod: {len(elements_with_data)}")
        
        elements_with_id = soup.find_all(attrs={"data-id": True})
        log.info(f"Éléments avec data-id: {len(elements_with_id)}")
        
        # Chercher les inputs
        gencod_inputs = soup.find_all("input", {"id": "gencod"})
        log.info(f"Inputs #gencod: {len(gencod_inputs)}")
        
        # =====================================
        # 2. Essayer une recherche
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("ÉTAPE 2 : Tester une recherche via le formulaire")
        log.info("=" * 80)
        
        # Remplir le formulaire de recherche
        search_input = await page.query_selector("#search-gencod")
        if search_input:
            await search_input.fill("9782253159064")
            log.info("✓ Gencod saisi dans le formulaire")
            
            # Cliquer sur le bouton recherche
            search_btn = await page.query_selector("#search-article")
            if search_btn:
                await search_btn.click()
                await page.wait_for_timeout(3000)
                log.info("✓ Recherche lancée")
                
                # Capturer la réponse API
                # (elle est capturée automatiquement via le network)
        
        # =====================================
        # 3. Tester les sélecteurs GTL
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("ÉTAPE 3 : Chercher les sélecteurs GTL")
        log.info("=" * 80)
        
        # Chercher les select/input de GTL
        gtl_selects = soup.find_all("select", id=lambda x: x and "rayon" in x.lower() if x else False)
        log.info(f"Selects de rayon: {len(gtl_selects)}")
        for sel in gtl_selects[:3]:
            log.info(f"  - {sel.get('id')}: {len(sel.find_all('option'))} options")
        
        # =====================================
        # 4. Inspecter les scripts
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("ÉTAPE 4 : Chercher les données dans les scripts")
        log.info("=" * 80)
        
        scripts = soup.find_all("script")
        log.info(f"Scripts trouvés: {len(scripts)}")
        
        for i, script in enumerate(scripts):
            if script.string and len(script.string) > 100:
                content = script.string[:500]
                if any(x in content.lower() for x in ["gtl", "rayon", "article", "gencod"]):
                    log.info(f"\n📄 Script {i} (pertinent):")
                    log.info(content[:300])
        
        log.info("\n✅ EXPLORATION TERMINÉE")
        
    except Exception as e:
        log.error(f"ERROR → {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await browser.close()
        await playwright.stop()


if __name__ == "__main__":
    asyncio.run(explore())