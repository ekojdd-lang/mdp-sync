#!/usr/bin/env python3
"""
Script de diagnostic pour voir la structure HTML des résultats
"""
import asyncio
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pathlib import Path

BASE = "https://www.maisondelapressegabon.com/gestion"

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("diagnostic")


async def diagnose():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(ignore_https_errors=True)
    page = await context.new_page()
    
    try:
        await page.goto(f"{BASE}/", wait_until="domcontentloaded")
        
        input("\n👉 Login et va sur Articles. Puis ENTER...\n")
        
        # Effectuer une recherche
        search_input = await page.query_selector("#search-gencod")
        type_select = await page.query_selector("#selectionType")
        
        if search_input and type_select:
            await search_input.fill("roman")
            await type_select.select_option("1")
            await search_input.press("Enter")
            await asyncio.sleep(2)
            
            # Capturer le HTML
            html = await page.content()
            
            # Sauvegarder
            Path("diagnostic_results.html").write_text(html, encoding="utf-8")
            log.info("✓ HTML sauvegardé dans diagnostic_results.html")
            
            # Analyser
            soup = BeautifulSoup(html, "html.parser")
            
            log.info("\n" + "=" * 80)
            log.info("1️⃣ TABLES")
            log.info("=" * 80)
            tables = soup.find_all("table")
            log.info(f"Tables trouvées: {len(tables)}\n")
            
            if tables:
                table = tables[0]
                rows = table.find_all("tr")
                log.info(f"Lignes dans la première table: {len(rows)}\n")
                
                if len(rows) > 1:
                    log.info("📋 PREMIÈRE LIGNE (header):")
                    headers = rows[0].find_all(["th", "td"])
                    for i, h in enumerate(headers[:5]):
                        log.info(f"  Col {i}: {h.get_text(strip=True)[:50]}")
                    
                    log.info("\n📋 DEUXIÈME LIGNE (data):")
                    cells = rows[1].find_all("td")
                    for i, cell in enumerate(cells[:5]):
                        log.info(f"  Col {i}: {cell.get_text(strip=True)[:50]}")
                        if cell.has_attr("data-gencod"):
                            log.info(f"         → data-gencod: {cell.get('data-gencod')}")
                        if cell.has_attr("data-id"):
                            log.info(f"         → data-id: {cell.get('data-id')}")
                    
                    log.info(f"\n📊 TOUTES LES LIGNES DE DONNÉES:")
                    for row_idx, row in enumerate(rows[1:11], 1):  # Premières 10 lignes
                        cells = row.find_all("td")
                        if cells:
                            first_cell = cells[0].get_text(strip=True)[:30]
                            log.info(f"  Row {row_idx}: {first_cell}")
            
            log.info("\n" + "=" * 80)
            log.info("2️⃣ ATTRIBUTS data-*")
            log.info("=" * 80)
            
            all_elem = soup.find_all(True)
            data_attrs = {}
            for elem in all_elem:
                for attr in elem.attrs:
                    if attr.startswith("data-"):
                        if attr not in data_attrs:
                            data_attrs[attr] = 0
                        data_attrs[attr] += 1
            
            for attr, count in sorted(data_attrs.items(), key=lambda x: x[1], reverse=True)[:10]:
                log.info(f"  {attr}: {count}x")
            
            log.info("\n" + "=" * 80)
            log.info("3️⃣ LIENS")
            log.info("=" * 80)
            
            links = soup.find_all("a", href=True)
            article_links = [l for l in links if "gencod" in l.get("href", "").lower() or "article" in l.get("href", "").lower()]
            log.info(f"Liens 'article/gencod': {len(article_links)}")
            
            if article_links:
                for link in article_links[:3]:
                    log.info(f"  href: {link.get('href')[:80]}")
            
            log.info("\n✅ DIAGNOSTIC TERMINÉ - Voir diagnostic_results.html")
        
    except Exception as e:
        log.error(f"ERROR → {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await browser.close()
        await playwright.stop()


if __name__ == "__main__":
    asyncio.run(diagnose())
