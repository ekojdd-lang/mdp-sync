import asyncio
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QThread, Signal

from api.mdp_api import MaisonPresseAPI
from backend.core.database import DatabaseManager
from backend.core.logger import logger

from services.sync_service import SyncService
from services.export_service import ExportService
from services.import_service import ImportService


class SyncWorker(QThread):
    """Worker thread pour synchronisation asynchrone"""

    log_signal = Signal(str)
    progress_signal = Signal(int, int, int)  # progress, success, failed
    finished_signal = Signal(dict)  # result stats

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self._running = True
        self._result = {}

    def log(self, message: str):
        """Emit log message"""
        self.log_signal.emit(message)

    def stop(self):
        """Stop worker safely"""
        self._running = False

    def run(self):
        """QThread run (wrapper)"""
        try:
            # ✅ Utiliser un event loop séparé pour éviter les deadlocks
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_async())
        except Exception as e:
            logger.error(f"Fatal error in worker: {e}")
            self.log(f"❌ ERREUR FATALE: {str(e)}")
        finally:
            try:
                loop.close()
            except:
                pass
            self.finished_signal.emit(self._result)

    async def run_async(self):
        """Async core logic"""

        api = MaisonPresseAPI()
        db = DatabaseManager()
        sync_service = SyncService(api, db)

        try:
            # ✅ INIT
            self.log("🔄 Initialisation Playwright...")
            await api.init()
            self.log("✅ Playwright initié")

            # ✅ IMPORT EXCEL
            self.log("📂 Chargement Excel...")

            try:
                codes = ImportService.load_codes_from_excel(self.file_path)
            except Exception as e:
                self.log(f"❌ Erreur lecture Excel: {str(e)}")
                self._result = {"success": 0, "failed": 0}
                return

            if not codes:
                self.log("⚠️  Aucun code trouvé dans le fichier")
                self._result = {"success": 0, "failed": 0}
                return

            total = len(codes)
            self.log(f"✅ {total} code(s) chargé(s)")

            # ✅ SYNC LOOP avec callback
            self.log("🔄 Synchronisation en cours...")

            def progress_callback(progress, success, failed):
                self.progress_signal.emit(progress, success, failed)

            stats = await sync_service.sync_many(
                codes,
                force=True,
                progress_callback=progress_callback
            )

            self._result = stats

            # ✅ EXPORT FINAL
            self.log("📊 Export des données...")

            articles = db.get_all_articles()

            if not articles:
                self.log("⚠️  Aucun article à exporter")
            else:
                export_path = ExportService.export_articles_to_excel(articles)
                self.log(f"✅ Export : {export_path}")

            self.log("✅ Synchronisation terminée")
            self.log(
                f"📈 Résultat: {stats['success']} ✅ | {stats['failed']} ❌ | {stats['total']} total"
            )

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            self.log(f"❌ ERREUR FATALE: {str(e)}")
            self._result = {"success": 0, "failed": 0, "error": str(e)}

        finally:
            # ✅ CLEANUP PROPRE
            try:
                await api.close()
            except Exception as e:
                logger.error(f"Error closing API: {e}")

            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing DB: {e}")