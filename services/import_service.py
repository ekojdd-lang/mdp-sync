import pandas as pd


class ImportService:

    @staticmethod
    def load_codes_from_excel(path):

        df = pd.read_excel(
            path,
            engine="openpyxl"
        )

        # nettoyage noms colonnes
        df.columns = [
            str(col).strip().lower()
            for col in df.columns
        ]

        if "gencod" not in df.columns:

            raise Exception(
                "COLONNE 'gencod' INTROUVABLE"
            )

        codes = []

        for value in df["gencod"]:

            if pd.notna(value):

                code = str(value).strip()

                codes.append(code)

        return codes