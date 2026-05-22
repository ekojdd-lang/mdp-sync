import requests

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit
)

from PySide6.QtGui import QPixmap

from PySide6.QtCore import Qt


class ArticleDialog(QDialog):

    def __init__(self, article):

        super().__init__()

        self.setWindowTitle(
            article["titre"]
        )

        self.resize(700, 600)

        layout = QVBoxLayout()

        # image couverture
        image_label = QLabel()

        image_label.setAlignment(
            Qt.AlignCenter
        )

        image_url = article["image_url"]

        if image_url:

            try:

                response = requests.get(
                    image_url,
                    timeout=10
                )

                if response.status_code == 200:

                    pixmap = QPixmap()

                    pixmap.loadFromData(
                        response.content
                    )

                    pixmap = pixmap.scaled(
                        250,
                        350,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )

                    image_label.setPixmap(
                        pixmap
                    )

            except Exception:

                image_label.setText(
                    "Image indisponible"
                )

        titre = QLabel(
            f"<h2>{article['titre']}</h2>"
        )

        titre.setWordWrap(True)

        auteurs = QLabel(
            f"Auteur(s) : {article['auteurs']}"
        )

        auteurs.setWordWrap(True)

        editeur = QLabel(
            f"Editeur : {article['editeur']}"
        )

        prix = QLabel(
            f"Prix : {article['prix']} FCFA"
        )

        presentation = QTextEdit()

        presentation.setReadOnly(True)

        presentation.setText(
            str(article["presentation"])
        )

        layout.addWidget(image_label)

        layout.addWidget(titre)

        layout.addWidget(auteurs)

        layout.addWidget(editeur)

        layout.addWidget(prix)

        layout.addWidget(presentation)

        self.setLayout(layout)