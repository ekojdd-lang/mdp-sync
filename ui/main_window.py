from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QFileDialog,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QHBoxLayout
)

from ui.sync_worker import SyncWorker

from ui.article_dialog import ArticleDialog

from core.database import DatabaseManager


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "MDP Sync Engine"
        )

        self.resize(1000, 700)

        self.current_page = 1

        self.page_size = 50

        layout = QVBoxLayout()

        title = QLabel(
            "Maison de la Presse Sync"
        )

        # champ recherche
        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Rechercher un article..."
        )

        self.search_input.textChanged.connect(
            self.filter_table
        )

        self.logs = QTextEdit()

        self.logs.setReadOnly(True)

        self.progress_bar = QProgressBar()

        self.progress_bar.setValue(0)

        self.sync_button = QPushButton(
            "Importer et Synchroniser"
        )

        self.sync_button.clicked.connect(
            self.start_sync
        )

        # tableau articles
        self.table = QTableWidget()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "Gencod",
            "Titre",
            "Prix",
            "Editeur"
        ])

        # tri colonnes
        self.table.setSortingEnabled(True)

        # double clic article
        self.table.cellDoubleClicked.connect(
            self.open_article
        )

        # pagination
        pagination_layout = QHBoxLayout()

        self.prev_button = QPushButton(
            "Précédent"
        )

        self.next_button = QPushButton(
            "Suivant"
        )

        self.page_label = QLabel()

        self.prev_button.clicked.connect(
            self.previous_page
        )

        self.next_button.clicked.connect(
            self.next_page
        )

        pagination_layout.addWidget(
            self.prev_button
        )

        pagination_layout.addWidget(
            self.page_label
        )

        pagination_layout.addWidget(
            self.next_button
        )

        layout.addWidget(title)

        layout.addWidget(self.search_input)

        layout.addWidget(self.sync_button)

        layout.addWidget(self.progress_bar)

        layout.addWidget(self.table)

        layout.addLayout(
            pagination_layout
        )

        layout.addWidget(self.logs)

        self.setLayout(layout)

        self.worker = None

        # charger articles existants
        self.load_articles_table()

    def log(self, message):

        self.logs.append(message)

    def load_articles_table(self):

        db = DatabaseManager()

        total_articles = db.count_articles()

        total_pages = max(
            1,
            (
                total_articles
                + self.page_size
                - 1
            ) // self.page_size
        )

        offset = (
            self.current_page - 1
        ) * self.page_size

        articles = db.get_articles_paginated(
            limit=self.page_size,
            offset=offset
        )

        self.table.setRowCount(
            len(articles)
        )

        for row, article in enumerate(articles):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(article["gencod"])
                )
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(article["titre"])
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(article["prix"])
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    str(article["editeur"])
                )
            )

        self.page_label.setText(
            f"Page {self.current_page} / {total_pages}"
        )

        self.prev_button.setEnabled(
            self.current_page > 1
        )

        self.next_button.setEnabled(
            self.current_page < total_pages
        )

        self.table.resizeColumnsToContents()

        db.close()

    def filter_table(self):

        search = (
            self.search_input
            .text()
            .lower()
        )

        for row in range(
            self.table.rowCount()
        ):

            visible = False

            for col in range(
                self.table.columnCount()
            ):

                item = self.table.item(
                    row,
                    col
                )

                if item:

                    text = item.text().lower()

                    if search in text:

                        visible = True

                        break

            self.table.setRowHidden(
                row,
                not visible
            )

    def open_article(self, row, column):

        gencod_item = self.table.item(
            row,
            0
        )

        if not gencod_item:

            return

        gencod = gencod_item.text()

        db = DatabaseManager()

        article = db.get_article(gencod)

        db.close()

        if not article:

            return

        dialog = ArticleDialog(article)

        dialog.exec()

    def next_page(self):

        self.current_page += 1

        self.load_articles_table()

    def previous_page(self):

        if self.current_page > 1:

            self.current_page -= 1

            self.load_articles_table()

    def start_sync(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir fichier Excel",
            "",
            "Excel Files (*.xlsx)"
        )

        if not file_path:

            return

        # désactiver bouton
        self.sync_button.setEnabled(False)

        # reset UI
        self.logs.clear()

        self.progress_bar.setValue(0)

        # création worker
        self.worker = SyncWorker(file_path)

        # connexion logs
        self.worker.log_signal.connect(
            self.log
        )

        # connexion progression
        self.worker.progress_signal.connect(
            self.progress_bar.setValue
        )

        # fin worker
        self.worker.finished_signal.connect(
            self.sync_finished
        )

        # démarrage thread
        self.worker.start()

    def sync_finished(self):

        self.progress_bar.setValue(100)

        self.current_page = 1

        self.load_articles_table()

        self.log(
            "\nSYNC TERMINEE"
        )

        # réactiver bouton
        self.sync_button.setEnabled(True)