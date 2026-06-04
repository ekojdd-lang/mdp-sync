"""
Module pour charger et gérer les données du fichier Excel de pricing
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Set, Dict, Optional, List
from dataclasses import dataclass

log = logging.getLogger("excel-loader")


@dataclass
class Article:
    """Représentation d'un article chargé depuis Excel"""
    gencod: str
    titre: str = ""
    auteurs: str = ""
    editeur: str = ""
    prix: float = 0.0
    type_produit: str = ""
    disponibilite: str = "1"
    image_url: str = ""
    presentation: str = ""
    categorie: str = ""
    rayon: str = ""
    langue: str = ""
    nombre_pages: int = 0
    date_parution: str = ""
    stock: int = 0
    isbn: str = ""
    ean: str = ""
    code_article: str = ""
    ref_fournisseur: str = ""
    distributeur: str = ""
    pays_origine: str = ""
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            "gencod": self.gencod,
            "titre": self.titre,
            "auteurs": self.auteurs,
            "editeur": self.editeur,
            "prix": self.prix,
            "type_produit": self.type_produit,
            "type_produit_code": self.type_produit,
            "disponibilite": self.disponibilite,
            "image_url": self.image_url,
            "presentation": self.presentation,
            "categorie": self.categorie,
            "rayon": self.rayon,
            "langue": self.langue,
            "nombre_pages": self.nombre_pages,
            "date_parution": self.date_parution,
            "stock": self.stock,
            "isbn": self.isbn,
            "ean": self.ean,
            "code_article": self.code_article,
            "ref_fournisseur": self.ref_fournisseur,
            "distributeur": self.distributeur,
            "pays_origine": self.pays_origine,
        }


