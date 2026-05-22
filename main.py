import asyncio

from backend.auth import AuthManager

from api.mdp_api import MaisonPresseAPI

from backend.core.database import DatabaseManager

from services.sync_service import SyncService

from services.import_service import ImportService

from services.export_service import ExportService

from backend.core.playwright_manager import PlaywrightManager


async def main():

    # ======================================================
    # INIT AUTH SESSION
    # ======================================================

    auth = AuthManager()

    await auth.init_session()

    print("APP READY")

    # ======================================================
    # LOAD CODES
    # ======================================================

    codes = ImportService.load_codes_from_excel(
        "imports/codes.xlsx"
    )

    # ======================================================
    # SERVICES
    # ======================================================

    api = MaisonPresseAPI()

    await api.init()

    db = DatabaseManager()

    sync_service = SyncService(api, db)

    # ======================================================
    # SYNC
    # ======================================================

    try:

        await sync_service.sync_many(
            codes,
            force=True
        )

        articles = db.get_all_articles()

        file_path = ExportService.export_articles_to_excel(
            articles
        )

        print(f"\nEXPORT EXCEL : {file_path}")

    finally:

        try:

            await api.close()

        except Exception as e:

            print("api close error:", e)

        try:

            await auth.close()

        except Exception as e:

            print("auth close error:", e)

        try:

            await PlaywrightManager.close()

        except Exception as e:

            print("playwright close error:", e)

        try:

            db.close()

        except Exception as e:

            print("db close error:", e)

        # IMPORTANT WINDOWS + PLAYWRIGHT
        await asyncio.sleep(2)


if __name__ == "__main__":

    asyncio.run(main())