import requests
import io
import logging
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QProgressBar
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal, QTimer

log = logging.getLogger("article_dialog")

# ✅ Global image cache
_image_cache = {}
_image_executor = ThreadPoolExecutor(max_workers=2)


class ImageLoaderThread(QThread):
    """Load image asynchronously without blocking UI"""
    
    image_loaded = Signal(QPixmap)
    image_error = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        """Load image in background thread"""
        try:
            # ✅ Check cache first
            if self.url in _image_cache:
                log.debug(f"Image from cache: {self.url}")
                self.image_loaded.emit(_image_cache[self.url])
                return

            # ✅ Download with timeout
            response = requests.get(
                self.url,
                timeout=10,
                headers={"User-Agent": "MDP-Sync/1.0"}
            )

            if response.status_code != 200:
                self.image_error.emit(f"HTTP {response.status_code}")
                return

            # ✅ Load image
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)

            if pixmap.isNull():
                self.image_error.emit("Format image invalide")
                return

            # ✅ Scale
            pixmap = pixmap.scaled(
                250, 350,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # ✅ Cache it
            _image_cache[self.url] = pixmap

            self.image_loaded.emit(pixmap)

        except requests.Timeout:
            self.image_error.emit("Timeout (10s)")
        except requests.ConnectionError:
            self.image_error.emit("Erreur connexion")
        except Exception as e:
            log.error(f"Image load error: {e}")
            self.image_error.emit(f"Erreur: {str(e)}")


class ArticleDialog(QDialog):
    """Article detail dialog with async image loading"""

    def __init__(self, article: dict):
        super().__init__()

        self.article = article or {}
        self.image_thread = None

        self.setWindowTitle(self.article.get("titre", "Article"))
        self.resize(700, 600)

        layout = QVBoxLayout()

        # ===== IMAGE LOADING =====
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(350)

        # ✅ Loading indicator
        self.loading_progress = QProgressBar()
        self.loading_progress.setMaximum(0)  # Animated
        self.loading_progress.setVisible(False)

        image_url = self.article.get("image_url")

        if image_url:
            self.loading_progress.setVisible(True)

            # ✅ Start async image load
            self.image_thread = ImageLoaderThread(image_url)
            self.image_thread.image_loaded.connect(self._on_image_loaded)
            self.image_thread.image_error.connect(self._on_image_error)
            self.image_thread.start()
        else:
            self.image_label.setText("❌ Pas d'image")

        # ===== INFOS =====
        titre = QLabel(f"<h2>{self.article.get('titre', 'Sans titre')}</h2>")
        titre.setWordWrap(True)

        auteurs = self.article.get('auteurs', 'Non renseigné')
        if isinstance(auteurs, list):
            auteurs = ", ".join(auteurs)

        auteurs_label = QLabel(f"<b>Auteur(s):</b> {auteurs}")
        auteurs_label.setWordWrap(True)

        editeur = QLabel(f"<b>Éditeur:</b> {self.article.get('editeur', 'Non renseigné')}")
        editeur.setWordWrap(True)

        prix = self.article.get('prix', 0)
        try:
            prix = float(prix)
            prix_label = QLabel(f"<b>Prix:</b> {prix:,.2f} FCFA")
        except (ValueError, TypeError):
            prix_label = QLabel(f"<b>Prix:</b> N/A")

        type_produit = QLabel(f"<b>Type:</b> {self.article.get('type_produit', 'Non renseigné')}")

        # ===== DESCRIPTION =====
        presentation = QTextEdit()
        presentation.setReadOnly(True)
        
        desc = str(self.article.get("presentation", "Pas de description disponible")).strip()
        if not desc or desc == "None":
            desc = "Pas de description disponible"

        presentation.setText(desc)

        # ===== LAYOUT =====
        layout.addWidget(self.image_label)
        layout.addWidget(self.loading_progress)
        layout.addWidget(titre)
        layout.addWidget(auteurs_label)
        layout.addWidget(editeur)
        layout.addWidget(prix_label)
        layout.addWidget(type_produit)
        layout.addWidget(QLabel("<b>Description:</b>"))
        layout.addWidget(presentation)

        self.setLayout(layout)

    # ===== CALLBACKS =====
    def _on_image_loaded(self, pixmap: QPixmap):
        """Image loaded successfully"""
        self.loading_progress.setVisible(False)
        self.image_label.setPixmap(pixmap)

    def _on_image_error(self, error: str):
        """Image load error"""
        self.loading_progress.setVisible(False)
        self.image_label.setText(f"❌ Image indisponible\n({error})")

    def closeEvent(self, event):
        """Cleanup on close"""
        try:
            if self.image_thread and self.image_thread.isRunning():
                self.image_thread.quit()
                self.image_thread.wait(1000)
        except Exception as e:
            log.error(f"Close error: {e}")

        event.accept()