class ExcelPricingLoader:
    """
    Charge le fichier Excel contenant les gencods, prix et types de produits.
    Fournit les données pour les articles de type_produit 6.
    """
    
    def __init__(self, excel_path: str = None):
        """
        Args:
            excel_path: Chemin vers le fichier Excel (par défaut: backend/data/pricing.xlsx)
        """
        if excel_path is None:
            excel_path = Path(__file__).parent.parent / "data" / "pricing.xlsx"
        
        self.excel_path = Path(excel_path)
        self.df = None
        self.articles_type6: Dict[str, Article] = {}
        self.all_articles: Dict[str, Article] = {}
        
        if self.excel_path.exists():
            self._load_excel()
        else:
            log.warning(f"❌ Fichier Excel introuvable: {self.excel_path}")
            
    def get_all_gencods_by_type(
        self,
        type_produit: str
    ) -> Set[str]:

        return {
            article.gencod
            for article in self.all_articles.values()
            if str(article.type_produit).strip() == str(type_produit)
        }
        
    
    def _load_excel(self):
        """Charge et parse le fichier Excel"""
        try:
            log.info(f"📂 Chargement du fichier Excel: {self.excel_path}")
            
            # Charger le fichier
            self.df = pd.read_excel(
                self.excel_path,
                dtype=str,
                engine="openpyxl"
            )
            
            log.info(f"✅ Fichier chargé: {len(self.df)} lignes")
            log.info(f"Colonnes trouvées: {list(self.df.columns)}")
            
            # Normaliser les noms de colonnes
            self.df.columns = self.df.columns.str.strip().str.lower()
            
            # Parser les données
            self._parse_articles()
            
        except Exception as e:
            log.error(f"❌ Erreur lors du chargement: {e}")
            raise
    
    def _find_column(self, possible_names: list) -> Optional[str]:
        """Cherche une colonne parmi les noms possibles"""
        if self.df is None:
            return None
        
        for col in self.df.columns:
            col_lower = col.lower().strip()
            for name in possible_names:
                if col_lower == name.lower().strip():
                    return col
        
        return None
    
    
    def _parse_articles(self):
        """Parse tous les articles du fichier Excel"""

        # =========================
        # Vérification sécurité
        # =========================
        if self.df is None or self.df.empty:
            log.warning("⚠️ DataFrame vide, aucun traitement possible")
            return

        # =========================
        # Chercher les colonnes
        # =========================
        gencod_col = self._find_column(['gencod', 'code gencod', 'gencod code'])

        prix_col = self._find_column(['prix', 'price', 'prix_aplique', 'prix appliqué', 'prix_apliquée'])

        type_col = self._find_column(['type_produit', 'type produit', 'typeproduit', 'product_type'])

        titre_col = self._find_column(['titre', 'title', 'nom', 'name'])

        auteur_col = self._find_column(['auteurs', 'auteur', 'author', 'authors'])

        editeur_col = self._find_column(['editeur', 'publisher', 'éditeur'])

        isbn_col = self._find_column(['isbn'])

        ean_col = self._find_column(['ean', 'code ean'])

        # =========================
        # Vérification critique
        # =========================
        if not gencod_col:
            log.error("❌ Colonne 'gencod' introuvable dans le fichier Excel")
            return

        log.info("📋 Colonnes utilisées:")
        log.info(f"  - Gencod: {gencod_col}")
        log.info(f"  - Prix: {prix_col}")
        log.info(f"  - Type produit: {type_col}")

        # =========================
        # Initialisation compteurs
        # =========================
        duplicate_count = 0
        skipped_count = 0

        columns = list(self.df.columns)

        # =========================
        # Parsing lignes Excel
        # =========================
        for row in self.df.itertuples(index=False):

            row_dict = dict(zip(columns, row))

            raw_gencod = row_dict.get(gencod_col)

            if pd.isna(raw_gencod):
                skipped_count += 1
                continue

            gencod = str(raw_gencod).replace(".0", "").strip()

            if not gencod or gencod.lower() == "nan":
                skipped_count += 1
                continue

            if gencod in self.all_articles:
                duplicate_count += 1
                continue

            # =========================
            # Prix
            # =========================
            prix = 0.0
            if prix_col:
                raw_prix = row_dict.get(prix_col)
                if pd.notna(raw_prix):
                    try:
                        prix = float(raw_prix)
                    except (ValueError, TypeError):
                        prix = 0.0

            # =========================
            # Type produit
            # =========================
            type_produit = ""
            if type_col:
                value = row_dict.get(type_col)
                if pd.notna(value):
                    type_produit = str(value).replace(".0", "").strip()

            # =========================
            # Titre
            # =========================
            titre = ""
            if titre_col:
                value = row_dict.get(titre_col)
                if pd.notna(value):
                    titre = str(value).strip()

            # =========================
            # Auteur
            # =========================
            auteur = ""
            if auteur_col:
                value = row_dict.get(auteur_col)
                if pd.notna(value):
                    auteur = str(value).strip()

            # =========================
            # Editeur
            # =========================
            editeur = ""
            if editeur_col:
                value = row_dict.get(editeur_col)
                if pd.notna(value):
                    editeur = str(value).strip()

            # =========================
            # ISBN
            # =========================
            isbn = ""
            if isbn_col:
                value = row_dict.get(isbn_col)
                if pd.notna(value):
                    isbn = str(value).replace(".0", "").strip()

            # =========================
            # EAN
            # =========================
            ean = ""
            if ean_col:
                value = row_dict.get(ean_col)
                if pd.notna(value):
                    ean = str(value).replace(".0", "").strip()

            # =========================
            # Création article
            # =========================
            article = Article(
                gencod=gencod,
                titre=titre,
                auteurs=auteur,
                editeur=editeur,
                prix=prix,
                type_produit=type_produit,
                isbn=isbn,
                ean=ean,
                disponibilite="1",
                stock=0
            )

            self.all_articles[gencod] = article

            if type_produit == "6":
                self.articles_type6[gencod] = article

        # =========================
        # LOG FINAL
        # =========================
        log.info("✅ Parsing terminé:")
        log.info(f"  - Total articles: {len(self.all_articles)}")
        log.info(f"  - Articles type_produit=6: {len(self.articles_type6)}")
        log.info(f"  - Doublons ignorés: {duplicate_count}")
        log.info(f"  - Lignes ignorées: {skipped_count}")

        duplicate_count = 0
        skipped_count = 0

        columns = list(self.df.columns)

        for row in self.df.itertuples(index=False):

            row_dict = dict(zip(columns, row))

            raw_gencod = row_dict.get(gencod_col)

            if pd.isna(raw_gencod):
                skipped_count += 1
                continue

            gencod = str(raw_gencod).replace(".0", "").strip()

            if not gencod or gencod.lower() == "nan":
                skipped_count += 1
                continue

            if gencod in self.all_articles:
                duplicate_count += 1
                continue

        # ==========================
        # Prix
        # ==========================
            prix = 0.0

            if prix_col:
                raw_prix = row_dict.get(prix_col)

                if pd.notna(raw_prix):
                    try:
                        prix = float(raw_prix)
                    except (ValueError, TypeError):
                        prix = 0.0

        # ==========================
        # Type produit
        # ==========================
            type_produit = ""

            if type_col:
                value = row_dict.get(type_col)

                if pd.notna(value):
                    type_produit = str(value).replace(".0", "").strip()

        # ==========================
        # Titre
        # ==========================
            titre = ""

            if titre_col:
                value = row_dict.get(titre_col)

                if pd.notna(value):
                    titre = str(value).strip()

        # ==========================
        # Auteur
        # ==========================
            auteur = ""

            if auteur_col:
                value = row_dict.get(auteur_col)

                if pd.notna(value):
                    auteur = str(value).strip()

        # ==========================
        # Editeur
        # ==========================
            editeur = ""

            if editeur_col:
                value = row_dict.get(editeur_col)

                if pd.notna(value):
                    editeur = str(value).strip()

        # ==========================
        # ISBN
        # ==========================
            isbn = ""

            if isbn_col:
                value = row_dict.get(isbn_col)

                if pd.notna(value):
                    isbn = str(value).replace(".0", "").strip()

        # ==========================
        # EAN
        # ==========================
            ean = ""

            if ean_col:
                value = row_dict.get(ean_col)

                if pd.notna(value):
                    ean = str(value).replace(".0", "").strip()

            article = Article(
                gencod=gencod,
                titre=titre,
                auteurs=auteur,
                editeur=editeur,
                prix=prix,
                type_produit=type_produit,
                isbn=isbn,
                ean=ean,
                disponibilite="1",
                stock=0
            )

            self.all_articles[gencod] = article

            if type_produit == "6":
                self.articles_type6[gencod] = article

        log.info("✅ Parsing terminé:")
        log.info(f"  - Total articles: {len(self.all_articles)}")
        log.info(f"  - Articles type_produit=6: {len(self.articles_type6)}")
        log.info(f"  - Doublons ignorés: {duplicate_count}")
        log.info(f"  - Lignes ignorées: {skipped_count}")
        
    def get_all_type6_articles(self) -> List[Article]:
        """Retourne tous les articles de type_produit 6"""
        return list(self.articles_type6.values())
    
    def get_all_gencods_type6(self) -> Set[str]:
        """Retourne l'ensemble des gencods de type_produit 6"""
        return set(self.articles_type6.keys())
    
    def get_article_type6(self, gencod: str) -> Optional[Article]:
        """Récupère un article de type_produit 6 par gencod"""
        return self.articles_type6.get(str(gencod).strip())
    
    def get_stats(self) -> dict:
        """Retourne des statistiques sur les données chargées"""
        if self.df is None:
            return {"status": "no_file", "message": "Aucun fichier Excel chargé"}
        
        type_counts = {}
        for article in self.all_articles.values():
            type_prod = article.type_produit or "unknown"
            type_counts[str(type_prod)] = type_counts.get(str(type_prod), 0) + 1
        
        return {
            "status": "loaded",
            "total_articles": len(self.all_articles),
            "articles_type6": len(self.articles_type6),
            "type_product_distribution": type_counts,
            "fichier": str(self.excel_path)
        }
    
    def get_all_articles(self) -> List[Article]:
        """Retourne tous les articles du fichier Excel"""
        return list(self.all_articles.values())
    
