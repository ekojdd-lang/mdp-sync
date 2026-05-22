import pandas as pd
import os


class ExportService:

    @staticmethod
    def export_articles_to_excel(
        articles,
        path="exports/articles.xlsx"
    ):

        os.makedirs("exports", exist_ok=True)

        rows = []

        for article in articles:

            rows.append({
                "Gencod": article["gencod"],
                "Titre": article["titre"],
                "Auteurs": article["auteurs"],
                "Editeur": article["editeur"],
                "Prix": article["prix"],
                "Disponibilité": article["disponibilite"]
            })

        df = pd.DataFrame(rows)

        df.to_excel(
            path,
            index=False
        )

        return path