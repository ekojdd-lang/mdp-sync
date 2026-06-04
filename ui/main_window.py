from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel,
    QFileDialog, QProgressBar, QTableWidget, QTableWidgetItem,
    QLineEdit, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

from ui.sync_worker import SyncWorker
from ui.article_dialog import ArticleDialog
from core.database import DatabaseManager


class MainWindow(QWidget):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MDP Sync Engine")
        self.resize(1200, 800)

        self.current_page = 1
        self.page_size = 50
        self.total_pages = 1

        # ✅ Singleton DB instance
        self.db = DatabaseManager()

        self.worker = None

        # UI Layout
        layout = QVBoxLayout()

        # ===== TITLE =====
        title = QLabel("Maison de la Presse Sync Engine")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        # ===== SEARCH =====
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un article (titre, code, éditeur...)...")
        self.search_input.textChanged.connect(self.filter_table)

        # ===== PROGRESS =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # ===== STATS =====
        self.stats_label = QLabel("Prêt")
        self.stats_label.setStyleSheet("color: #666; font-size: 11px;")

        # ===== SYNC BUTTON =====
        self.sync_button = QPushButton("📥 Importer et Synchroniser")
        self.sync_button.clicked.connect(self.start_sync)
        self.sync_button.setMinimumHeight(40)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Code",
            "Type",
            "Titre",
            "Prix",
            "Éditeur"
        ])

        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.open_article)
        self.table.setAlternatingRowColors(True)

        # ===== PAGINATION =====
        pagination_layout = QHBoxLayout()

        self.prev_button = QPushButton("◄ Précédent")
        self.next_button = QPushButton("Suivant ►")
        self.page_label = QLabel("Page 1 / 1")

        self.prev_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.next_button)

        # ===== LOGS =====
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setMaximumHeight(150)

        # ===== ASSEMBLE LAYOUT =====
        layout.addWidget(title)
        layout.addWidget(self.search_input)
        layout.addWidget(self.sync_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.stats_label)
        layout.addWidget(QLabel("Articles:"))
        layout.addWidget(self.table)
        layout.addLayout(pagination_layout)
        layout.addWidget(QLabel("Logs:"))
        layout.addWidget(self.logs)

        self.setLayout(layout)

        # Initial load
        self.load_articles_table()

    # =========================================================
    # LOGGING
    # =========================================================
    def log(self, message):
        """Add log message to text edit"""
        self.logs.append(message)
        # Auto-scroll to bottom
        self.logs.verticalScrollBar().setValue(
            self.logs.verticalScrollBar().maximum()
        )

    # =========================================================
    # TABLE LOADING
    # =========================================================
    def load_articles_table(self):
        """Load articles from DB with pagination"""

        try:
            # ✅ Récupérer TOUS les articles
            all_articles = self.db.get_all_articles()

            if not all_articles:
                self.table.setRowCount(0)
                self.page_label.setText("Aucun article")
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
                self.update_stats(0, 0)
                return

            total_articles = len(all_articles)
            self.total_pages = max(
                1,
                (total_articles + self.page_size - 1) // self.page_size
            )

            # Clamp page
            self.current_page = max(1, min(self.current_page, self.total_pages))

            # Paginer manuellement
            start_idx = (self.current_page - 1) * self.page_size
            end_idx = start_idx + self.page_size
            articles = all_articles[start_idx:end_idx]

            # ✅ Populate table
            self.table.setRowCount(len(articles))

            for row, article in enumerate(articles):
                code = (
                    article.get("code_article")
                    or article.get("isbn")
                    or article.get("ean")
                    or article.get("gencod")
                    or ""
                )

                self.table.setItem(row, 0, QTableWidgetItem(str(code)))
                self.table.setItem(row, 1, QTableWidgetItem(str(article.get("type_produit", ""))))
                self.table.setItem(row, 2, QTableWidgetItem(str(article.get("titre", ""))))
                self.table.setItem(row, 3, QTableWidgetItem(f"${article.get('prix', 0)}"))
                self.table.setItem(row, 4, QTableWidgetItem(str(article.get("editeur", ""))))

            self.page_label.setText(f"Page {self.current_page} / {self.total_pages}")

            self.prev_button.setEnabled(self.current_page > 1)
            self.next_button.setEnabled(self.current_page < self.total_pages)

            self.table.resizeColumnsToContents()

            # ✅ Update stats
            available = len([a for a in all_articles if a.get("stock", 0) > 0])
            self.update_stats(total_articles, available)

        except Exception as e:
            self.log(f"❌ Erreur chargement table: {str(e)}")

    def update_stats(self, total, available):
        """Update statistics label"""
        self.stats_label.setText(
            f"Total: {total} articles | Disponibles: {available}"
        )

    # =========================================================
    # FILTERING
    # =========================================================
    def filter_table(self):
        """Filter table by search text"""

        search = self.search_input.text().lower()

        visible_count = 0

        for row in range(self.table.rowCount()):
            visible = False

            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)

                if item and search in item.text().lower():
                    visible = True
                    break

            self.table.setRowHidden(row, not visible)
            if visible:
                visible_count += 1

    # =========================================================
    # ARTICLE DIALOG
    # =========================================================
    def open_article(self, row, column):
        """Open article detail dialog"""

        gencod_item = self.table.item(row, 0)

        if not gencod_item:
            return

        try:
            article = self.db.get_article(gencod_item.text())
        except Exception as e:
            self.log(f"❌ Erreur: {str(e)}")
            return

        if not article:
            QMessageBox.warning(self, "Erreur", "Article non trouvé")
            return

        dialog = ArticleDialog(article)
        dialog.exec()

    # =========================================================
    # PAGINATION
    # =========================================================
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_articles_table()

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_articles_table()

    # =========================================================
    # SYNCHRONIZATION
    # =========================================================
    def start_sync(self):
        """Start sync process"""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir fichier Excel à synchroniser",
            "",
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if not file_path:
            return

        # ✅ Disable button during sync
        self.sync_button.setEnabled(False)
        self.logs.clear()
        self.progress_bar.setValue(0)

        # ✅ Create worker
        self.worker = SyncWorker(file_path)

        # ✅ Connect signals
        self.worker.log_signal.connect(self.log)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.sync_finished)

        # ✅ Start async thread
        self.worker.start()

    def update_progress(self, progress, success, failed):
        """Update progress during sync"""
        self.progress_bar.setValue(progress)
        self.stats_label.setText(
            f"Sync: {success} ✅ | {failed} ❌ | {progress}%"
        )

    def sync_finished(self, result):
        """Sync finished callback"""

        self.progress_bar.setValue(100)
        self.current_page = 1
        self.load_articles_table()

        success = result.get("success", 0)
        failed = result.get("failed", 0)
        total = result.get("total", 0)

        msg = f"Synchronisation terminée!\n\n✅ {success} articles\n❌ {failed} erreurs\n📊 Total: {total}"

        self.log(f"\n{msg}")

        QMessageBox.information(self, "✅ Sync terminée", msg)

        self.sync_button.setEnabled(True)

    # =========================================================
    # CLEANUP
    # =========================================================
    def closeEvent(self, event):
        """Cleanup on close"""
        try:
            if self.worker and self.worker.isRunning():
                self.worker.stop()
                self.worker.wait(5000)

            self.db.close()
        except Exception as e:
            print(f"Error on close: {e}")

        event.accept()