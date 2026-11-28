from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSlider,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from senna_music.core.collections import (
    add_favorites,
    add_tracks_to_favorite_collection,
    add_tracks_to_playlist,
    create_favorite_collection,
    create_playlist,
    delete_favorite_collection,
    delete_playlist,
    list_favorite_collection_tracks,
    list_favorite_collections,
    list_favorites,
    list_playlist_tracks,
    list_playlists,
    remove_favorite,
    remove_track_from_favorite_collection,
    remove_track_from_playlist,
    rename_favorite_collection,
    rename_playlist,
)
from senna_music.core.metadata import read_cover_art, update_track_metadata
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
MONITOR_INTERVAL_MS = 60_000


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
        self._tracks: list[dict] = []
        self._current_track_path: str | None = None
        self._slider_is_pressed = False

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)
        self.player.positionChanged.connect(self._position_changed)
        self.player.durationChanged.connect(self._duration_changed)
        self.player.playbackStateChanged.connect(self._playback_state_changed)
        self.player.mediaStatusChanged.connect(self._media_status_changed)

        self._build_ui()
        self._show_page("Home")
        self._start_scan()

        self._monitor_timer = QTimer(self)
        self._monitor_timer.setInterval(MONITOR_INTERVAL_MS)
        self._monitor_timer.timeout.connect(self._start_scan)
        self._monitor_timer.start()

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
                "Enable one or more sources on Search Sources to start online discovery."
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
            intro = QLabel(
                "Choose music folders. Subfolders are scanned automatically while the app runs."
            )
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
            self.track_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
            self.track_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.track_table.verticalHeader().setVisible(False)
            self.track_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.track_table.horizontalHeader().setSectionsClickable(True)
            self.track_table.horizontalHeader().setSortIndicatorShown(True)
            self.track_table.setSortingEnabled(True)
            self.track_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.track_table.customContextMenuRequested.connect(self._track_context_menu)
            self.track_table.cellDoubleClicked.connect(self._play_selected_track)
            layout.addWidget(self.track_table, 1)

            remove_button = QPushButton("Remove Selected Folder")
            remove_button.clicked.connect(self._remove_folder)
            layout.addWidget(remove_button, 0, Qt.AlignmentFlag.AlignLeft)
            self._refresh_folders()
            self._refresh_tracks()

        elif name == "Search Sources":
            intro = QLabel("Enable the sources you want included in the next search.")
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


        elif name == "Playlists":
            actions = QHBoxLayout()
            for label, callback in (
                ("New Playlist", self._create_playlist),
                ("Rename", self._rename_playlist),
                ("Delete", self._delete_playlist),
                ("Add Tracks", self._add_tracks_to_playlist),
            ):
                button = QPushButton(label)
                button.clicked.connect(callback)
                actions.addWidget(button)
            actions.addStretch(1)
            layout.addLayout(actions)
            self.playlist_list = QListWidget()
            self.playlist_list.currentItemChanged.connect(self._refresh_playlist_tracks)
            layout.addWidget(self.playlist_list, 1)
            self.playlist_tracks_table = QTableWidget(0, 4)
            self.playlist_tracks_table.setHorizontalHeaderLabels(
                ["Track", "Artist", "Album", "Duration"]
            )
            self.playlist_tracks_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.playlist_tracks_table.setSelectionBehavior(
                QTableWidget.SelectionBehavior.SelectRows
            )
            self.playlist_tracks_table.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )
            self.playlist_tracks_table.customContextMenuRequested.connect(
                self._playlist_track_menu
            )
            self.playlist_tracks_table.cellDoubleClicked.connect(
                self._play_playlist_track
            )
            layout.addWidget(self.playlist_tracks_table, 2)
            self._refresh_playlists()

        elif name == "Favorites":
            favorites_actions = QHBoxLayout()
            add_favorite_button = QPushButton("Add Tracks")
            add_favorite_button.clicked.connect(self._add_tracks_to_favorites)
            remove_favorite_button = QPushButton("Remove Selected")
            remove_favorite_button.clicked.connect(self._remove_selected_favorites)
            favorites_actions.addWidget(add_favorite_button)
            favorites_actions.addWidget(remove_favorite_button)
            favorites_actions.addStretch(1)
            layout.addLayout(favorites_actions)
            self.favorites_table = QTableWidget(0, 4)
            self.favorites_table.setHorizontalHeaderLabels(
                ["Track", "Artist", "Album", "Duration"]
            )
            self.favorites_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.favorites_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.favorites_table.cellDoubleClicked.connect(self._play_favorite_track)
            layout.addWidget(self.favorites_table, 2)
            collection_actions = QHBoxLayout()
            for label, callback in (
                ("New Collection", self._create_favorite_collection),
                ("Rename", self._rename_favorite_collection),
                ("Delete", self._delete_favorite_collection),
                ("Add Tracks", self._add_tracks_to_favorite_collection),
            ):
                button = QPushButton(label)
                button.clicked.connect(callback)
                collection_actions.addWidget(button)
            collection_actions.addStretch(1)
            layout.addLayout(collection_actions)
            self.favorite_collections_list = QListWidget()
            self.favorite_collections_list.currentItemChanged.connect(
                self._refresh_favorite_collection_tracks
            )
            layout.addWidget(self.favorite_collections_list, 1)
            self.favorite_collection_tracks_table = QTableWidget(0, 4)
            self.favorite_collection_tracks_table.setHorizontalHeaderLabels(
                ["Track", "Artist", "Album", "Duration"]
            )
            self.favorite_collection_tracks_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.favorite_collection_tracks_table.setSelectionBehavior(
                QTableWidget.SelectionBehavior.SelectRows
            )
            self.favorite_collection_tracks_table.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )
            self.favorite_collection_tracks_table.customContextMenuRequested.connect(
                self._favorite_collection_track_menu
            )
            self.favorite_collection_tracks_table.cellDoubleClicked.connect(
                self._play_favorite_collection_track
            )
            layout.addWidget(self.favorite_collection_tracks_table, 2)
            self._refresh_favorites()
            self._refresh_favorite_collections()

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
        player.setFixedHeight(86)
        row = QHBoxLayout(player)
        row.setContentsMargins(18, 8, 18, 8)

        self.player_track_label = QLabel("Nothing playing")
        self.player_track_label.setObjectName("playerTrack")
        self.player_track_label.setMinimumWidth(180)
        row.addWidget(self.player_track_label, 2)

        previous_button = QPushButton("Previous")
        previous_button.clicked.connect(self._previous_track)
        row.addWidget(previous_button)
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self._toggle_playback)
        row.addWidget(self.play_button)
        next_button = QPushButton("Next")
        next_button.clicked.connect(self._next_track)
        row.addWidget(next_button)

        self.position_label = QLabel("0:00")
        self.position_label.setObjectName("muted")
        row.addWidget(self.position_label)
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderPressed.connect(self._slider_pressed)
        self.position_slider.sliderReleased.connect(self._slider_released)
        row.addWidget(self.position_slider, 3)
        self.duration_label = QLabel("0:00")
        self.duration_label.setObjectName("muted")
        row.addWidget(self.duration_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(110)
        self.volume_slider.valueChanged.connect(
            lambda value: self.audio_output.setVolume(value / 100)
        )
        self.volume_slider.setToolTip("Volume")
        row.addWidget(self.volume_slider)
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
        enabled = [
            source for source in ("youtube", "spotify", "soundcloud")
            if get_setting(f"source_enabled:{source}", "false") == "true"
        ]
        if not enabled:
            self.search_status.setText("No sources enabled. Open Search Sources to enable one.")
            return
        self.search_status.setText(
            "Online source adapters are not connected in this build. Local Music is available."
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
        self._tracks = list_tracks()
        self.track_table.setRowCount(len(self._tracks))
        for row, track in enumerate(self._tracks):
            values = [
                track["title"],
                track["artist"],
                track["album"],
                self._format_duration(track["duration"]),
                "Local Music",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, track["path"])
                    if not track["scan_error"]:
                        artwork = read_cover_art(track["path"])
                        if artwork:
                            pixmap = QPixmap()
                            if pixmap.loadFromData(artwork):
                                item.setIcon(QIcon(pixmap.scaled(
                                    32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation,
                                )))
                    if track["scan_error"]:
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
        self.scan_status.setText(f"Library updated · {count} audio files found.")
        self._refresh_tracks()
        self._scan_thread = None

    def _scan_failed(self, message: str) -> None:
        self.scan_button.setEnabled(True)
        self.scan_status.setText("Scan failed: " + message)
        self._scan_thread = None

    def _add_folder(self) -> None:
        dialog = QFileDialog(self, "Select a music folder")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setLabelText(QFileDialog.DialogLabel.Accept, "Confirm")
        if not dialog.exec():
            return
        selected = dialog.selectedFiles()
        if not selected:
            return
        folder = Path(selected[0])
        if not folder.is_dir():
            QMessageBox.warning(self, "Invalid folder", "The selected folder is not available.")
            return
        if add_library_folder(folder):
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

    def _selected_track(self) -> dict | None:
        row = self.track_table.currentRow()
        if row < 0:
            return None
        item = self.track_table.item(row, 0)
        if item is None:
            return None
        path = item.data(Qt.ItemDataRole.UserRole)
        return next((track for track in self._tracks if track["path"] == path), None)

    def _play_selected_track(self, _row: int = -1, _column: int = -1) -> None:
        track = self._selected_track()
        if track is not None:
            self._play_track(track)

    def _play_track(self, track: dict) -> None:
        path = Path(track["path"])
        if not path.is_file():
            QMessageBox.warning(self, "Track unavailable", "The audio file no longer exists.")
            self._start_scan()
            return
        self._current_track_path = str(path)
        self.player_track_label.setText(
            f"{track['title']}  ·  {track['artist'] or 'Unknown artist'}"
        )
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.player.play()

    def _toggle_playback(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        elif self._current_track_path:
            self.player.play()
        else:
            self._play_selected_track()

    def _track_paths(self) -> list[dict]:
        return [
            track for track in self._tracks
            if not track["scan_error"] and Path(track["path"]).is_file()
        ]

    def _step_track(self, direction: int) -> None:
        tracks = self._track_paths()
        if not tracks:
            return
        current = next(
            (index for index, track in enumerate(tracks)
             if track["path"] == self._current_track_path),
            -1,
        )
        next_index = (current + direction) % len(tracks)
        self._play_track(tracks[next_index])

    def _previous_track(self) -> None:
        if self.player.position() > 3000:
            self.player.setPosition(0)
        else:
            self._step_track(-1)

    def _next_track(self) -> None:
        self._step_track(1)

    def _media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._next_track()

    def _playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        self.play_button.setText(
            "Pause" if state == QMediaPlayer.PlaybackState.PlayingState else "Play"
        )

    def _position_changed(self, position: int) -> None:
        if not self._slider_is_pressed:
            self.position_slider.setValue(position)
        self.position_label.setText(self._format_duration(position / 1000))

    def _duration_changed(self, duration: int) -> None:
        self.position_slider.setRange(0, duration)
        self.duration_label.setText(self._format_duration(duration / 1000))

    def _slider_pressed(self) -> None:
        self._slider_is_pressed = True

    def _slider_released(self) -> None:
        self._slider_is_pressed = False
        self.player.setPosition(self.position_slider.value())

    def _track_context_menu(self, position) -> None:
        item = self.track_table.itemAt(position)
        if item is None:
            return
        selected_rows = {
            index.row() for index in self.track_table.selectionModel().selectedRows()
        }
        if item.row() not in selected_rows:
            self.track_table.setCurrentCell(item.row(), 0)
            selected_rows = {item.row()}
        selected_tracks = []
        for row in selected_rows:
            cell = self.track_table.item(row, 0)
            if cell is None:
                continue
            path = cell.data(Qt.ItemDataRole.UserRole)
            match = next((track for track in self._tracks if track["path"] == path), None)
            if match is not None:
                selected_tracks.append(match)
        if not selected_tracks:
            return
        menu = QMenu(self)
        play_action = menu.addAction("Play")
        details_action = menu.addAction("View Track Details")
        menu.addSeparator()
        edit_label = "Edit Metadata" if len(selected_tracks) == 1 else "Edit Metadata for Selected"
        edit_action = menu.addAction(edit_label)
        menu.addSeparator()
        add_favorite_action = menu.addAction("Add to Favorites")
        playlist_menu = menu.addMenu("Add to Playlist")
        playlist_actions = {
            playlist_menu.addAction(item["name"]): item["id"]
            for item in list_playlists()
        }
        retry_action = None
        if any(track["scan_error"] for track in selected_tracks):
            retry_action = menu.addAction("Retry")
        chosen = menu.exec(self.track_table.viewport().mapToGlobal(position))
        if chosen == play_action:
            self._play_track(selected_tracks[0])
        elif chosen == details_action:
            self._show_track_details(selected_tracks[0])
        elif chosen == edit_action:
            self._edit_track_metadata(selected_tracks)
        elif chosen == add_favorite_action:
            add_favorites([track["path"] for track in selected_tracks])
        elif chosen in playlist_actions:
            add_tracks_to_playlist(
                playlist_actions[chosen], [track["path"] for track in selected_tracks]
            )
        elif retry_action is not None and chosen == retry_action:
            self._start_scan()


    def _edit_track_metadata(self, tracks: list[dict]) -> None:
        if not tracks:
            return
        bulk = len(tracks) > 1
        dialog = QDialog(self)
        dialog.setWindowTitle(
            "Edit Track Metadata" if not bulk else f"Edit Metadata · {len(tracks)} tracks"
        )
        form = QFormLayout(dialog)
        fields = {
            "title": "Title", "artist": "Artist", "album": "Album",
            "track_number": "Track number", "year": "Year", "genre": "Genre",
        }
        inputs: dict[str, QLineEdit] = {}
        for key, label in fields.items():
            field = QLineEdit()
            if bulk:
                field.setPlaceholderText("Leave blank to keep unchanged")
            else:
                field.setText(str(tracks[0].get(key) or ""))
            form.addRow(label, field)
            inputs[key] = field
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        updates = {
            key: field.text() for key, field in inputs.items()
            if not bulk or field.text().strip()
        }
        if not updates:
            return
        failures: list[str] = []
        for track in tracks:
            try:
                update_track_metadata(track["path"], updates)
            except (OSError, ValueError) as error:
                failures.append(f"{Path(track['path']).name}: {error}")
        scan_library()
        self._refresh_tracks()
        if failures:
            QMessageBox.warning(
                self, "Some metadata could not be saved", "\\n".join(failures)
            )
        else:
            QMessageBox.information(self, "Metadata saved", "Track metadata was updated.")


    def _selected_list_id(self, widget: QListWidget) -> int | None:
        item = widget.currentItem()
        return int(item.data(Qt.ItemDataRole.UserRole)) if item else None

    def _create_playlist(self) -> None:
        name, accepted = QInputDialog.getText(self, "New Playlist", "Playlist name:")
        if accepted:
            try:
                created = create_playlist(name)
            except ValueError as error:
                QMessageBox.warning(self, "Invalid name", str(error))
                return
            if not created:
                QMessageBox.warning(self, "Duplicate name", "A playlist with that name already exists.")
            else:
                self._refresh_playlists()

    def _rename_playlist(self) -> None:
        item_id = self._selected_list_id(self.playlist_list)
        item = self.playlist_list.currentItem()
        if item_id is None or item is None:
            return
        name, accepted = QInputDialog.getText(
            self, "Rename Playlist", "Playlist name:", text=item.text().split(" (")[0]
        )
        if accepted:
            try:
                renamed = rename_playlist(item_id, name)
            except ValueError as error:
                QMessageBox.warning(self, "Invalid name", str(error))
                return
            if not renamed:
                QMessageBox.warning(self, "Duplicate name", "A playlist with that name already exists.")
            else:
                self._refresh_playlists(item_id)

    def _delete_playlist(self) -> None:
        item_id = self._selected_list_id(self.playlist_list)
        if item_id is None:
            return
        answer = QMessageBox.question(
            self, "Delete Playlist", "Delete this playlist? Local music files will not be deleted."
        )
        if answer == QMessageBox.StandardButton.Yes:
            delete_playlist(item_id)
            self._refresh_playlists()

    def _refresh_playlists(self, selected_id: int | None = None) -> None:
        if not hasattr(self, "playlist_list"):
            return
        self.playlist_list.clear()
        selected_item = None
        for playlist in list_playlists():
            item = QListWidgetItem(
                f"{playlist['name']} ({playlist['track_count']})"
            )
            item.setData(Qt.ItemDataRole.UserRole, playlist["id"])
            self.playlist_list.addItem(item)
            if playlist["id"] == selected_id:
                selected_item = item
        if selected_item is not None:
            self.playlist_list.setCurrentItem(selected_item)
        elif self.playlist_list.count():
            self.playlist_list.setCurrentRow(0)
        else:
            self.playlist_tracks_table.setRowCount(0)

    def _refresh_playlist_tracks(self, current=None, _previous=None) -> None:
        if not hasattr(self, "playlist_tracks_table"):
            return
        item_id = int(current.data(Qt.ItemDataRole.UserRole)) if current else None
        tracks = list_playlist_tracks(item_id) if item_id is not None else []
        self._fill_track_table(self.playlist_tracks_table, tracks)

    def _add_tracks_to_playlist(self) -> None:
        playlist_id = self._selected_list_id(self.playlist_list)
        if playlist_id is None:
            QMessageBox.information(self, "Select a Playlist", "Create or select a playlist first.")
            return
        paths = self._pick_track_paths()
        if paths:
            add_tracks_to_playlist(playlist_id, paths)
            self._refresh_playlists(playlist_id)

    def _playlist_track_menu(self, position) -> None:
        row = self.playlist_tracks_table.rowAt(position.y())
        if row < 0:
            return
        path = self.playlist_tracks_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        item_id = self._selected_list_id(self.playlist_list)
        if item_id is None:
            return
        menu = QMenu(self)
        remove_action = menu.addAction("Remove from Playlist")
        chosen = menu.exec(self.playlist_tracks_table.viewport().mapToGlobal(position))
        if chosen == remove_action:
            remove_track_from_playlist(item_id, path)
            self._refresh_playlists(item_id)

    def _play_playlist_track(self, row: int, _column: int) -> None:
        item = self.playlist_tracks_table.item(row, 0)
        if item is not None:
            path = item.data(Qt.ItemDataRole.UserRole)
            track = next((entry for entry in self._tracks if entry["path"] == path), None)
            if track:
                self._play_track(track)

    def _refresh_favorites(self) -> None:
        if not hasattr(self, "favorites_table"):
            return
        self._fill_track_table(self.favorites_table, list_favorites())

    def _add_tracks_to_favorites(self) -> None:
        paths = self._pick_track_paths()
        if paths:
            add_favorites(paths)
            self._refresh_favorites()

    def _remove_selected_favorites(self) -> None:
        paths = self._selected_table_paths(self.favorites_table)
        for path in paths:
            remove_favorite(path)
        self._refresh_favorites()

    def _refresh_favorite_collections(self, selected_id: int | None = None) -> None:
        if not hasattr(self, "favorite_collections_list"):
            return
        self.favorite_collections_list.clear()
        selected_item = None
        for collection in list_favorite_collections():
            item = QListWidgetItem(
                f"{collection['name']} ({collection['track_count']})"
            )
            item.setData(Qt.ItemDataRole.UserRole, collection["id"])
            self.favorite_collections_list.addItem(item)
            if collection["id"] == selected_id:
                selected_item = item
        if selected_item is not None:
            self.favorite_collections_list.setCurrentItem(selected_item)
        elif self.favorite_collections_list.count():
            self.favorite_collections_list.setCurrentRow(0)
        else:
            self.favorite_collection_tracks_table.setRowCount(0)

    def _refresh_favorite_collection_tracks(self, current=None, _previous=None) -> None:
        if not hasattr(self, "favorite_collection_tracks_table"):
            return
        item_id = int(current.data(Qt.ItemDataRole.UserRole)) if current else None
        tracks = list_favorite_collection_tracks(item_id) if item_id is not None else []
        self._fill_track_table(self.favorite_collection_tracks_table, tracks)

    def _create_favorite_collection(self) -> None:
        name, accepted = QInputDialog.getText(
            self, "New Favorites Collection", "Collection name:"
        )
        if accepted:
            try:
                created = create_favorite_collection(name)
            except ValueError as error:
                QMessageBox.warning(self, "Invalid name", str(error))
                return
            if not created:
                QMessageBox.warning(
                    self, "Duplicate name", "A Favorites collection with that name already exists."
                )
            else:
                self._refresh_favorite_collections()

    def _rename_favorite_collection(self) -> None:
        item_id = self._selected_list_id(self.favorite_collections_list)
        item = self.favorite_collections_list.currentItem()
        if item_id is None or item is None:
            return
        name, accepted = QInputDialog.getText(
            self, "Rename Collection", "Collection name:",
            text=item.text().split(" (")[0],
        )
        if accepted:
            try:
                renamed = rename_favorite_collection(item_id, name)
            except ValueError as error:
                QMessageBox.warning(self, "Invalid name", str(error))
                return
            if not renamed:
                QMessageBox.warning(
                    self, "Duplicate name", "A Favorites collection with that name already exists."
                )
            else:
                self._refresh_favorite_collections(item_id)

    def _delete_favorite_collection(self) -> None:
        item_id = self._selected_list_id(self.favorite_collections_list)
        if item_id is None:
            return
        answer = QMessageBox.question(
            self, "Delete Collection",
            "Delete this Favorites collection? Tracks and local files will remain.",
        )
        if answer == QMessageBox.StandardButton.Yes:
            delete_favorite_collection(item_id)
            self._refresh_favorite_collections()

    def _add_tracks_to_favorite_collection(self) -> None:
        collection_id = self._selected_list_id(self.favorite_collections_list)
        if collection_id is None:
            QMessageBox.information(
                self, "Select a Collection", "Create or select a Favorites collection first."
            )
            return
        paths = self._pick_track_paths()
        if paths:
            add_tracks_to_favorite_collection(collection_id, paths)
            self._refresh_favorite_collections(collection_id)

    def _favorite_collection_track_menu(self, position) -> None:
        row = self.favorite_collection_tracks_table.rowAt(position.y())
        if row < 0:
            return
        path = self.favorite_collection_tracks_table.item(row, 0).data(
            Qt.ItemDataRole.UserRole
        )
        collection_id = self._selected_list_id(self.favorite_collections_list)
        if collection_id is None:
            return
        menu = QMenu(self)
        remove_action = menu.addAction("Remove from Collection")
        chosen = menu.exec(
            self.favorite_collection_tracks_table.viewport().mapToGlobal(position)
        )
        if chosen == remove_action:
            remove_track_from_favorite_collection(collection_id, path)
            self._refresh_favorite_collections(collection_id)

    def _play_favorite_track(self, row: int, _column: int) -> None:
        self._play_table_track(self.favorites_table, row)

    def _play_favorite_collection_track(self, row: int, _column: int) -> None:
        self._play_table_track(self.favorite_collection_tracks_table, row)

    def _play_table_track(self, table: QTableWidget, row: int) -> None:
        item = table.item(row, 0)
        if item is not None:
            path = item.data(Qt.ItemDataRole.UserRole)
            track = next((entry for entry in self._tracks if entry["path"] == path), None)
            if track:
                self._play_track(track)

    def _pick_track_paths(self) -> list[str]:
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Tracks")
        layout = QVBoxLayout(dialog)
        listing = QListWidget()
        for track in self._tracks:
            if track["scan_error"]:
                continue
            item = QListWidgetItem(
                f"{track['title']} — {track['artist'] or 'Unknown artist'}"
            )
            item.setData(Qt.ItemDataRole.UserRole, track["path"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            listing.addItem(item)
        layout.addWidget(listing)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return []
        return [
            str(listing.item(index).data(Qt.ItemDataRole.UserRole))
            for index in range(listing.count())
            if listing.item(index).checkState() == Qt.CheckState.Checked
        ]

    @staticmethod
    def _fill_track_table(table: QTableWidget, tracks: list[dict]) -> None:
        table.setRowCount(len(tracks))
        for row, track in enumerate(tracks):
            values = [
                track["title"], track["artist"], track["album"],
                MainWindow._format_duration(track["duration"]),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, track["path"])
                table.setItem(row, column, item)

    @staticmethod
    def _selected_table_paths(table: QTableWidget) -> list[str]:
        return [
            str(table.item(row, 0).data(Qt.ItemDataRole.UserRole))
            for row in sorted({index.row() for index in table.selectionModel().selectedRows()})
            if table.item(row, 0) is not None
        ]

    def _show_track_details(self, track: dict) -> None:
        details = (
            f"Track: {track['title']}\n"
            f"Artist: {track['artist'] or '—'}\n"
            f"Album: {track['album'] or '—'}\n"
            f"Duration: {self._format_duration(track['duration'])}\n"
            f"Format: {track['file_format']}\n"
            f"Location: {track['path']}"
        )
        if track["scan_error"]:
            details += f"\n\nError: {track['scan_error']}"
        QMessageBox.information(self, "Track Details", details)

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
