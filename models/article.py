from datetime import datetime


class Article:

    def __init__(self, article):

        self.date_sync = datetime.now()

        # =====================================================
        # IDENTIFIANTS
        # =====================================================

        self.gencod = (
            article.get("gencod")
            or article.get("ean")
            or article.get("isbn")
            or ""
        )

        self.isbn = (
            article.get("isbn")
            or self.gencod
        )

        # =====================================================
        # INFOS PRINCIPALES
        # =====================================================

        self.titre = (
            article.get("titre")
            or ""
        )

        self.editeur = (
            article.get("editeur")
            or ""
        )

        self.presentation = (
            article.get("presentation")
            or ""
        )

        self.image_url = (
            article.get("imageUrl")
            or article.get("image_url")
            or ""
        )

        # =====================================================
        # PRIX
        # =====================================================

        prix = article.get("prix", 0)

        try:

            self.prix = round(
                float(prix),
                2
            )

        except Exception:

            self.prix = 0

        # =====================================================
        # DISPONIBILITÉ
        # =====================================================

        self.disponibilite = str(
            article.get(
                "disponibilite",
                "0"
            )
        )

        # =====================================================
        # STOCK
        # =====================================================

        try:

            self.stock = int(
                article.get(
                    "stock",
                    0
                )
            )

        except Exception:

            self.stock = 0

        # =====================================================
        # AUTEURS
        # =====================================================

        self.auteurs = []

        auteurs = (
            article.get("auteurs")
            or []
        )

        for auteur in auteurs:

            if isinstance(auteur, dict):

                nom = (
                    auteur.get("nom")
                    or auteur.get("name")
                )

                if nom:

                    self.auteurs.append(
                        nom.strip()
                    )

            elif isinstance(auteur, str):

                self.auteurs.append(
                    auteur.strip()
                )

        # =====================================================
        # MÉTADONNÉES LIVRE
        # =====================================================

        self.categorie = (
            article.get("categorie")
            or article.get("rayon")
            or article.get("genre")
            or ""
        )

        self.langue = (
            article.get("langue")
            or "Français"
        )

        # =====================================================
        # NOMBRE DE PAGES
        # =====================================================

        try:

            self.nombre_pages = int(
                article.get(
                    "nombre_pages",
                    article.get(
                        "pages",
                        0
                    )
                )
            )

        except Exception:

            self.nombre_pages = 0

        # =====================================================
        # DATE PARUTION
        # =====================================================

        self.date_parution = (
            article.get("date_parution")
            or article.get("dateParution")
            or article.get("publication_date")
            or ""
        )

    # =========================================================
    # SERIALIZATION
    # =========================================================

    def to_dict(self):

        return {

            "gencod":
            self.gencod,

            "isbn":
            self.isbn,

            "titre":
            self.titre,

            "auteurs":
            self.auteurs,

            "editeur":
            self.editeur,

            "prix":
            self.prix,

            "disponibilite":
            self.disponibilite,

            "image_url":
            self.image_url,

            "presentation":
            self.presentation,

            "categorie":
            self.categorie,

            "langue":
            self.langue,

            "nombre_pages":
            self.nombre_pages,

            "date_parution":
            self.date_parution,

            "stock":
            self.stock,

            "date_sync":
            self.date_sync.isoformat()
        }

    # =========================================================
    # DEBUG
    # =========================================================

    def __repr__(self):

        return (
            f"<Article "
            f"{self.gencod} | "
            f"{self.titre}>"
        )