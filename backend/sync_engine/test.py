#!/usr/bin/env python3
"""
Script de test pour valider la structure de l'API d'administration
"""
import asyncio
import json
import logging
from playwright.async_api import async_playwright

BASE = "https://www.maisondelapressegabon.com/gestion"
API_ENDPOINT = f"{BASE}/api/articles.php"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("api-test")


async def test_api():
    """Teste les appels API."""
    
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
        # =====================================
        # 1. LOGIN MANUEL
        # =====================================
        log.info("=" * 80)
        log.info("ÉTAPE 1 : LOGIN")
        log.info("=" * 80)
        
        await page.goto(f"{BASE}/", wait_until="domcontentloaded")
        
        input(
            "\n👉 Connecte-toi à l'interface d'admin\n"
            "👉 Va dans : Base de données → Création Articles\n"
            "👉 Puis appuie sur ENTER...\n"
        )
        
        # =====================================
        # 2. TEST getGtlList (racine)
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("ÉTAPE 2 : TEST getGtlList (racine)")
        log.info("=" * 80)
        
        for type_produit in [1, 5, 6]:
            log.info(f"\nType produit: {type_produit}")
            
            response = await request.get(
                API_ENDPOINT,
                params={
                    "action": "getGtlList",
                    "gtl": None,
                    "typeProduit": type_produit
                }
            )
            
            if response.status == 200:
                data = await response.json()
                log.info(f"✓ Status 200")
                log.info(f"Response type: {type(data).__name__}")
                log.info(f"Response keys: {list(data.keys())[:5] if isinstance(data, dict) else 'N/A'}")
                log.info(f"Full response:\n{json.dumps(data, indent=2, ensure_ascii=False)[:1000]}")
            else:
                log.error(f"✗ Status {response.status}")
        
        # =====================================
        # 3. TEST getArticle avec un gencod valide
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("ÉTAPE 3 : TEST getArticle")
        log.info("=" * 80)
        
        # Utiliser un gencod existant (ex: 9782253159064)
        test_gencod = "9782253159064"
        
        log.info(f"\nTest gencod: {test_gencod}")
        
        for type_produit in [1]:
            response = await request.get(
                API_ENDPOINT,
                params={
                    "action": "getArticle",
                    "gencod": test_gencod,
                    "typeProduit": type_produit
                }
            )
            
            if response.status == 200:
                data = await response.json()
                log.info(f"✓ Status 200")
                log.info(f"Response type: {type(data).__name__}")
                log.info(f"Response keys: {list(data.keys())}")
                log.info(f"Article structure:\n{json.dumps(data, indent=2, ensure_ascii=False)[:2000]}")
            else:
                log.error(f"✗ Status {response.status}")
        
        # =====================================
        # 4. TEST getCodeSupport
        # =====================================
        log.info("\n" + "=" * 80)
        log.info("ÉTAPE 4 : TEST getCodeSupport")
        log.info("=" * 80)
        
        for type_produit in [1, 5, 6]:
            response = await request.get(
                API_ENDPOINT,
                params={
                    "action": "getCodeSupport",
                    "typeProduit": type_produit
                }
            )
            
            if response.status == 200:
                data = await response.json()
                log.info(f"✓ Type {type_produit}: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
            else:
                log.error(f"✗ Type {type_produit}: Status {response.status}")
        
        log.info("\n" + "=" * 80)
        log.info("✅ TESTS COMPLÉTÉS")
        log.info("=" * 80)
        
    except Exception as e:
        log.error(f"ERROR → {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await browser.close()
        await playwright.stop()


if __name__ == "__main__":
    asyncio.run(test_api())
