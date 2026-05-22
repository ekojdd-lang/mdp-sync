import asyncio

from PySide6.QtCore import (
    QThread,
    Signal
)

from api.mdp_api import MaisonPresseAPI

from backend.core.database import DatabaseManager

from services.sync_service import SyncService
from services.export_service import ExportService
from services.import_service import ImportService


class SyncWorker(QThread):

    log_signal = Signal(str)

    progress_signal = Signal(int)

    finished_signal = Signal()

    # ==================================================
    # INIT
    # ==================================================
    def __init__(self, file_path):

        super().__init__()

        self.file_path = file_path

    # ==================================================
    # LOG
    # ==================================================
    def log(self, message):

        self.log_signal.emit(message)

    # ==================================================
    # RUN
    # ==================================================
    def run(self):

        asyncio.run(self.run_async())

    # ==================================================
    # ASYNC RUN
    # ==================================================
    async def run_async(self):

        api = MaisonPresseAPI()

        db = DatabaseManager()

        sync_service = SyncService(api, db)

        try:

            # ==========================================
            # INIT API
            # ==========================================
            self.log("Initialisation Playwright...")

            await api.init()

            # ==========================================
            # LOAD EXCEL
            # ==========================================
            self.log("Chargement Excel...")

            codes = (
                ImportService
                .load_codes_from_excel(
                    self.file_path
                )
            )

            self.log(
                f"{len(codes)} code(s) chargé(s)"
            )

            if len(codes) == 0:

                self.log(
                    "Aucun code trouvé dans le fichier"
                )

                return

            # ==========================================
            # SYNC
            # ==========================================
            self.log(
                "Synchronisation en cours..."
            )

            total = len(codes)

            for index, code in enumerate(codes):

                try:

                    self.log(
                        f"SYNC ARTICLE : {code}"
                    )

                    result = await sync_service.sync_article(
                        code,
                        force=True
                    )

                    if result:

                        self.log(
                            f"ARTICLE SYNCHRONISÉ : {code}"
                        )

                    else:

                        self.log(
                            f"ÉCHEC : {code}"
                        )

                except Exception as e:

                    self.log(
                        f"ERREUR ARTICLE {code} : {str(e)}"
                    )

                # ======================================
                # PROGRESS
                # ======================================
                progress = int(
                    ((index + 1) / total) * 100
                )

                self.progress_signal.emit(
                    progress
                )

            # ==========================================
            # EXPORT
            # ==========================================
            articles = db.get_all_articles()

            export_path = (
                ExportService
                .export_articles_to_excel(
                    articles
                )
            )

            self.log(
                "Synchronisation terminée"
            )

            self.log(
                f"Export : {export_path}"
            )

        except Exception as e:

            self.log(
                f"ERREUR : {str(e)}"
            )

        finally:

            try:
                await api.close()
            except Exception:
                pass

            db.close()

            self.finished_signal.emit()