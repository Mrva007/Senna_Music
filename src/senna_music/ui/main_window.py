from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from senna_music.core.scanner import scan_library
from senna_music.core.storage import (
    add_library_folder,
    get_setting,
    list_library_folders,
    list_tracks,
    remove_library_folder,
    set_setting,
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


class LibraryScanThread(QThread):
    completed = Signal(int)
    failed = Signal(str)

    def run(self) -> None:
        try:
            self.completed.emit(scan_library())
        except Exception as error:  # noqa: BLE001 - report background scan failures in the UI
            self.failed.emit(str(error))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Senna Music")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)
        self._nav_buttons: dict[str, QPushButton] = {}
        self._pages: dict[str, QWidget] = {}
        self._scan_thread: LibraryScanThread | None = None
        self._build_ui()
        self._show_page("Home")
        self._start_scan()

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
            intro = QLabel("Choose folders that contain your music. Subfolders are scanned too.")
            intro.setObjectName("muted")
            layout.addWidget(intro)
            actions = QHBoxLayout()
            add_button = QPushButton("Add Music Folder")
            add_button.clicked.connect(self._add_folder)
            actions.addWidget(add_button)
            self.scan_button = QPushButton("Scan Library")
            self.scan_button.clicked.connect(self._start_scan)
            actions.addWidget(self.scan_button)
            actions.addStretch(1)
            layout.addLayout(actions)

            self.folder_list = QListWidget()
            self.folder_list.setMaximumHeight(105)
            self.folder_list.setObjectName("folderList")
            layout.addWidget(self.folder_list)

            self.scan_status = QLabel("")
            self.scan_status.setObjectName("muted")
            layout.addWidget(self.scan_status)

            self.track_table = QTableWidget(0, 5)
            self.track_table.setHorizontalHeaderLabels(
                ["Track name", "Artist", "Album", "Duration", "Source"]
            )
            self.track_table.setAlternatingRowColors(True)
            self.track_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.track_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.track_table.verticalHeader().setVisible(False)
            self.track_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.track_table.horizontalHeader().setSectionsClickable(True)
            self.track_table.horizontalHeader().setSortIndicatorShown(True)
            self.track_table.setSortingEnabled(True)
            layout.addWidget(self.track_table, 1)
            remove_button = QPushButton("Remove Selected Folder")
            remove_button.clicked.connect(self._remove_folder)
            layout.addWidget(remove_button, 0, Qt.AlignmentFlag.AlignLeft)
            self._refresh_folders()
            self._refresh_tracks()

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
                source_key = source.casefold()
                enabled = get_setting(f"source_enabled:{source_key}", "false") == "true"
                toggle = QCheckBox("Enabled")
                toggle.setChecked(enabled)
                status = QLabel("Enabled" if enabled else "Disabled")
                status.setObjectName("muted")

                def save_source_state(
                    value: bool, key: str = source_key, status_label: QLabel = status
                ) -> None:
                    set_setting(f"source_enabled:{key}", "true" if value else "false")
                    status_label.setText("Enabled" if value else "Disabled")

                toggle.toggled.connect(save_source_state)
                row_layout.addWidget(toggle)
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

    def _refresh_tracks(self) -> None:
        if not hasattr(self, "track_table"):
            return
        self.track_table.setSortingEnabled(False)
        tracks = list_tracks()
        self.track_table.setRowCount(len(tracks))
        for row, track in enumerate(tracks):
            values = [
                track["title"],
                track["artist"],
                track["album"],
                self._format_duration(track["duration"]),
                "Local Music",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0 and track["scan_error"]:
                    item.setText("⚠ " + value)
                    item.setToolTip(track["scan_error"])
                    item.setForeground(Qt.GlobalColor.red)
                self.track_table.setItem(row, column, item)
        self.track_table.setSortingEnabled(True)

    @staticmethod
    def _format_duration(seconds: float | None) -> str:
        if seconds is None:
            return "—"
        total = int(seconds)
        return f"{total // 60}:{total % 60:02d}"

    def _start_scan(self) -> None:
        if self._scan_thread is not None and self._scan_thread.isRunning():
            return
        self.scan_button.setEnabled(False)
        self.scan_status.setText("Scanning registered music folders…")
        self._scan_thread = LibraryScanThread(self)
        self._scan_thread.completed.connect(self._scan_completed)
        self._scan_thread.failed.connect(self._scan_failed)
        self._scan_thread.start()

    def _scan_completed(self, count: int) -> None:
        self.scan_button.setEnabled(True)
        self.scan_status.setText(f"Scan complete · {count} audio files found.")
        self._refresh_tracks()

    def _scan_failed(self, message: str) -> None:
        self.scan_button.setEnabled(True)
        self.scan_status.setText("Scan failed: " + message)

    def _add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select a music folder")
        if not folder:
            return
        if not Path(folder).is_dir():
            QMessageBox.warning(self, "Invalid folder", "The selected folder is not available.")
            return
        add_library_folder(folder)
        self._refresh_folders()
        self._start_scan()

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
            self._refresh_tracks()

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
        QLineEdit, QListWidget, QTableWidget { background: #20232b; border: 1px solid #383d48; border-radius: 7px; padding: 7px; selection-background-color: #3b5f91; }
        QHeaderView::section { background: #252a34; color: #cbd1dc; padding: 8px; border: 0; border-bottom: 1px solid #383d48; }
        QTableWidget::item { padding: 6px; }
        QFrame#playerBar { background: #111318; border-top: 1px solid #2b2e36; }
        QLabel#playerTrack { font-weight: 600; }
        QFrame#sourceRow { background: #20232b; border: 1px solid #303540; border-radius: 8px; }
        """
