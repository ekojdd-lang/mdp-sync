#!/usr/bin/env python3
"""
Script pour analyser la page rayons_catalogue.php
"""
import asyncio
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pathlib import Path

BASE = "https://www.maisondelapressegabon.com/gestion"
RAYONS_PAGE = f"{BASE}/rayons_catalogue.php"

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("rayons-analysis")


async def analyze_rayons_page():
    """Analyse la page rayons_catalogue.php"""
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(ignore_https_errors=True)
    page = await context.new_page()
    
    try:
        await page.goto(f"{BASE}/", wait_until="domcontentloaded")
        
        input("\n👉 Login et reste sur la page. Puis ENTER...\n")
        
        log.info("=" * 80)
        log.info("NAVIGATION VERS rayons_catalogue.php")
        log.info("=" * 80)
        
        await page.goto(RAYONS_PAGE, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        
        html = await page.content()
        
        # Sauvegarder
        Path("rayons_catalogue.html").write_text(html, encoding="utf-8")
        log.info("✓ HTML sauvegardé dans rayons_catalogue.html\n")
        
        # Analyser
        soup = BeautifulSoup(html, "html.parser")
        
        # =====================================
        log.info("=" * 80)
        log.info("1️⃣ TABLES")
        log.info("=" * 80)
        
        tables = soup.find_all("table")
        log.info(f"Tables trouvées: {len(tables)}\n")
        
        if tables:
            for t_idx, table in enumerate(tables[:2]):
                rows = table.find_all("tr")
                log.info(f"📋 Table {t_idx}: {len(rows)} lignes")
                
                if rows:
                    # En-têtes
                    headers = rows[0].find_all(["th", "td"])
                    log.info(f"   En-têtes: {[h.get_text(strip=True)[:20] for h in headers[:5]]}")
                    
                    # Données
                    if len(rows) > 1:
                        for row_idx, row in enumerate(rows[1:4]):  # Premières 3 lignes
                            cells = row.find_all("td")
                            if cells:
                                cell_texts = [c.get_text(strip=True)[:30] for c in cells[:5]]
                                log.info(f"   Ligne {row_idx}: {cell_texts}")
        
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("2️⃣ LISTES (UL/LI)")
        log.info("=" * 80)
        
        lists = soup.find_all(["ul", "ol"])
        log.info(f"Listes trouvées: {len(lists)}")
        
        for l_idx, lst in enumerate(lists[:2]):
            items = lst.find_all("li")
            log.info(f"   Liste {l_idx}: {len(items)} items")
            
            for item in items[:3]:
                item_text = item.get_text(strip=True)[:50]
                log.info(f"     - {item_text}")
        
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("3️⃣ ATTRIBUTS data-*")
        log.info("=" * 80)
        
        all_elem = soup.find_all(True)
        data_attrs = {}
        
        for elem in all_elem:
            for attr in elem.attrs:
                if attr.startswith("data-"):
                    if attr not in data_attrs:
                        data_attrs[attr] = []
                    val = elem.get(attr)
                    if val:
                        data_attrs[attr].append(str(val)[:40])
        
        for attr, values in sorted(data_attrs.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            log.info(f"   {attr}: {len(values)} éléments")
            log.info(f"     Exemples: {list(set(values[:2]))}")
        
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("4️⃣ BOUTONS / LIENS")
        log.info("=" * 80)
        
        buttons = soup.find_all(["button", "a"])
        button_texts = [b.get_text(strip=True)[:40] for b in buttons if b.get_text(strip=True)]
        log.info(f"Boutons/Liens: {len(buttons)}")
        log.info(f"Textes uniques: {len(set(button_texts))}")
        
        for text in list(set(button_texts))[:10]:
            if text:
                log.info(f"   - {text}")
        
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("5️⃣ SÉLECTEURS IMPORTANTS")
        log.info("=" * 80)
        
        # Chercher les selects
        selects = soup.find_all("select")
        log.info(f"Selects trouvés: {len(selects)}")
        
        for sel in selects[:3]:
            sel_id = sel.get("id", "N/A")
            sel_name = sel.get("name", "N/A")
            options = sel.find_all("option")
            log.info(f"   #{sel_id} (name={sel_name}): {len(options)} options")
        
        # Chercher les inputs
        inputs = soup.find_all("input", {"type": "text"})
        log.info(f"\nInputs text: {len(inputs)}")
        
        for inp in inputs[:3]:
            inp_id = inp.get("id", "N/A")
            inp_placeholder = inp.get("placeholder", "N/A")
            log.info(f"   #{inp_id} (placeholder={inp_placeholder})")
        
        log.info("\n" + "=" * 80)
        log.info("✅ ANALYSE TERMINÉE")
        log.info("Fichier complet: rayons_catalogue.html")
        log.info("=" * 80)
        
    except Exception as e:
        log.error(f"ERROR → {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await browser.close()
        await playwright.stop()


if __name__ == "__main__":
    asyncio.run(analyze_rayons_page())
