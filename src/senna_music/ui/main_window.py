from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from senna_music.core.storage import (
    add_library_folder,
    list_library_folders,
    remove_library_folder,
)


PAGES = [
    ("Home", "Home"),
    ("Local Music", "Local Music"),
    ("Playlists", "Playlists"),
    ("Favorites", "Favorites"),
    ("Download Queue", "Download Queue"),
    ("Search Sources", "Search Sources"),
    ("Settings", "Settings"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Senna Music")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)
        self._nav_buttons: dict[str, QPushButton] = {}
        self._pages: dict[str, QWidget] = {}
        self._build_ui()
        self._show_page("Home")

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(208)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 22, 16, 16)
        side_layout.setSpacing(8)

        brand = QLabel("SENNA MUSIC")
        brand.setObjectName("brand")
        side_layout.addWidget(brand)
        side_layout.addSpacing(20)

        for label, page_name in PAGES:
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, name=page_name: self._show_page(name))
            side_layout.addWidget(button)
            self._nav_buttons[page_name] = button

        side_layout.addStretch(1)
        version = QLabel("Version 0.1.0 · Early build")
        version.setObjectName("muted")
        side_layout.addWidget(version)

        self.stack = QStackedWidget()
        self.stack.setObjectName("workspace")
        for _, page_name in PAGES:
            page = self._make_page(page_name)
            self._pages[page_name] = page
            self.stack.addWidget(page)

        body.addWidget(sidebar)
        body.addWidget(self.stack, 1)
        root_layout.addLayout(body, 1)
        root_layout.addWidget(self._build_player())
        self.setCentralWidget(root)
        self.setStyleSheet(self._stylesheet())

    def _make_page(self, name: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 28, 34, 24)
        layout.setSpacing(16)

        title = QLabel(name)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        if name == "Home":
            intro = QLabel("Your music, in one place.")
            intro.setObjectName("muted")
            layout.addWidget(intro)
            search_row = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Search tracks, artists or albums…")
            self.search_input.setMinimumHeight(44)
            self.search_input.returnPressed.connect(self._search)
            search_button = QPushButton("Search")
            search_button.setMinimumHeight(44)
            search_button.clicked.connect(self._search)
            search_row.addWidget(self.search_input, 1)
            search_row.addWidget(search_button)
            layout.addLayout(search_row)
            self.search_status = QLabel(
                "Online search adapters are being connected in the next development step."
            )
            self.search_status.setObjectName("muted")
            layout.addWidget(self.search_status)
            for section in ("Recently Played", "Playlists", "Local Music"):
                heading = QLabel(section)
                heading.setObjectName("sectionTitle")
                layout.addWidget(heading)
                hint = QLabel("Your " + section.lower() + " will appear here.")
                hint.setObjectName("muted")
                layout.addWidget(hint)
            layout.addStretch(1)

        elif name == "Local Music":
            intro = QLabel("Choose the folders that contain your music.")
            intro.setObjectName("muted")
            layout.addWidget(intro)
            actions = QHBoxLayout()
            add_button = QPushButton("Add Music Folder")
            add_button.clicked.connect(self._add_folder)
            actions.addWidget(add_button)
            actions.addStretch(1)
            layout.addLayout(actions)
            self.folder_list = QListWidget()
            self.folder_list.setObjectName("folderList")
            layout.addWidget(self.folder_list, 1)
            remove_button = QPushButton("Remove Selected Folder")
            remove_button.clicked.connect(self._remove_folder)
            layout.addWidget(remove_button, 0, Qt.AlignmentFlag.AlignLeft)
            self._refresh_folders()

        elif name == "Search Sources":
            intro = QLabel("Enable and configure the sources used by integrated search.")
            intro.setObjectName("muted")
            layout.addWidget(intro)
            for source in ("YouTube", "Spotify", "SoundCloud"):
                row = QFrame()
                row.setObjectName("sourceRow")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(14, 10, 14, 10)
                row_layout.addWidget(QLabel(source), 1)
                status = QLabel("Not configured")
                status.setObjectName("muted")
                row_layout.addWidget(status)
                layout.addWidget(row)
            layout.addStretch(1)

        elif name == "Settings":
            intro = QLabel("Application preferences will be added incrementally.")
            intro.setObjectName("muted")
            layout.addWidget(intro)
            layout.addStretch(1)

        else:
            intro = QLabel(f"{name} will be implemented in the next milestones.")
            intro.setObjectName("muted")
            layout.addWidget(intro)
            layout.addStretch(1)

        return page

    def _build_player(self) -> QWidget:
        player = QFrame()
        player.setObjectName("playerBar")
        player.setFixedHeight(76)
        row = QHBoxLayout(player)
        row.setContentsMargins(22, 8, 22, 8)
        track = QLabel("Nothing playing")
        track.setObjectName("playerTrack")
        row.addWidget(track, 1)
        self.player_status = QLabel("Local player is being connected")
        self.player_status.setObjectName("muted")
        row.addWidget(self.player_status)
        return player

    def _show_page(self, name: str) -> None:
        self.stack.setCurrentWidget(self._pages[name])
        for page_name, button in self._nav_buttons.items():
            button.setChecked(page_name == name)

    def _search(self) -> None:
        query = self.search_input.text().strip()
        if len(query) < 2:
            self.search_status.setText("Enter at least 2 characters to search.")
            return
        self.search_status.setText(
            "Search UI is ready. Source adapters are scheduled for the next milestone."
        )

    def _refresh_folders(self) -> None:
        if not hasattr(self, "folder_list"):
            return
        self.folder_list.clear()
        for folder in list_library_folders():
            self.folder_list.addItem(folder)

    def _add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select a music folder")
        if not folder:
            return
        if not Path(folder).is_dir():
            QMessageBox.warning(self, "Invalid folder", "The selected folder is not available.")
            return
        add_library_folder(folder)
        self._refresh_folders()

    def _remove_folder(self) -> None:
        item = self.folder_list.currentItem()
        if item is None:
            return
        folder = item.text()
        answer = QMessageBox.question(
            self,
            "Remove music folder",
            "Remove this folder from the Senna Music library list? Files on disk will not be deleted.",
        )
        if answer == QMessageBox.StandardButton.Yes:
            remove_library_folder(folder)
            self._refresh_folders()

    @staticmethod
    def _stylesheet() -> str:
        return """
        QMainWindow, QWidget#workspace { background: #17191e; color: #eceef2; }
        QWidget { color: #eceef2; font-family: Segoe UI, sans-serif; font-size: 14px; }
        QFrame#sidebar { background: #111318; border-right: 1px solid #2b2e36; }
        QLabel#brand { color: #ffffff; font-size: 17px; font-weight: 700; letter-spacing: 1px; }
        QLabel#pageTitle { font-size: 27px; font-weight: 650; color: #ffffff; }
        QLabel#sectionTitle { font-size: 17px; font-weight: 600; margin-top: 12px; }
        QLabel#muted { color: #9da3af; }
        QPushButton#navButton { text-align: left; padding: 11px 13px; border: 0; border-radius: 7px; color: #c4c8d0; background: transparent; }
        QPushButton#navButton:hover { background: #222630; }
        QPushButton#navButton:checked { color: #ffffff; background: #292e39; border-left: 3px solid #76a7fa; }
        QPushButton { background: #303744; color: #ffffff; border: 1px solid #414957; border-radius: 7px; padding: 9px 14px; }
        QPushButton:hover { background: #3a4555; }
        QLineEdit, QListWidget { background: #20232b; border: 1px solid #383d48; border-radius: 7px; padding: 9px; selection-background-color: #3b5f91; }
        QFrame#playerBar { background: #111318; border-top: 1px solid #2b2e36; }
        QLabel#playerTrack { font-weight: 600; }
        QFrame#sourceRow { background: #20232b; border: 1px solid #303540; border-radius: 8px; }
        """
