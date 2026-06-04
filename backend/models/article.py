from datetime import datetime
import json


class Article:

    def __init__(self, article):

        print("\n===== ARTICLE RECU =====")
        print(
            json.dumps(
                article,
                indent=2,
                ensure_ascii=False
            )
        )

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

        self.isbn = article.get("isbn") or ""
        self.ean = article.get("ean") or ""

        self.code_article = (
            self.isbn
            or self.ean
            or self.gencod
        )

        # =====================================================
        # TYPE PRODUIT
        # =====================================================

        type_produit = (
            article.get("typeProduit")
            or article.get("type_produit")
        )

        self.type_produit_code = str(type_produit) if type_produit else ""

        if self.type_produit_code == "5":
            self.type_produit = "jouet"

        elif self.type_produit_code == "6":
            self.type_produit = "papeterie"

        elif self.isbn:
            self.type_produit = "livre"

        elif self.ean:
            self.type_produit = "papeterie"

        else:
            self.type_produit = "inconnu"

        # =====================================================
        # INFOS PAPETERIE / JOUETS
        # =====================================================

        self.rayon = article.get("rayon") or article.get("categorie") or ""
        self.ref_fournisseur = article.get("ref_fournisseur") or article.get("refFournisseur") or ""
        self.distributeur = article.get("distributeur") or ""
        self.pays_origine = article.get("pays_origine") or article.get("paysOrigine") or ""

        # =====================================================
        # METADONNEES EPAGINE
        # =====================================================

        self.code_support = article.get("codeSupport") or ""
        self.code_rayon = article.get("codeRayon") or ""
        self.collection = article.get("collection") or ""
        self.collection_numero = article.get("collectionNumero") or ""
        self.langue_iso = article.get("langueIso") or ""
        self.lectorat = article.get("lectoratLibelle") or ""
        self.fournisseur_nom = article.get("fournisseurNom") or ""
        self.fournisseur_reference = article.get("fournisseurReference") or ""

        # =====================================================
        # INFOS PRINCIPALES
        # =====================================================

        self.titre = article.get("titre") or ""
        self.editeur = article.get("editeur") or ""
        self.presentation = article.get("presentation") or ""

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
            self.prix = round(float(prix), 2)
        except Exception:
            self.prix = 0.0

        # =====================================================
        # DISPONIBILITE
        # =====================================================

        self.disponibilite = str(article.get("disponibilite", "0"))

        # =====================================================
        # STOCK (souvent absent API MDP)
        # =====================================================

        try:
            self.stock = int(article.get("stock", 0))
        except Exception:
            self.stock = 0

        # =====================================================
        # DIMENSIONS
        # =====================================================

        def to_float(value):
            try:
                return float(
                    str(value)
                    .replace("cm", "")
                    .replace("g", "")
                    .replace(",", ".")
                    .strip()
                )
            except Exception:
                return 0.0

        self.longueur = to_float(article.get("longueur"))
        self.largeur = to_float(article.get("largeur"))
        self.epaisseur = to_float(article.get("epaisseur"))
        self.poids = to_float(article.get("poids"))

        # =====================================================
        # AUTEURS (ROBUSTE)
        # =====================================================

        self.auteurs = []

        auteurs = article.get("auteurs")

        if isinstance(auteurs, str):
            auteurs = auteurs.replace(";", ",")
            self.auteurs = [
                a.strip()
                for a in auteurs.split(",")
                if a.strip()
            ]

        elif isinstance(auteurs, list):
            for a in auteurs:
                if isinstance(a, dict):
                    nom = a.get("nom") or a.get("name")
                    if nom:
                        self.auteurs.append(nom.strip())
                elif isinstance(a, str):
                    self.auteurs.append(a.strip())

        # =====================================================
        # METADONNEES LIVRE
        # =====================================================

        self.categorie = (
            article.get("categorie")
            or article.get("rayon")
            or article.get("genre")
            or ""
        )

        self.langue = article.get("langue") or "Français"

        # =====================================================
        # NOMBRE DE PAGES
        # =====================================================

        try:
            self.nombre_pages = int(
                article.get("pages")
                or article.get("nombre_pages")
                or 0
            )
        except Exception:
            self.nombre_pages = 0

        # =====================================================
        # DATE PARUTION (FIX IMPORTANT)
        # =====================================================

        date_parution = (
            article.get("dateParution")
            or article.get("date_parution")
            or article.get("publication_date")
        )

        self.date_parution = ""

        if date_parution:

            # timestamp
            try:
                ts = int(date_parution)
                self.date_parution = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
            except Exception:
                # ISO string fallback
                try:
                    self.date_parution = str(date_parution)
                except Exception:
                    self.date_parution = ""

    # =========================================================
    # SERIALIZATION
    # =========================================================

    def to_dict(self):
        """Retourne exactement 35 clés pour correspondre à la BD."""
        return {
            "gencod": self.gencod,
            "isbn": self.isbn,
            "ean": self.ean,
            "code_article": self.code_article,
            "type_produit": self.type_produit,
            "type_produit_code": self.type_produit_code,
            "titre": self.titre,
            "auteurs": self.auteurs,
            "editeur": self.editeur,
            "prix": self.prix,
            "disponibilite": self.disponibilite,
            "image_url": self.image_url,
            "presentation": self.presentation,
            "categorie": self.categorie,
            "rayon": self.rayon,
            "langue": self.langue,
            "nombre_pages": self.nombre_pages,
            "date_parution": self.date_parution,
            "stock": self.stock,
            "ref_fournisseur": self.ref_fournisseur,
            "distributeur": self.distributeur,
            "pays_origine": self.pays_origine,
            "longueur": self.longueur,
            "largeur": self.largeur,
            "epaisseur": self.epaisseur,
            "poids": self.poids,
            "code_support": self.code_support,
            "code_rayon": self.code_rayon,
            "collection": self.collection,
            "collection_numero": self.collection_numero,
            "langue_iso": self.langue_iso,
            "lectorat": self.lectorat,
            "fournisseur_nom": self.fournisseur_nom,
            "fournisseur_reference": self.fournisseur_reference,
            "date_sync": self.date_sync.isoformat()
        }
    # =========================================================
    # DEBUG
    # =========================================================

    def __repr__(self):

        return (
            f"<Article "
            f"{self.type_produit} | "
            f"{self.code_article} | "
            f"{self.titre}>"
        )
