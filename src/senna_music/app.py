from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from senna_music.core.storage import initialize_database
from senna_music.ui.main_window import MainWindow


def main() -> int:
    initialize_database()
    app = QApplication(sys.argv)
    app.setApplicationName("Senna Music")
    app.setOrganizationName("Admir")
    app.setApplicationVersion("0.1.0")
    window = MainWindow()
    window.show()
    return app.exec()
