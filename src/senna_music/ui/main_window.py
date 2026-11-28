from __future__ import annotations

import json
import random
import shutil
import threading
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import keyring
from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QIcon, QPalette, QPixmap, QTextCursor
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
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
    QPlainTextEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
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
    reorder_favorite_collection_tracks,
    reorder_favorites,
    reorder_playlist_tracks,
)
from senna_music.core.downloads import DownloadCancelled, download_audio
from senna_music.core.lyrics import LyricsProviderError, LyricsResult, fetch_lyrics, parse_lrc
from senna_music.core.metadata import read_cover_art, update_track_metadata
from senna_music.core.scanner import scan_library
from senna_music.core.search import SearchResult, search_source
from senna_music.core.storage import (
    add_download_task,
    add_library_folder,
    clear_finished_download_tasks,
    delete_download_task,
    get_next_download_task,
    get_setting,
    list_download_tasks,
    list_library_folders,
    list_tracks,
    remove_library_folder,
    retry_download_task,
    set_setting,
    update_download_task,
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
KEYRING_SERVICE = "Senna Music"
SEARCH_HISTORY_LIMIT = 20


class SearchWorker(QThread):
    results_ready = Signal(str, object)
    source_failed = Signal(str, str)

    def __init__(
        self,
        query: str,
        sources: list[str],
        spotify_client_id: str,
        spotify_client_secret: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.query = query
        self.sources = sources
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret

    def run(self) -> None:
        executor = ThreadPoolExecutor(max_workers=max(1, len(self.sources)))
        futures = {
            executor.submit(
                search_source,
                source,
                self.query,
                10,
                self.spotify_client_id,
                self.spotify_client_secret,
            ): source
            for source in self.sources
        }
        try:
            for future in as_completed(futures, timeout=30):
                source = futures[future]
                try:
                    self.results_ready.emit(source, future.result())
                except Exception as error:  # noqa: BLE001
                    self.source_failed.emit(source, str(error))
        except TimeoutError:
            for future, source in futures.items():
                if not future.done():
                    future.cancel()
                    self.source_failed.emit(source, "Search timed out after 30 seconds.")
        finally:
            executor.shutdown(wait=False, cancel_futures=True)




class LyricsWorker(QThread):
    completed = Signal(str, str, object)
    failed = Signal(str, str, str)

    def __init__(self, track: dict, language: str, parent=None) -> None:
        super().__init__(parent)
        self.track = track
        self.language = language

    def run(self) -> None:
        try:
            result = fetch_lyrics(
                self.track["title"],
                self.track["artist"],
                self.track["album"],
                self.track["duration"],
                self.language,
            )
            self.completed.emit(self.track["path"], self.language, result)
        except (LyricsProviderError, OSError, ValueError) as error:
            self.failed.emit(self.track["path"], self.language, str(error))


class DownloadQueueWorker(QThread):
    progress_changed = Signal(int, float)
    task_changed = Signal(int)
    queue_finished = Signal()

    def __init__(self, ffmpeg_location: str = "", parent=None) -> None:
        super().__init__(parent)
        self.ffmpeg_location = ffmpeg_location
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.stop_event = threading.Event()
        self.active_task_id: int | None = None

    def pause(self) -> None:
        self.pause_event.clear()
        if self.active_task_id is not None:
            update_download_task(self.active_task_id, status="paused")
            self.task_changed.emit(self.active_task_id)

    def resume(self) -> None:
        self.pause_event.set()
        if self.active_task_id is not None:
            update_download_task(self.active_task_id, status="downloading")
            self.task_changed.emit(self.active_task_id)

    def cancel_current(self) -> None:
        self.cancel_event.set()
        self.pause_event.set()

    def stop_after_current(self) -> None:
        self.stop_event.set()
        self.cancel_current()
        self.resume()

    def _progress(self, task_id: int, percent: float) -> None:
        update_download_task(task_id, progress=percent)
        self.progress_changed.emit(task_id, percent)

    def run(self) -> None:
        while not self.stop_event.is_set():
            self.pause_event.wait()
            if self.stop_event.is_set():
                break
            task = get_next_download_task()
            if task is None:
                break
            task_id = int(task["id"])
            self.active_task_id = task_id
            update_download_task(task_id, status="downloading", error="")
            self.task_changed.emit(task_id)
            try:
                result = download_audio(
                    task,
                    task["destination_root"],
                    progress_callback=lambda value, current_task_id=task_id: self._progress(current_task_id, value),
                    cancel_event=self.cancel_event,
                    pause_event=self.pause_event,
                    ffmpeg_location=self.ffmpeg_location,
                )
                update_download_task(
                    task_id,
                    status=result["status"],
                    progress=100 if result["status"] in {"completed", "skipped"} else 0,
                    destination_path=result.get("path", ""),
                    error=result.get("message", ""),
                )
            except DownloadCancelled as error:
                update_download_task(task_id, status="cancelled", error=str(error))
            except Exception as error:  # noqa: BLE001 - record task failures for the queue UI
                update_download_task(task_id, status="failed", error=str(error))
            finally:
                self.cancel_event.clear()
                self.active_task_id = None
                self.task_changed.emit(task_id)
            if self.stop_event.is_set():
                break
        self.queue_finished.emit()


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
        self._search_worker: SearchWorker | None = None
        self._download_worker: DownloadQueueWorker | None = None
        self._playback_queue: list[str] = []
        self._current_queue_index = -1
        self._shuffle_enabled = False
        self._repeat_mode = "off"
        self._local_view = "All Tracks"
        self._local_filter: dict[str, str] = {}
        self._lyrics_workers: list[LyricsWorker] = []
        self._current_lyrics_path: str | None = None
        self._current_lyrics_result: LyricsResult | None = None
        self._lyrics_lines: list[tuple[int, str]] = []
        self._restore_position_ms: int | None = None
        self._expanded_player_dialog: QDialog | None = None

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)
        self.player.positionChanged.connect(self._position_changed)
        self.player.durationChanged.connect(self._duration_changed)
        self.player.playbackStateChanged.connect(self._playback_state_changed)
        self.player.mediaStatusChanged.connect(self._media_status_changed)

        self._build_ui()
        self._restore_playback_state()
        self._show_page("Home")
        self._start_scan()
        self._state_save_timer = QTimer(self)
        self._state_save_timer.setInterval(10_000)
        self._state_save_timer.timeout.connect(self._save_playback_state)
        self._state_save_timer.start()

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
            self.search_button = QPushButton("Search")
            self.search_button.setMinimumHeight(44)
            self.search_button.clicked.connect(self._search)
            search_row.addWidget(self.search_input, 1)
            search_row.addWidget(self.search_button)
            layout.addLayout(search_row)

            history_row = QHBoxLayout()
            history_row.addWidget(QLabel("Recent searches"))
            self.search_history_combo = QComboBox()
            self.search_history_combo.addItem("Choose a recent search")
            self.search_history_combo.activated.connect(self._select_search_history)
            history_row.addWidget(self.search_history_combo, 1)
            clear_history_button = QPushButton("Clear History")
            clear_history_button.clicked.connect(self._clear_search_history)
            history_row.addWidget(clear_history_button)
            layout.addLayout(history_row)

            filter_row = QHBoxLayout()
            filter_row.addWidget(QLabel("Filter"))
            self.search_filter = QComboBox()
            self.search_filter.addItems(
                ["All Sources", "Local Music", "YouTube", "Spotify", "SoundCloud"]
            )
            self.search_filter.currentTextChanged.connect(self._apply_search_filter)
            filter_row.addWidget(self.search_filter)
            filter_row.addStretch(1)
            layout.addLayout(filter_row)

            self.search_status = QLabel(
                "Enable one or more sources on Search Sources to start online discovery."
            )
            self.search_status.setObjectName("muted")
            layout.addWidget(self.search_status)
            self.search_results_table = QTableWidget(0, 5)
            self.search_results_table.setHorizontalHeaderLabels(
                ["Track", "Artist", "Album", "Duration", "Source"]
            )
            self.search_results_table.setSelectionBehavior(
                QTableWidget.SelectionBehavior.SelectRows
            )
            self.search_results_table.setEditTriggers(
                QTableWidget.EditTrigger.NoEditTriggers
            )
            self.search_results_table.verticalHeader().setVisible(False)
            self.search_results_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.search_results_table.setSortingEnabled(True)
            self.search_results_table.setSelectionMode(
                QTableWidget.SelectionMode.ExtendedSelection
            )
            self.search_results_table.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )
            self.search_results_table.customContextMenuRequested.connect(
                self._search_result_menu
            )
            self.search_results_table.cellDoubleClicked.connect(self._open_search_result)
            layout.addWidget(self.search_results_table, 2)
            self._refresh_search_history()
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

            view_row = QHBoxLayout()
            view_row.addWidget(QLabel("View"))
            self.local_view_combo = QComboBox()
            self.local_view_combo.addItems(["All Tracks", "Artists", "Albums", "Folders"])
            self.local_view_combo.currentTextChanged.connect(self._set_local_view)
            view_row.addWidget(self.local_view_combo)
            self.local_filter_label = QLabel("All tracks")
            self.local_filter_label.setObjectName("muted")
            view_row.addWidget(self.local_filter_label, 1)
            clear_filter_button = QPushButton("Clear Filter")
            clear_filter_button.clicked.connect(self._clear_local_filter)
            view_row.addWidget(clear_filter_button)
            layout.addLayout(view_row)

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
            self.track_table.cellDoubleClicked.connect(self._activate_local_view_row)
            layout.addWidget(self.track_table, 1)

            remove_button = QPushButton("Remove Selected Folder")
            remove_button.clicked.connect(self._remove_folder)
            layout.addWidget(remove_button, 0, Qt.AlignmentFlag.AlignLeft)
            self._refresh_folders()
            self._refresh_tracks()


        elif name == "Download Queue":
            actions = QHBoxLayout()
            controls = (
                ("Start Queue", self._start_download_queue),
                ("Pause", self._pause_download_queue),
                ("Resume", self._resume_download_queue),
                ("Cancel Current", self._cancel_current_download),
                ("Retry Selected", self._retry_selected_downloads),
                ("Remove Selected", self._remove_selected_downloads),
                ("Clear Finished", self._clear_finished_downloads),
            )
            for label, callback in controls:
                button = QPushButton(label)
                button.clicked.connect(callback)
                actions.addWidget(button)
            layout.addLayout(actions)
            self.download_status = QLabel("Downloads are stored in the folder selected in Settings.")
            self.download_status.setObjectName("muted")
            layout.addWidget(self.download_status)
            self.download_table = QTableWidget(0, 7)
            self.download_table.setHorizontalHeaderLabels(
                ["Track", "Artist", "Album", "Format", "Status", "Progress", "Source"]
            )
            self.download_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.download_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
            self.download_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.download_table.verticalHeader().setVisible(False)
            self.download_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            layout.addWidget(self.download_table, 1)
            self._refresh_download_queue()

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

            spotify_label = QLabel("Spotify Developer credentials (for public track metadata)")
            spotify_label.setObjectName("muted")
            layout.addWidget(spotify_label)
            self.spotify_client_id_input = QLineEdit(
                keyring.get_password(KEYRING_SERVICE, "spotify_client_id") or ""
            )
            self.spotify_client_id_input.setPlaceholderText("Spotify Client ID")
            layout.addWidget(self.spotify_client_id_input)
            self.spotify_client_secret_input = QLineEdit(
                keyring.get_password(KEYRING_SERVICE, "spotify_client_secret") or ""
            )
            self.spotify_client_secret_input.setPlaceholderText("Spotify Client Secret")
            self.spotify_client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
            layout.addWidget(self.spotify_client_secret_input)
            save_credentials = QPushButton("Save Spotify Credentials")
            save_credentials.clicked.connect(self._save_spotify_credentials)
            layout.addWidget(save_credentials)
            credentials_help = QLabel(
                "Create an app in the Spotify Developer Dashboard. Credentials are stored "
                "in the Windows credential store, not in the Senna Music database."
            )
            credentials_help.setObjectName("muted")
            credentials_help.setWordWrap(True)
            layout.addWidget(credentials_help)

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
            self.playlist_tracks_table.setSelectionMode(
                QTableWidget.SelectionMode.ExtendedSelection
            )
            self.playlist_tracks_table.setDragDropMode(
                QAbstractItemView.DragDropMode.InternalMove
            )
            self.playlist_tracks_table.setDragDropOverwriteMode(False)
            self.playlist_tracks_table.model().rowsMoved.connect(
                self._playlist_tracks_reordered
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
            self.favorites_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
            self.favorites_table.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
            self.favorites_table.setDragDropOverwriteMode(False)
            self.favorites_table.model().rowsMoved.connect(self._favorites_reordered)
            self.favorites_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.favorites_table.customContextMenuRequested.connect(
                self._favorites_track_menu
            )
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
            self.favorite_collection_tracks_table.setSelectionMode(
                QTableWidget.SelectionMode.ExtendedSelection
            )
            self.favorite_collection_tracks_table.setDragDropMode(
                QAbstractItemView.DragDropMode.InternalMove
            )
            self.favorite_collection_tracks_table.setDragDropOverwriteMode(False)
            self.favorite_collection_tracks_table.model().rowsMoved.connect(
                self._favorite_collection_tracks_reordered
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
            layout.addWidget(QLabel("Download destination"))
            destination_row = QHBoxLayout()
            self.download_folder_input = QLineEdit(get_setting("download_folder", ""))
            self.download_folder_input.setPlaceholderText("Choose where downloaded music is stored")
            destination_row.addWidget(self.download_folder_input, 1)
            browse_destination = QPushButton("Browse")
            browse_destination.clicked.connect(self._select_download_folder)
            destination_row.addWidget(browse_destination)
            layout.addLayout(destination_row)

            layout.addWidget(QLabel("Default download format"))
            self.download_format_combo = QComboBox()
            self.download_format_combo.addItems(["original", "mp3", "m4a", "flac"])
            current_format = get_setting("download_format", "original")
            self.download_format_combo.setCurrentText(current_format)
            layout.addWidget(self.download_format_combo)

            layout.addWidget(QLabel("Default audio quality"))
            self.download_quality_combo = QComboBox()
            self.download_quality_combo.addItems(["128", "192", "256", "320"])
            self.download_quality_combo.setCurrentText(get_setting("download_quality", "192"))
            layout.addWidget(self.download_quality_combo)

            layout.addWidget(QLabel("Preferred lyrics language"))
            self.lyrics_language_settings_combo = QComboBox()
            self.lyrics_language_settings_combo.addItems([
                "Auto", "English", "Bosnian", "Croatian", "Serbian",
                "French", "German", "Dutch", "Spanish", "Italian",
            ])
            self.lyrics_language_settings_combo.setCurrentText(
                self._lyrics_language_label(get_setting("lyrics_language", "auto"))
            )
            layout.addWidget(self.lyrics_language_settings_combo)

            layout.addWidget(QLabel("FFmpeg executable or folder (optional)"))
            ffmpeg_row = QHBoxLayout()
            self.ffmpeg_path_input = QLineEdit(get_setting("ffmpeg_location", ""))
            self.ffmpeg_path_input.setPlaceholderText(
                shutil.which("ffmpeg") or "FFmpeg is not on PATH"
            )
            ffmpeg_row.addWidget(self.ffmpeg_path_input, 1)
            browse_ffmpeg = QPushButton("Browse")
            browse_ffmpeg.clicked.connect(self._select_ffmpeg)
            ffmpeg_row.addWidget(browse_ffmpeg)
            layout.addLayout(ffmpeg_row)

            ffmpeg_status = QLabel(
                "FFmpeg detected on PATH." if shutil.which("ffmpeg")
                else "FFmpeg is required for MP3/M4A/FLAC conversion. Set its executable or folder."
            )
            ffmpeg_status.setObjectName("muted")
            ffmpeg_status.setWordWrap(True)
            layout.addWidget(ffmpeg_status)
            save_settings = QPushButton("Save Settings")
            save_settings.clicked.connect(self._save_download_settings)
            layout.addWidget(save_settings)
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
        player.setFixedHeight(94)
        row = QHBoxLayout(player)
        row.setContentsMargins(18, 8, 18, 8)

        self.player_art_label = QLabel()
        self.player_art_label.setFixedSize(58, 58)
        self.player_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(self.player_art_label)

        self.player_track_label = QLabel("Nothing playing")
        self.player_track_label.setObjectName("playerTrack")
        self.player_track_label.setMinimumWidth(180)
        self.player_track_label.setWordWrap(True)
        row.addWidget(self.player_track_label, 2)

        self.player_favorite_button = QPushButton("♡")
        self.player_favorite_button.setToolTip("Add or remove Favorite")
        self.player_favorite_button.clicked.connect(self._toggle_current_favorite)
        row.addWidget(self.player_favorite_button)

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
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(
            lambda value: self.audio_output.setVolume(value / 100)
        )
        self.volume_slider.setToolTip("Volume")
        row.addWidget(self.volume_slider)

        expand_button = QPushButton("Expand")
        expand_button.setToolTip("Open expanded player")
        expand_button.clicked.connect(self._open_expanded_player)
        row.addWidget(expand_button)
        return player

    def _show_page(self, name: str) -> None:
        self.stack.setCurrentWidget(self._pages[name])
        for page_name, button in self._nav_buttons.items():
            button.setChecked(page_name == name)


    @staticmethod
    def _normalize_search_text(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value.casefold())
        return "".join(char for char in decomposed if not unicodedata.combining(char)).strip()

    def _remember_search(self, query: str) -> None:
        try:
            history = json.loads(get_setting("search_history", "[]"))
        except (TypeError, ValueError):
            history = []
        history = [item for item in history if item.casefold() != query.casefold()]
        history.insert(0, query)
        set_setting("search_history", json.dumps(history[:SEARCH_HISTORY_LIMIT]))
        self._refresh_search_history()

    def _refresh_search_history(self) -> None:
        if not hasattr(self, "search_history_combo"):
            return
        try:
            history = json.loads(get_setting("search_history", "[]"))
        except (TypeError, ValueError):
            history = []
        self.search_history_combo.blockSignals(True)
        self.search_history_combo.clear()
        self.search_history_combo.addItem("Choose a recent search")
        self.search_history_combo.addItems(history[:SEARCH_HISTORY_LIMIT])
        self.search_history_combo.setCurrentIndex(0)
        self.search_history_combo.blockSignals(False)

    def _select_search_history(self, index: int) -> None:
        if index <= 0:
            return
        self.search_input.setText(self.search_history_combo.itemText(index))
        self._search()

    def _clear_search_history(self) -> None:
        set_setting("search_history", "[]")
        self._refresh_search_history()

    def _save_spotify_credentials(self) -> None:
        client_id = self.spotify_client_id_input.text().strip()
        client_secret = self.spotify_client_secret_input.text().strip()
        if not client_id or not client_secret:
            QMessageBox.warning(
                self, "Missing credentials", "Enter both Spotify Client ID and Client Secret."
            )
            return
        try:
            keyring.set_password(KEYRING_SERVICE, "spotify_client_id", client_id)
            keyring.set_password(KEYRING_SERVICE, "spotify_client_secret", client_secret)
        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(
                self, "Credential storage failed",
                f"Windows credential storage is unavailable: {error}",
            )
            return
        QMessageBox.information(
            self, "Credentials saved", "Spotify app credentials were saved securely."
        )

    def _search(self) -> None:
        query = self.search_input.text().strip()
        if len(query) < 2:
            self.search_status.setText("Enter at least 2 characters to search.")
            return
        if self._search_worker is not None and self._search_worker.isRunning():
            return

        self._remember_search(query)
        self.search_results_table.setRowCount(0)
        normalized_query = self._normalize_search_text(query)
        local_matches = []
        for track in self._tracks:
            searchable = " ".join(
                [track["title"], track["artist"], track["album"]]
            )
            if normalized_query in self._normalize_search_text(searchable):
                local_matches.append(track)
        for track in local_matches:
            self._append_search_row(
                {
                    "source": "Local Music",
                    "title": track["title"],
                    "artist": track["artist"],
                    "album": track["album"],
                    "duration": track["duration"],
                    "local_track": track,
                }
            )

        enabled = [
            source for source in ("YouTube", "Spotify", "SoundCloud")
            if get_setting(f"source_enabled:{source.casefold()}", "false") == "true"
        ]
        if not enabled:
            self.search_status.setText(
                f"{len(local_matches)} local matches. No online sources are enabled."
            )
            self._apply_search_filter(self.search_filter.currentText())
            return

        client_id = keyring.get_password(KEYRING_SERVICE, "spotify_client_id") or ""
        client_secret = keyring.get_password(KEYRING_SERVICE, "spotify_client_secret") or ""
        self.search_status.setText("Searching enabled sources…")
        self.search_button.setEnabled(False)
        self._search_worker = SearchWorker(
            query, enabled, client_id, client_secret, self
        )
        self._search_worker.results_ready.connect(self._on_source_results)
        self._search_worker.source_failed.connect(self._on_source_failed)
        self._search_worker.finished.connect(self._search_completed)
        self._search_worker.start()
        self._apply_search_filter(self.search_filter.currentText())

    def _append_search_row(self, result: dict | SearchResult) -> None:
        self.search_results_table.setSortingEnabled(False)
        row = self.search_results_table.rowCount()
        self.search_results_table.insertRow(row)
        if isinstance(result, SearchResult):
            values = [
                result.title, result.artist, result.album,
                self._format_duration(result.duration), result.source,
            ]
            payload = result
        else:
            values = [
                result["title"], result["artist"], result["album"],
                self._format_duration(result["duration"]), result["source"],
            ]
            payload = result
        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value or ""))
            if column == 0:
                item.setData(Qt.ItemDataRole.UserRole, payload)
            self.search_results_table.setItem(row, column, item)
        self.search_results_table.setSortingEnabled(True)
        self._apply_search_filter(self.search_filter.currentText())

    def _on_source_results(self, _source: str, results: list[SearchResult]) -> None:
        for result in results:
            self._append_search_row(result)

    def _on_source_failed(self, source: str, message: str) -> None:
        self._append_search_row({
            "source": source,
            "title": "Search failed",
            "artist": message,
            "album": "",
            "duration": None,
        })

    def _search_completed(self) -> None:
        self.search_button.setEnabled(True)
        self._search_worker = None
        if self.search_results_table.rowCount() == 0:
            self.search_status.setText("No results found.")
        else:
            self.search_status.setText("Search complete.")
        self._apply_search_filter(self.search_filter.currentText())

    def _apply_search_filter(self, source: str) -> None:
        if not hasattr(self, "search_results_table"):
            return
        for row in range(self.search_results_table.rowCount()):
            source_item = self.search_results_table.item(row, 4)
            row_source = source_item.text() if source_item else ""
            self.search_results_table.setRowHidden(
                row, source != "All Sources" and row_source != source
            )

    def _open_search_result(self, row: int, _column: int) -> None:
        item = self.search_results_table.item(row, 0)
        if item is None:
            return
        result = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(result, dict) and result.get("local_track"):
            self._play_track(result["local_track"])
            return
        if not isinstance(result, SearchResult):
            return
        details = (
            f"{result.title}\\n{result.artist}\\n{result.album}\\n"
            f"Source: {result.source}\\n\\n{result.url}"
        )
        message = QMessageBox(self)
        message.setWindowTitle("Search Result Details")
        message.setText(details)
        open_button = message.addButton("Open Source", QMessageBox.ButtonRole.AcceptRole)
        message.addButton(QMessageBox.StandardButton.Close)
        message.exec()
        if message.clickedButton() == open_button:
            QDesktopServices.openUrl(QUrl(result.url))

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
        self._tracks = list_tracks()
        table = self.track_table
        table.setSortingEnabled(False)

        if self._local_view == "Artists":
            groups: dict[str, int] = {}
            for track in self._tracks:
                artist = track["artist"] or "Unknown Artist"
                groups[artist] = groups.get(artist, 0) + 1
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Artist", "Tracks"])
            rows = sorted(groups.items(), key=lambda item: item[0].casefold())
            table.setRowCount(len(rows))
            for row, (artist, count) in enumerate(rows):
                item = QTableWidgetItem(artist)
                item.setData(Qt.ItemDataRole.UserRole, artist)
                table.setItem(row, 0, item)
                table.setItem(row, 1, QTableWidgetItem(str(count)))

        elif self._local_view == "Albums":
            groups: dict[tuple[str, str], int] = {}
            for track in self._tracks:
                key = (track["album"] or "Singles", track["artist"] or "Unknown Artist")
                groups[key] = groups.get(key, 0) + 1
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Album", "Artist", "Tracks"])
            rows = sorted(groups.items(), key=lambda item: (item[0][1].casefold(), item[0][0].casefold()))
            table.setRowCount(len(rows))
            for row, ((album, artist), count) in enumerate(rows):
                item = QTableWidgetItem(album)
                item.setData(Qt.ItemDataRole.UserRole, (album, artist))
                table.setItem(row, 0, item)
                table.setItem(row, 1, QTableWidgetItem(artist))
                table.setItem(row, 2, QTableWidgetItem(str(count)))

        elif self._local_view == "Folders":
            groups: dict[str, int] = {}
            for track in self._tracks:
                folder = str(Path(track["path"]).parent)
                groups[folder] = groups.get(folder, 0) + 1
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Folder", "Tracks"])
            rows = sorted(groups.items(), key=lambda item: item[0].casefold())
            table.setRowCount(len(rows))
            for row, (folder, count) in enumerate(rows):
                item = QTableWidgetItem(folder)
                item.setData(Qt.ItemDataRole.UserRole, folder)
                table.setItem(row, 0, item)
                table.setItem(row, 1, QTableWidgetItem(str(count)))

        else:
            tracks = [
                track for track in self._tracks
                if all(
                    (
                        track["artist"] or "Unknown Artist"
                    ) == self._local_filter.get("artist", track["artist"] or "Unknown Artist")
                    and (track["album"] or "Singles")
                    == self._local_filter.get("album", track["album"] or "Singles")
                    and (
                        str(Path(track["path"]).parent)
                        == self._local_filter.get("folder", str(Path(track["path"]).parent))
                    )
                    for _ in [0]
                )
            ]
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(
                ["Track name", "Artist", "Album", "Duration", "Source"]
            )
            table.setRowCount(len(tracks))
            for row, track in enumerate(tracks):
                values = [
                    track["title"], track["artist"], track["album"],
                    self._format_duration(track["duration"]), "Local Music",
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
                    table.setItem(row, column, item)

        table.setSortingEnabled(True)
        if hasattr(self, "local_filter_label"):
            if self._local_filter:
                self.local_filter_label.setText(
                    "Filtered: " + " · ".join(f"{key.title()}: {value}" for key, value in self._local_filter.items())
                )
            else:
                self.local_filter_label.setText("All tracks")

    def _set_local_view(self, view: str) -> None:
        self._local_view = view
        self._refresh_tracks()

    def _clear_local_filter(self) -> None:
        self._local_filter = {}
        self.local_view_combo.setCurrentText("All Tracks")
        self._refresh_tracks()

    def _activate_local_view_row(self, row: int, _column: int) -> None:
        if self._local_view == "All Tracks":
            self._play_selected_track(row, _column)
            return
        item = self.track_table.item(row, 0)
        if item is None:
            return
        value = item.data(Qt.ItemDataRole.UserRole)
        if self._local_view == "Artists":
            self._local_filter = {"artist": str(value)}
        elif self._local_view == "Albums":
            album, artist = value
            self._local_filter = {"album": album, "artist": artist}
        elif self._local_view == "Folders":
            self._local_filter = {"folder": str(value)}
        self.local_view_combo.setCurrentText("All Tracks")
        self._refresh_tracks()

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
        if self._current_track_path:
            current_track = next(
                (track for track in self._tracks if track["path"] == self._current_track_path),
                None,
            )
            if current_track:
                self._update_player_display(current_track)
                self._load_current_lyrics()
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
            paths = [item["path"] for item in self._track_paths()]
            self._play_track(track, paths)

    def _play_track(self, track: dict, queue_paths: list[str] | None = None) -> None:
        path = Path(track["path"])
        if not path.is_file():
            QMessageBox.warning(self, "Track unavailable", "The audio file no longer exists.")
            self._start_scan()
            return
        track_path = str(path)
        if queue_paths is not None:
            self._playback_queue = list(dict.fromkeys(queue_paths))
            if track_path not in self._playback_queue:
                self._playback_queue.insert(0, track_path)
        elif track_path not in self._playback_queue:
            self._playback_queue = [track_path]
        self._current_queue_index = self._playback_queue.index(track_path)
        self._current_track_path = track_path
        self.player.setSource(QUrl.fromLocalFile(track_path))
        self.player.play()
        self._update_player_display(track)
        self._load_current_lyrics()
        self._refresh_expanded_queue()
        self._save_playback_state()

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

    def _enqueue_paths(self, paths: list[str], play_next: bool = False) -> None:
        clean_paths = list(dict.fromkeys(paths))
        if not clean_paths:
            return
        if not self._playback_queue:
            self._playback_queue = clean_paths
            if self._current_track_path in clean_paths:
                self._current_queue_index = clean_paths.index(self._current_track_path)
            else:
                first = next(
                    (track for track in self._track_paths()
                     if track["path"] == clean_paths[0]),
                    None,
                )
                if first:
                    self._play_track(first, clean_paths)
            self._refresh_expanded_queue()
            return
        insertion = self._current_queue_index + 1 if play_next else len(self._playback_queue)
        additions = [path for path in clean_paths if path not in self._playback_queue]
        self._playback_queue[insertion:insertion] = additions
        self._refresh_expanded_queue()
        self._save_playback_state()

    def _step_track(self, direction: int) -> None:
        if not self._playback_queue:
            available = [track["path"] for track in self._track_paths()]
            if not available:
                return
            self._playback_queue = available
            self._current_queue_index = -1
        if self._shuffle_enabled and direction > 0 and len(self._playback_queue) > 1:
            choices = [
                index for index in range(len(self._playback_queue))
                if index != self._current_queue_index
            ]
            next_index = random.choice(choices)
        else:
            next_index = self._current_queue_index + direction
            if next_index < 0 or next_index >= len(self._playback_queue):
                if self._repeat_mode == "all":
                    next_index = next_index % len(self._playback_queue)
                else:
                    self.player.stop()
                    return
        next_path = self._playback_queue[next_index]
        track = next((item for item in self._tracks if item["path"] == next_path), None)
        if track is None or not Path(next_path).is_file():
            self._playback_queue.pop(next_index)
            self._step_track(direction)
            return
        self._current_queue_index = next_index
        self._play_track(track, self._playback_queue)

    def _previous_track(self) -> None:
        if self.player.position() > 3000:
            self.player.setPosition(0)
        else:
            self._step_track(-1)

    def _next_track(self) -> None:
        self._step_track(1)

    def _media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.LoadedMedia and self._restore_position_ms is not None:
            self.player.setPosition(self._restore_position_ms)
            self._restore_position_ms = None
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._repeat_mode == "one":
                self.player.setPosition(0)
                self.player.play()
            else:
                self._next_track()

    def _update_player_display(self, track: dict | None) -> None:
        if track is None:
            self.player_track_label.setText("Nothing playing")
            self.player_art_label.clear()
            self.player_favorite_button.setText("♡")
            return
        self.player_track_label.setText(
            f"{track['title']}\\n{track['artist'] or 'Unknown artist'} · {track['album'] or 'Single'}"
        )
        artwork = read_cover_art(track["path"])
        pixmap = QPixmap()
        if artwork and pixmap.loadFromData(artwork):
            pixmap = pixmap.scaled(
                56, 56, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.player_art_label.setPixmap(pixmap)
        else:
            self.player_art_label.clear()
        favorite_paths = {item["path"] for item in list_favorites()}
        self.player_favorite_button.setText("♥" if track["path"] in favorite_paths else "♡")
        if self._expanded_player_dialog is not None:
            self._update_expanded_track(track)

    def _toggle_current_favorite(self) -> None:
        if not self._current_track_path:
            return
        favorites = {item["path"] for item in list_favorites()}
        if self._current_track_path in favorites:
            remove_favorite(self._current_track_path)
        else:
            add_favorites([self._current_track_path])
        self._update_player_display(
            next((item for item in self._tracks if item["path"] == self._current_track_path), None)
        )
        self._refresh_favorites()

    def _open_expanded_player(self) -> None:
        if self._expanded_player_dialog is None:
            dialog = QDialog(self)
            dialog.setWindowTitle("Senna Music — Player")
            dialog.resize(1040, 720)
            layout = QHBoxLayout(dialog)
            left = QVBoxLayout()
            self.expanded_art_label = QLabel()
            self.expanded_art_label.setFixedSize(300, 300)
            self.expanded_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            left.addWidget(self.expanded_art_label, 0, Qt.AlignmentFlag.AlignHCenter)
            self.expanded_title_label = QLabel("Nothing playing")
            self.expanded_title_label.setObjectName("sectionTitle")
            self.expanded_title_label.setWordWrap(True)
            left.addWidget(self.expanded_title_label)
            controls = QHBoxLayout()
            previous = QPushButton("Previous")
            previous.clicked.connect(self._previous_track)
            play = QPushButton("Play/Pause")
            play.clicked.connect(self._toggle_playback)
            next_button = QPushButton("Next")
            next_button.clicked.connect(self._next_track)
            controls.addWidget(previous)
            controls.addWidget(play)
            controls.addWidget(next_button)
            left.addLayout(controls)
            self.expanded_position_slider = QSlider(Qt.Orientation.Horizontal)
            self.expanded_position_slider.setRange(0, 0)
            self.expanded_position_slider.sliderPressed.connect(self._slider_pressed)
            self.expanded_position_slider.sliderReleased.connect(self._expanded_slider_released)
            left.addWidget(self.expanded_position_slider)
            lyrics_header = QHBoxLayout()
            lyrics_header.addWidget(QLabel("Lyrics"))
            self.lyrics_follow_button = QPushButton("Follow")
            self.lyrics_follow_button.setCheckable(True)
            self.lyrics_follow_button.setChecked(True)
            self.lyrics_follow_button.setToolTip(
                "Follow the current lyric line; turn off to scroll manually"
            )
            lyrics_header.addWidget(self.lyrics_follow_button)
            self.lyrics_language_combo = QComboBox()
            self.lyrics_language_combo.addItems([
                "Auto", "English", "Bosnian", "Croatian", "Serbian",
                "French", "German", "Dutch", "Spanish", "Italian",
            ])
            self.lyrics_language_combo.setCurrentText(
                self._lyrics_language_label(get_setting("lyrics_language", "auto"))
            )
            self.lyrics_language_combo.currentTextChanged.connect(
                self._lyrics_language_changed
            )
            lyrics_header.addWidget(self.lyrics_language_combo)
            left.addLayout(lyrics_header)
            self.lyrics_status_label = QLabel("Lyrics load when a track is selected.")
            self.lyrics_status_label.setObjectName("muted")
            left.addWidget(self.lyrics_status_label)
            self.lyrics_text = QPlainTextEdit()
            self.lyrics_text.setReadOnly(True)
            self.lyrics_text.setPlaceholderText("Lyrics will appear here when available.")
            left.addWidget(self.lyrics_text, 1)
            left.addStretch(1)

            right = QVBoxLayout()
            right.addWidget(QLabel("Playback Queue"))
            queue_controls = QHBoxLayout()
            self.shuffle_button = QPushButton("Shuffle")
            self.shuffle_button.setCheckable(True)
            self.shuffle_button.toggled.connect(self._set_shuffle)
            self.repeat_combo = QComboBox()
            self.repeat_combo.addItems(["off", "all", "one"])
            self.repeat_combo.currentTextChanged.connect(self._set_repeat_mode)
            queue_controls.addWidget(self.shuffle_button)
            queue_controls.addWidget(QLabel("Repeat"))
            queue_controls.addWidget(self.repeat_combo)
            right.addLayout(queue_controls)
            self.expanded_queue_list = QListWidget()
            self.expanded_queue_list.setDragDropMode(
                QAbstractItemView.DragDropMode.InternalMove
            )
            self.expanded_queue_list.model().rowsMoved.connect(self._queue_reordered)
            right.addWidget(self.expanded_queue_list, 1)
            layout.addLayout(left, 1)
            layout.addLayout(right, 1)
            self._expanded_player_dialog = dialog
            self._refresh_expanded_queue()
            self._update_player_display(
                next((item for item in self._tracks if item["path"] == self._current_track_path), None)
            )
        self._expanded_player_dialog.show()
        if self._current_track_path:
            self._load_current_lyrics()
        self._expanded_player_dialog.raise_()
        self._expanded_player_dialog.activateWindow()

    def _update_expanded_track(self, track: dict) -> None:
        self.expanded_title_label.setText(
            f"{track['title']}\\n{track['artist'] or 'Unknown artist'}\\n{track['album'] or 'Single'}"
        )
        artwork = read_cover_art(track["path"])
        pixmap = QPixmap()
        if artwork and pixmap.loadFromData(artwork):
            self.expanded_art_label.setPixmap(
                pixmap.scaled(
                    300, 300, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.expanded_art_label.clear()
        if self._current_lyrics_path == track["path"] and self._current_lyrics_result:
            self._render_lyrics(self._current_lyrics_result)
        elif self._expanded_player_dialog is not None:
            self.lyrics_status_label.setText("Loading lyrics…")
            self.lyrics_text.setPlainText("")

    def _refresh_expanded_queue(self) -> None:
        if self._expanded_player_dialog is None:
            return
        self.expanded_queue_list.clear()
        for path in self._playback_queue:
            track = next((item for item in self._tracks if item["path"] == path), None)
            label = (
                f"{track['title']} — {track['artist'] or 'Unknown artist'}"
                if track else Path(path).name
            )
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.expanded_queue_list.addItem(item)
        self.expanded_queue_list.setCurrentRow(self._current_queue_index)
        self.shuffle_button.setChecked(self._shuffle_enabled)
        self.repeat_combo.setCurrentText(self._repeat_mode)

    def _queue_reordered(self, *_args) -> None:
        if self._expanded_player_dialog is None:
            return
        self._playback_queue = [
            str(self.expanded_queue_list.item(index).data(Qt.ItemDataRole.UserRole))
            for index in range(self.expanded_queue_list.count())
        ]
        self._current_queue_index = self._playback_queue.index(
            self._current_track_path
        ) if self._current_track_path in self._playback_queue else -1
        self._save_playback_state()

    def _set_shuffle(self, enabled: bool) -> None:
        self._shuffle_enabled = enabled
        self._save_playback_state()

    def _set_repeat_mode(self, mode: str) -> None:
        self._repeat_mode = mode
        self._save_playback_state()

    def _expanded_slider_released(self) -> None:
        self._slider_is_pressed = False
        self.player.setPosition(self.expanded_position_slider.value())


    @staticmethod
    def _lyrics_language_label(code: str) -> str:
        labels = {
            "auto": "Auto", "en": "English", "bs": "Bosnian",
            "hr": "Croatian", "sr": "Serbian", "fr": "French",
            "de": "German", "nl": "Dutch", "es": "Spanish", "it": "Italian",
        }
        return labels.get(code, "Auto")

    @staticmethod
    def _lyrics_language_code(label: str) -> str:
        return {
            "Auto": "auto", "English": "en", "Bosnian": "bs",
            "Croatian": "hr", "Serbian": "sr", "French": "fr",
            "German": "de", "Dutch": "nl", "Spanish": "es", "Italian": "it",
        }.get(label, "auto")

    def _lyrics_language_changed(self, label: str) -> None:
        language = self._lyrics_language_code(label)
        set_setting("lyrics_language", language)
        self._load_current_lyrics(force=True)

    def _load_current_lyrics(self, force: bool = False) -> None:
        if not self._current_track_path:
            return
        if not force and self._current_lyrics_path == self._current_track_path:
            if self._current_lyrics_result:
                self._render_lyrics(self._current_lyrics_result)
                return
            if any(
                worker.isRunning()
                and worker.track["path"] == self._current_track_path
                for worker in self._lyrics_workers
            ):
                return
        track = next(
            (item for item in self._tracks if item["path"] == self._current_track_path),
            None,
        )
        if track is None:
            return
        self._current_lyrics_path = self._current_track_path
        self._current_lyrics_result = None
        self._lyrics_lines = []
        if self._expanded_player_dialog is not None:
            self.lyrics_status_label.setText("Loading lyrics…")
            self.lyrics_text.setPlainText("")
        worker = LyricsWorker(
            track, get_setting("lyrics_language", "auto"), self
        )
        worker.completed.connect(self._lyrics_loaded)
        worker.failed.connect(self._lyrics_failed)
        worker.finished.connect(lambda current=worker: self._lyrics_worker_finished(current))
        self._lyrics_workers.append(worker)
        worker.start()

    def _lyrics_worker_finished(self, worker: LyricsWorker) -> None:
        if worker in self._lyrics_workers:
            self._lyrics_workers.remove(worker)

    def _lyrics_loaded(self, path: str, language: str, result: LyricsResult) -> None:
        if (
            path != self._current_track_path
            or language != get_setting("lyrics_language", "auto")
        ):
            return
        self._current_lyrics_result = result
        self._render_lyrics(result)

    def _lyrics_failed(self, path: str, language: str, message: str) -> None:
        if (
            path != self._current_track_path
            or language != get_setting("lyrics_language", "auto")
        ):
            return
        self._current_lyrics_result = LyricsResult("error", message=message)
        self._render_lyrics(self._current_lyrics_result)

    def _render_lyrics(self, result: LyricsResult) -> None:
        if self._expanded_player_dialog is None:
            return
        if result.status == "found":
            if result.synced_lyrics:
                self._lyrics_lines = parse_lrc(result.synced_lyrics)
                self.lyrics_text.setPlainText("\\n".join(line for _, line in self._lyrics_lines))
                self.lyrics_status_label.setText(
                    f"Synchronized lyrics · {result.language.upper()} · {result.provider}"
                )
            else:
                self._lyrics_lines = []
                self.lyrics_text.setPlainText(result.plain_lyrics)
                self.lyrics_status_label.setText(
                    f"Plain lyrics · {result.language.upper()} · {result.provider}"
                )
        else:
            self._lyrics_lines = []
            self.lyrics_text.setPlainText("")
            self.lyrics_status_label.setText(result.message or "Lyrics are unavailable.")
        self._sync_lyrics(self.player.position())

    def _sync_lyrics(self, position_ms: int) -> None:
        if (
            self._expanded_player_dialog is None
            or not self._lyrics_lines
            or not hasattr(self, "lyrics_text")
            or not self.lyrics_follow_button.isChecked()
        ):
            return
        active_index = -1
        for index, (timestamp, _line) in enumerate(self._lyrics_lines):
            if timestamp > position_ms:
                break
            active_index = index
        if active_index < 0:
            return
        cursor = QTextCursor(self.lyrics_text.document())
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        for _index in range(active_index):
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format.setBackground(self.palette().color(QPalette.ColorRole.Highlight))
        self.lyrics_text.setExtraSelections([selection])
        self.lyrics_text.setTextCursor(cursor)
        self.lyrics_text.ensureCursorVisible()

    def _save_playback_state(self) -> None:
        state = {
            "queue": self._playback_queue,
            "current_track": self._current_track_path,
            "position_ms": self.player.position(),
            "shuffle": self._shuffle_enabled,
            "repeat": self._repeat_mode,
        }
        set_setting("playback_state", json.dumps(state))

    def _restore_playback_state(self) -> None:
        try:
            state = json.loads(get_setting("playback_state", "{}"))
        except (TypeError, ValueError):
            return
        self._playback_queue = [
            str(path) for path in state.get("queue", []) if isinstance(path, str)
        ]
        self._current_track_path = state.get("current_track")
        if self._current_track_path not in self._playback_queue:
            self._current_track_path = None
        self._current_queue_index = (
            self._playback_queue.index(self._current_track_path)
            if self._current_track_path else -1
        )
        self._shuffle_enabled = bool(state.get("shuffle", False))
        self._repeat_mode = state.get("repeat", "off")
        if self._repeat_mode not in {"off", "all", "one"}:
            self._repeat_mode = "off"
        if self._current_track_path and Path(self._current_track_path).is_file():
            self._restore_position_ms = int(state.get("position_ms", 0))
            self.player.setSource(QUrl.fromLocalFile(self._current_track_path))
            track = next(
                (item for item in self._tracks if item["path"] == self._current_track_path),
                None,
            )
            if track:
                self._update_player_display(track)
                self._load_current_lyrics()
            else:
                self.player_track_label.setText(Path(self._current_track_path).name)
        self._refresh_expanded_queue()


    def _playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        self.play_button.setText(
            "Pause" if state == QMediaPlayer.PlaybackState.PlayingState else "Play"
        )

    def _position_changed(self, position: int) -> None:
        if not self._slider_is_pressed:
            self.position_slider.setValue(position)
            if self._expanded_player_dialog is not None:
                self.expanded_position_slider.setValue(position)
        self.position_label.setText(self._format_duration(position / 1000))
        self._sync_lyrics(position)

    def _duration_changed(self, duration: int) -> None:
        self.position_slider.setRange(0, duration)
        if self._expanded_player_dialog is not None:
            self.expanded_position_slider.setRange(0, duration)
        self.duration_label.setText(self._format_duration(duration / 1000))

    def _slider_pressed(self) -> None:
        self._slider_is_pressed = True

    def _slider_released(self) -> None:
        self._slider_is_pressed = False
        self.player.setPosition(self.position_slider.value())

    def _track_context_menu(self, position) -> None:
        if self._local_view != "All Tracks":
            return
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
        for row in sorted(selected_rows):
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
        play_next_action = menu.addAction("Play Next")
        add_queue_action = menu.addAction("Add to Queue")
        details_action = menu.addAction("View Track Details")
        menu.addSeparator()
        edit_label = "Edit Metadata" if len(selected_tracks) == 1 else "Edit Metadata for Selected"
        edit_action = menu.addAction(edit_label)
        menu.addSeparator()
        favorite_paths = {item["path"] for item in list_favorites()}
        selected_paths = [track["path"] for track in selected_tracks]
        all_favorite = all(path in favorite_paths for path in selected_paths)
        favorite_label = "Remove from Favorites" if all_favorite else "Add to Favorites"
        add_favorite_action = menu.addAction(favorite_label)
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
            self._play_track(
                selected_tracks[0], [track["path"] for track in self._track_paths()]
            )
        elif chosen == play_next_action:
            self._enqueue_paths(selected_paths, play_next=True)
        elif chosen == add_queue_action:
            self._enqueue_paths(selected_paths)
        elif chosen == details_action:
            self._show_track_details(selected_tracks[0])
        elif chosen == edit_action:
            self._edit_track_metadata(selected_tracks)
        elif chosen == add_favorite_action:
            if all_favorite:
                for path in selected_paths:
                    remove_favorite(path)
            else:
                add_favorites(selected_paths)
            self._refresh_favorites()
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
        play_action = menu.addAction("Play")
        play_next_action = menu.addAction("Play Next")
        add_queue_action = menu.addAction("Add to Queue")
        menu.addSeparator()
        remove_action = menu.addAction("Remove from Playlist")
        chosen = menu.exec(self.playlist_tracks_table.viewport().mapToGlobal(position))
        if chosen == play_action:
            self._play_playlist_track(row, 0)
        elif chosen == play_next_action:
            self._enqueue_paths([path], play_next=True)
        elif chosen == add_queue_action:
            self._enqueue_paths([path])
        elif chosen == remove_action:
            remove_track_from_playlist(item_id, path)
            self._refresh_playlists(item_id)

    def _play_playlist_track(self, row: int, _column: int) -> None:
        item = self.playlist_tracks_table.item(row, 0)
        playlist_id = self._selected_list_id(self.playlist_list)
        if item is not None and playlist_id is not None:
            path = item.data(Qt.ItemDataRole.UserRole)
            track = next((entry for entry in self._tracks if entry["path"] == path), None)
            queue_paths = [entry["path"] for entry in list_playlist_tracks(playlist_id)]
            if track:
                self._play_track(track, queue_paths)


    @staticmethod
    def _table_track_paths(table: QTableWidget) -> list[str]:
        return [
            str(table.item(row, 0).data(Qt.ItemDataRole.UserRole))
            for row in range(table.rowCount())
            if table.item(row, 0) is not None
            and table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        ]

    def _playlist_tracks_reordered(self, *_args) -> None:
        playlist_id = self._selected_list_id(self.playlist_list)
        if playlist_id is not None:
            reorder_playlist_tracks(
                playlist_id, self._table_track_paths(self.playlist_tracks_table)
            )
            self._refresh_playlists(playlist_id)

    def _favorites_reordered(self, *_args) -> None:
        reorder_favorites(self._table_track_paths(self.favorites_table))
        self._refresh_favorites()

    def _favorite_collection_tracks_reordered(self, *_args) -> None:
        collection_id = self._selected_list_id(self.favorite_collections_list)
        if collection_id is not None:
            reorder_favorite_collection_tracks(
                collection_id,
                self._table_track_paths(self.favorite_collection_tracks_table),
            )
            self._refresh_favorite_collections(collection_id)

    def _favorites_track_menu(self, position) -> None:
        row = self.favorites_table.rowAt(position.y())
        if row < 0:
            return
        selected_rows = {
            index.row() for index in self.favorites_table.selectionModel().selectedRows()
        }
        if row not in selected_rows:
            self.favorites_table.setCurrentCell(row, 0)
            selected_rows = {row}
        paths = [
            str(self.favorites_table.item(index, 0).data(Qt.ItemDataRole.UserRole))
            for index in sorted(selected_rows)
            if self.favorites_table.item(index, 0) is not None
        ]
        if not paths:
            return
        menu = QMenu(self)
        play_action = menu.addAction("Play")
        next_action = menu.addAction("Play Next")
        queue_action = menu.addAction("Add to Queue")
        menu.addSeparator()
        remove_action = menu.addAction("Remove from Favorites")
        chosen = menu.exec(self.favorites_table.viewport().mapToGlobal(position))
        if chosen == play_action:
            track = next((item for item in self._tracks if item["path"] == paths[0]), None)
            if track:
                self._play_track(track, [item["path"] for item in list_favorites()])
        elif chosen == next_action:
            self._enqueue_paths(paths, play_next=True)
        elif chosen == queue_action:
            self._enqueue_paths(paths)
        elif chosen == remove_action:
            for path in paths:
                remove_favorite(path)
            self._refresh_favorites()

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
        play_action = menu.addAction("Play")
        play_next_action = menu.addAction("Play Next")
        add_queue_action = menu.addAction("Add to Queue")
        menu.addSeparator()
        remove_action = menu.addAction("Remove from Collection")
        chosen = menu.exec(
            self.favorite_collection_tracks_table.viewport().mapToGlobal(position)
        )
        if chosen == play_action:
            self._play_favorite_collection_track(row, 0)
        elif chosen == play_next_action:
            self._enqueue_paths([path], play_next=True)
        elif chosen == add_queue_action:
            self._enqueue_paths([path])
        elif chosen == remove_action:
            remove_track_from_favorite_collection(collection_id, path)
            self._refresh_favorite_collections(collection_id)

    def _play_favorite_track(self, row: int, _column: int) -> None:
        self._play_table_track(
            self.favorites_table, row,
            [track["path"] for track in list_favorites()],
        )

    def _play_favorite_collection_track(self, row: int, _column: int) -> None:
        collection_id = self._selected_list_id(self.favorite_collections_list)
        paths = (
            [track["path"] for track in list_favorite_collection_tracks(collection_id)]
            if collection_id is not None else []
        )
        self._play_table_track(self.favorite_collection_tracks_table, row, paths)

    def _play_table_track(
        self, table: QTableWidget, row: int, queue_paths: list[str] | None = None
    ) -> None:
        item = table.item(row, 0)
        if item is not None:
            path = item.data(Qt.ItemDataRole.UserRole)
            track = next((entry for entry in self._tracks if entry["path"] == path), None)
            if track:
                self._play_track(track, queue_paths)

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


    def _select_download_folder(self) -> None:
        current = self.download_folder_input.text().strip()
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", current)
        if folder:
            self.download_folder_input.setText(folder)

    def _select_ffmpeg(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select FFmpeg executable", "", "FFmpeg executable (ffmpeg.exe);;All files (*)"
        )
        if path:
            self.ffmpeg_path_input.setText(path)

    def _save_download_settings(self) -> None:
        folder = self.download_folder_input.text().strip()
        if folder and not Path(folder).expanduser().is_dir():
            QMessageBox.warning(self, "Invalid folder", "The download folder does not exist.")
            return
        set_setting("download_folder", folder)
        set_setting("download_format", self.download_format_combo.currentText())
        set_setting("download_quality", self.download_quality_combo.currentText())
        set_setting("lyrics_language", self._lyrics_language_code(
            self.lyrics_language_settings_combo.currentText()
        ))
        set_setting("ffmpeg_location", self.ffmpeg_path_input.text().strip())
        if hasattr(self, "lyrics_language_combo"):
            self.lyrics_language_combo.setCurrentText(
                self._lyrics_language_label(get_setting("lyrics_language", "auto"))
            )
        QMessageBox.information(self, "Settings saved", "Download settings were saved.")

    def _search_result_menu(self, position) -> None:
        clicked_row = self.search_results_table.rowAt(position.y())
        if clicked_row < 0:
            return
        selected_rows = {
            index.row() for index in self.search_results_table.selectionModel().selectedRows()
        }
        if clicked_row not in selected_rows:
            self.search_results_table.setCurrentCell(clicked_row, 0)
            selected_rows = {clicked_row}
        results = []
        for row in sorted(selected_rows):
            item = self.search_results_table.item(row, 0)
            if item is None:
                continue
            result = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(result, SearchResult) and result.download_url:
                results.append(result)
        if not results:
            return
        menu = QMenu(self)
        if len(results) == 1:
            format_menu = menu.addMenu("Download as")
            actions = {
                format_menu.addAction(label): value
                for label, value in (
                    ("Original", "original"), ("MP3", "mp3"),
                    ("M4A", "m4a"), ("FLAC", "flac"),
                )
            }
            chosen = menu.exec(self.search_results_table.viewport().mapToGlobal(position))
            if chosen in actions:
                self._enqueue_search_results(results, actions[chosen])
        else:
            download_action = menu.addAction("Download Selected")
            chosen = menu.exec(self.search_results_table.viewport().mapToGlobal(position))
            if chosen == download_action:
                self._enqueue_search_results(results)

    def _enqueue_search_results(
        self, results: list[SearchResult], requested_format: str | None = None
    ) -> None:
        destination = get_setting("download_folder", "")
        if not destination or not Path(destination).expanduser().is_dir():
            destination = QFileDialog.getExistingDirectory(
                self, "Choose Download Folder", str(Path.home())
            )
            if not destination:
                return
            set_setting("download_folder", destination)
            if hasattr(self, "download_folder_input"):
                self.download_folder_input.setText(destination)
        file_format = requested_format or get_setting("download_format", "original")
        quality = get_setting("download_quality", "192")
        queued = 0
        unavailable = 0
        for result in results:
            if not result.download_url:
                unavailable += 1
                continue
            add_download_task({
                "source": result.source,
                "source_url": result.url,
                "download_url": result.download_url,
                "destination_root": destination,
                "title": result.title,
                "artist": result.artist,
                "album": result.album,
                "requested_format": file_format,
                "quality": quality,
            })
            queued += 1
        self._refresh_download_queue()
        if queued:
            self.download_status.setText(f"{queued} download(s) added to the queue.")
            self._start_download_queue()
        if unavailable:
            QMessageBox.information(
                self, "Some results unavailable",
                f"{unavailable} result(s) do not have a supported download URL.",
            )

    def _refresh_download_queue(self) -> None:
        if not hasattr(self, "download_table"):
            return
        tasks = list_download_tasks()
        self.download_table.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            values = [
                task["title"], task["artist"], task["album"],
                task["requested_format"].upper(), task["status"].title(),
                f"{task['progress']:.0f}%", task["source"],
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value or ""))
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, task["id"])
                    if task["error"]:
                        item.setToolTip(task["error"])
                self.download_table.setItem(row, column, item)

    def _start_download_queue(self) -> None:
        if self._download_worker is not None and self._download_worker.isRunning():
            self._download_worker.resume()
            return
        if get_next_download_task() is None:
            self._refresh_download_queue()
            return
        ffmpeg_location = get_setting("ffmpeg_location", "")
        self._download_worker = DownloadQueueWorker(ffmpeg_location, self)
        self._download_worker.progress_changed.connect(self._download_progress_changed)
        self._download_worker.task_changed.connect(
            lambda _task_id: self._refresh_download_queue()
        )
        self._download_worker.queue_finished.connect(self._download_queue_finished)
        self._download_worker.start()
        self.download_status.setText("Download queue is running…")

    def _download_progress_changed(self, _task_id: int, _progress: float) -> None:
        self._refresh_download_queue()

    def _download_queue_finished(self) -> None:
        self._refresh_download_queue()
        self._download_worker = None
        self.download_status.setText("Download queue is idle.")

    def _pause_download_queue(self) -> None:
        if self._download_worker is not None and self._download_worker.isRunning():
            self._download_worker.pause()
            self.download_status.setText("Download paused.")

    def _resume_download_queue(self) -> None:
        if self._download_worker is not None and self._download_worker.isRunning():
            self._download_worker.resume()
        else:
            self._start_download_queue()

    def _cancel_current_download(self) -> None:
        if self._download_worker is not None and self._download_worker.isRunning():
            self._download_worker.cancel_current()

    def _selected_download_ids(self) -> list[int]:
        return [
            int(self.download_table.item(row, 0).data(Qt.ItemDataRole.UserRole))
            for row in sorted({
                index.row() for index in self.download_table.selectionModel().selectedRows()
            })
            if self.download_table.item(row, 0) is not None
        ]

    def _retry_selected_downloads(self) -> None:
        for task_id in self._selected_download_ids():
            task = next((item for item in list_download_tasks() if item["id"] == task_id), None)
            if task and task["status"] in {"failed", "cancelled"}:
                retry_download_task(task_id)
        self._refresh_download_queue()
        self._start_download_queue()

    def _remove_selected_downloads(self) -> None:
        active_id = self._download_worker.active_task_id if self._download_worker else None
        for task_id in self._selected_download_ids():
            if task_id != active_id:
                delete_download_task(task_id)
        self._refresh_download_queue()

    def _clear_finished_downloads(self) -> None:
        clear_finished_download_tasks()
        self._refresh_download_queue()

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


    def closeEvent(self, event) -> None:
        workers = [
            self._scan_thread, self._search_worker, self._download_worker,
            *self._lyrics_workers,
        ]
        if self._download_worker is not None and self._download_worker.isRunning():
            self._download_worker.stop_after_current()
        for worker in workers:
            if worker is not None and worker.isRunning() and not worker.wait(5000):
                QMessageBox.warning(
                    self,
                    "Operation still running",
                    "Senna Music is still finishing a background operation. "
                    "Wait for it to stop, then close the application.",
                )
                event.ignore()
                return
        self._save_playback_state()
        event.accept()

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
