from pathlib import Path
import sqlite3
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "mdp.db"


class DatabaseManager:

    def __init__(self):

        os.makedirs(DATA_DIR, exist_ok=True)

        print("DATABASE:", DB_PATH)

        self.connection = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

        self.create_tables()

        self.run_migrations()

    # =====================================================
    # CREATE TABLES
    # =====================================================

    def create_tables(self):

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gencod TEXT UNIQUE,
                isbn TEXT,
                titre TEXT,
                auteurs TEXT,
                editeur TEXT,
                prix REAL,
                disponibilite TEXT,
                image_url TEXT,
                presentation TEXT,
                categorie TEXT,
                langue TEXT,
                nombre_pages INTEGER,
                date_parution TEXT,
                stock INTEGER DEFAULT 0,
                date_sync DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.connection.commit()

    # =====================================================
    # SAFE MIGRATIONS (ANTI-CRASH)
    # =====================================================

    def run_migrations(self):

        self.cursor.execute("PRAGMA table_info(articles)")
        columns = [row["name"] for row in self.cursor.fetchall()]

        migrations = {
            "isbn": "ALTER TABLE articles ADD COLUMN isbn TEXT",
            "categorie": "ALTER TABLE articles ADD COLUMN categorie TEXT",
            "langue": "ALTER TABLE articles ADD COLUMN langue TEXT",
            "nombre_pages": "ALTER TABLE articles ADD COLUMN nombre_pages INTEGER",
            "date_parution": "ALTER TABLE articles ADD COLUMN date_parution TEXT",
            "stock": "ALTER TABLE articles ADD COLUMN stock INTEGER DEFAULT 0",
        }

        for column, query in migrations.items():

            if column in columns:
                continue

            try:
                self.cursor.execute(query)
            except sqlite3.OperationalError:
                # colonne déjà existante ou conflit → on ignore proprement
                pass

        self.connection.commit()

    # =====================================================
    # SAVE ARTICLE
    # =====================================================

    def save_article(self, article):

        auteurs = ""

        if hasattr(article, "auteurs"):

            if isinstance(article.auteurs, list):
                auteurs = ", ".join(article.auteurs)
            else:
                auteurs = str(article.auteurs)

        self.cursor.execute("""
            INSERT OR REPLACE INTO articles (
                gencod,
                isbn,
                titre,
                auteurs,
                editeur,
                prix,
                disponibilite,
                image_url,
                presentation,
                categorie,
                langue,
                nombre_pages,
                date_parution,
                stock
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            getattr(article, "gencod", ""),
            getattr(article, "isbn", getattr(article, "gencod", "")),
            getattr(article, "titre", ""),
            auteurs,
            getattr(article, "editeur", ""),
            getattr(article, "prix", 0),
            getattr(article, "disponibilite", "0"),
            getattr(article, "image_url", ""),
            getattr(article, "presentation", ""),
            getattr(article, "categorie", ""),
            getattr(article, "langue", ""),
            getattr(article, "nombre_pages", 0),
            getattr(article, "date_parution", ""),
            getattr(article, "stock", 0),
        ))

        self.connection.commit()

    # =====================================================
    # GET ARTICLE
    # =====================================================

    def get_article(self, gencod):

        self.cursor.execute("""
            SELECT * FROM articles WHERE gencod = ?
        """, (gencod,))

        return self.cursor.fetchone()

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all_articles(self):

        self.cursor.execute("""
            SELECT * FROM articles ORDER BY id DESC
        """)

        return self.cursor.fetchall()

    # =====================================================
    # PAGINATION
    # =====================================================

    def get_articles_paginated(self, limit=20, offset=0, search=""):

        query = "SELECT * FROM articles"
        params = []

        if search:
            query += """
                WHERE titre LIKE ?
                OR auteurs LIKE ?
                OR editeur LIKE ?
                OR gencod LIKE ?
                OR isbn LIKE ?
                OR categorie LIKE ?
            """
            s = f"%{search}%"
            params.extend([s, s, s, s, s, s])

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    # =====================================================
    # COUNT
    # =====================================================

    def count_articles(self, search=""):

        query = "SELECT COUNT(*) as total FROM articles"
        params = []

        if search:
            query += """
                WHERE titre LIKE ?
                OR auteurs LIKE ?
                OR editeur LIKE ?
                OR gencod LIKE ?
                OR isbn LIKE ?
                OR categorie LIKE ?
            """
            s = f"%{search}%"
            params.extend([s, s, s, s, s, s])

        self.cursor.execute(query, params)
        return self.cursor.fetchone()["total"]

    # =====================================================
    # EXISTS
    # =====================================================

    def article_exists(self, gencod):

        self.cursor.execute("""
            SELECT id FROM articles WHERE gencod = ?
        """, (gencod,))

        return self.cursor.fetchone() is not None

    # =====================================================
    # DELETE
    # =====================================================

    def delete_article(self, gencod):

        self.cursor.execute("""
            DELETE FROM articles WHERE gencod = ?
        """, (gencod,))

        self.connection.commit()

    # =====================================================
    # STOCK VALUE
    # =====================================================

    def get_total_stock_value(self):

        self.cursor.execute("""
            SELECT SUM(prix * stock) as total FROM articles
        """)

        result = self.cursor.fetchone()
        return result["total"] or 0

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        if self.connection:
            self.connection.close()