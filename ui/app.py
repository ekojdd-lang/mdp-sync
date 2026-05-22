import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setStyleSheet(
        """
        QWidget {
            background-color: #1e1e1e;
            color: #f5f5f5;
            font-size: 14px;
        }

        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #2893ff;
        }

        QPushButton:disabled {
            background-color: #555555;
        }

        QLineEdit {
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #555;
            background-color: #2d2d2d;
        }

        QTextEdit {
            background-color: #252526;
            border: 1px solid #444;
            border-radius: 6px;
        }

        QTableWidget {
            background-color: #252526;
            gridline-color: #444;
            border: 1px solid #444;
        }

        QHeaderView::section {
            background-color: #333333;
            color: white;
            padding: 6px;
            border: none;
        }

        QProgressBar {
            border: 1px solid #555;
            border-radius: 5px;
            text-align: center;
            background-color: #2d2d2d;
        }

        QProgressBar::chunk {
            background-color: #00b894;
            border-radius: 5px;
        }
        """
    )

    window = MainWindow()

    window.show()

    sys.exit(app.exec())