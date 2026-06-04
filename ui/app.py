import sys
import traceback
import logging

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from ui.main_window import MainWindow

# ✅ Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("mdp_sync.log"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("app")

STYLE = """
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
    color: #f5f5f5;
}

QLineEdit:focus {
    border: 1px solid #0078d7;
}

QTextEdit {
    background-color: #252526;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 5px;
}

QTableWidget {
    background-color: #252526;
    gridline-color: #444;
    border: 1px solid #444;
}

QTableWidget::item {
    padding: 5px;
}

QHeaderView::section {
    background-color: #333333;
    color: white;
    padding: 6px;
    border: none;
    font-weight: bold;
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

QDialog {
    background-color: #1e1e1e;
}

QLabel {
    color: #f5f5f5;
}

QMessageBox {
    background-color: #1e1e1e;
}

QMessageBox QLabel {
    color: #f5f5f5;
}
"""


def main():
    """Main application entry point"""

    try:
        log.info("🚀 Application démarrage...")

        app = QApplication(sys.argv)

        # ✅ Style global
        app.setStyleSheet(STYLE)

        # ✅ Create main window
        window = MainWindow()
        window.show()

        log.info("✅ Application lancée")

        exit_code = app.exec()

        log.info(f"Application fermée (code: {exit_code})")

        return exit_code

    except Exception as e:
        log.critical("💥 ERREUR FATALE")
        traceback.print_exc()

        # ✅ Show error dialog
        try:
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Erreur critique",
                f"L'application a rencontré une erreur:\n\n{str(e)}\n\nConsultez mdp_sync.log pour plus de détails"
            )
        except Exception:
            print(f"FATAL: {e}")

        return 1


if __name__ == "__main__":
    sys.exit(main())