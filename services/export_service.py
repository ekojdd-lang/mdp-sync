import pandas as pd
import os
import logging
from pathlib import Path
from datetime import datetime

log = logging.getLogger("export_service")


class ExportService:
    """Service d'export Excel avec validation"""

    @staticmethod
    def export_articles_to_excel(
        articles: list[dict],
        path: str = None
    ) -> str:
        """
        Export articles to Excel
        ✅ Default path with timestamp
        ✅ Validation
        ✅ Error handling
        ✅ Formatting
        """

        if not articles:
            raise ValueError("Aucun article à exporter")

        # ✅ Default path with timestamp
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"exports/articles_{timestamp}.xlsx"

        # ✅ Create directory
        export_dir = os.path.dirname(path) or "exports"

        try:
            Path(export_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise Exception(f"Erreur création dossier: {str(e)}")

        # ✅ Prepare data
        rows = []

        for idx, article in enumerate(articles):

            if not article or not isinstance(article, dict):
                log.warning(f"Article {idx} invalide")
                continue

            try:
                # ✅ Format auteurs
                auteurs = article.get('auteurs', '')
                if isinstance(auteurs, list):
                    auteurs = ", ".join(str(a).strip() for a in auteurs if a)
                else:
                    auteurs = str(auteurs).strip()

                # ✅ Format prix
                try:
                    prix = float(article.get('prix', 0))
                except (ValueError, TypeError):
                    prix = 0.0

                # ✅ Format stock
                try:
                    stock = int(article.get('stock', 0))
                except (ValueError, TypeError):
                    stock = 0

                # ✅ Build row
                row = {
                    "Gencod": str(article.get("gencod", "")).strip(),
                    "Titre": str(article.get("titre", "")).strip(),
                    "Auteurs": auteurs,
                    "Éditeur": str(article.get("editeur", "")).strip(),
                    "Type": str(article.get("type_produit", "")).strip(),
                    "Prix (FCFA)": prix,
                    "Stock": stock,
                    "Date Sync": str(article.get("date_sync", "")).strip(),
                }

                rows.append(row)

            except Exception as e:
                log.warning(f"Erreur article {idx}: {str(e)}")
                continue

        if not rows:
            raise Exception("Aucun article valide à exporter")

        # ✅ Create DataFrame
        try:
            df = pd.DataFrame(rows)
        except Exception as e:
            raise Exception(f"Erreur création DataFrame: {str(e)}")

        # ✅ Export to Excel
        try:
            df.to_excel(
                path,
                index=False,
                engine="openpyxl",
                sheet_name="Articles"
            )

            # ✅ Auto-format Excel
            try:
                from openpyxl import load_workbook
                wb = load_workbook(path)
                ws = wb.active

                # Adjust column widths
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter

                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

                wb.save(path)

            except Exception as e:
                log.warning(f"Formatting error: {e}")

            log.info(f"✅ Export: {len(rows)} articles → {path}")

            return path

        except Exception as e:
            raise Exception(f"Erreur export Excel: {str(e)}")