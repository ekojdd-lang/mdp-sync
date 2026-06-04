import pandas as pd
import logging

log = logging.getLogger("import_service")


class ImportService:
    """Service d'import Excel avec validation"""

    @staticmethod
    def load_codes_from_excel(path: str) -> list[str]:
        """
        Load gencods from Excel file
        ✅ Validation
        ✅ Error handling
        ✅ Clean codes
        """

        if not path or not path.endswith(('.xlsx', '.xls')):
            raise ValueError("Fichier doit être .xlsx ou .xls")

        try:
            # ✅ Load with error handling
            df = pd.read_excel(path, engine="openpyxl")

        except FileNotFoundError:
            raise Exception(f"Fichier non trouvé: {path}")

        except Exception as e:
            raise Exception(f"Erreur lecture Excel: {str(e)}")

        if df.empty:
            raise Exception("Fichier Excel vide")

        # ✅ Clean column names
        df.columns = [
            str(col).strip().lower()
            for col in df.columns
        ]

        # ✅ Check required column
        if "gencod" not in df.columns:
            available = ", ".join(df.columns.tolist())
            raise Exception(
                f"Colonne 'gencod' introuvable.\n"
                f"Colonnes disponibles: {available}"
            )

        codes: list[str] = []

        # ✅ Process codes
        for idx, value in enumerate(df["gencod"]):

            try:
                # Skip NaN/None
                if pd.isna(value) or value is None:
                    continue

                # Convert to string
                code = str(value).strip()

                if not code or code == "nan" or code == "None":
                    continue

                # ✅ Clean Excel float format (12345.0 → 12345)
                if code.endswith(".0") and code[:-2].isdigit():
                    code = code[:-2]

                # ✅ Basic validation
                if len(code) < 5:
                    log.warning(f"Code trop court (ligne {idx+2}): {code}")
                    continue

                if code in codes:
                    log.warning(f"Doublon (ligne {idx+2}): {code}")
                    continue

                codes.append(code)

            except Exception as e:
                log.warning(f"Erreur traitement ligne {idx+2}: {str(e)}")
                continue

        if not codes:
            raise Exception("Aucun code valide trouvé dans le fichier")

        log.info(f"✅ {len(codes)} codes chargés avec succès")

        return codes