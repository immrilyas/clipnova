import os
import re
import sys
import json
import uuid
import shutil
import secrets
import string
import threading
import subprocess
import webbrowser
import requests
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QComboBox, QLineEdit,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QMessageBox, QFrame, QSizePolicy,
    QAbstractItemView, QCheckBox, QStackedWidget, QScrollArea,
    QGridLayout, QDialog, QSpinBox
)

APP_NAME = "ClipNova"
APP_DIR = Path(__file__).resolve().parent

def resource_path(*parts):
    """Find bundled resources in source and PyInstaller builds."""
    roots = []
    if getattr(sys, "_MEIPASS", None):
        roots.append(Path(sys._MEIPASS))
    roots.extend([APP_DIR, Path(sys.executable).resolve().parent])
    for root in roots:
        candidate = root.joinpath(*parts)
        if candidate.exists():
            return candidate
    return roots[0].joinpath(*parts) if roots else Path(*parts)
DEFAULT_FOLDER = str(Path.home() / "Downloads" / "ClipNova")
DATA_DIR = Path.home() / "AppData" / "Local" / "ClipNova"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LICENSE_FILE = DATA_DIR / "licenses.json"
ACTIVE_LICENSE_FILE = DATA_DIR / "active_license.json"

PAYMENT_METHODS = {
    "Meezan Bank": {
        "title": "ILYAS KHAN",
        "details": [
            ("IBAN", "PK12MEZN0000300115107271"),
            ("Account number", "00300115107271"),
        ],
        "qr": "Account_QR_Code.png",
        "description": "Bank transfer",
    },
    "Easypaisa": {
        "title": "ILYAS KHAN",
        "details": [("Mobile number", "03139480207")],
        "qr": "image.png",
        "description": "Mobile wallet",
    },
    "JazzCash / Raast": {
        "title": "SHAHZAIB",
        "details": [("Mobile number", "03429818400")],
        "qr": "Raast_Qr.png",
        "description": "Mobile wallet / Raast",
    },
}

PLANS = [
    ("STARTER", "PKR 1,500 / month", "300 videos/day • 15,000 videos/month • No ads"),
    ("PREMIUM", "PKR 2,500 / month", "800 videos/day • 40,000 videos/month • No ads"),
    ("STARTER PLUS", "PKR 7,000 lifetime", "1,000 videos/day • 80,000 videos lifetime • No ads"),
    ("ULTRA PRO", "PKR 10,000 lifetime", "Unlimited daily and lifetime downloads • No ads"),
]
FREE_PLAN_DETAILS = "100 videos/day • Ads supported • After daily limit, each verified completed rewarded ad unlocks 1 extra video"

DARK_STYLE = r"""
* { font-family: "Segoe UI"; font-size: 10pt; }
QMainWindow, QWidget { background:#071126; color:#edf3ff; }
QFrame#Sidebar { background:#091631; border:1px solid #20365f; border-radius:18px; }
QFrame#Panel { background:#0c1c3b; border:1px solid #244779; border-radius:15px; }
QFrame#Hero { border:1px solid #ff8a24; border-radius:20px;
 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #5a2b12,stop:.5 #10234d,stop:1 #0a1530); }
QFrame#MiniPanel { background:#0b1934; border:1px solid #253d69; border-radius:13px; }
QLabel#Brand { font-size:21pt; font-weight:900; color:#ffffff; }
QLabel#Heading { font-size:22pt; font-weight:850; color:#ffffff; }
QLabel#HeroTitle { font-size:27pt; font-weight:900; color:#ffffff; }
QLabel#Section { font-size:12pt; font-weight:800; color:#f5f7ff; }
QLabel#Muted { color:#a8bfdf; }
QLabel#Metric { font-size:19pt; font-weight:900; color:#ffffff; }
QLabel#Accent { color:#ffbd73; font-weight:800; }
QPushButton { background:#12284c; color:#eaf2ff; border:1px solid #2b4d7b;
 border-radius:10px; padding:10px 12px; font-weight:650; }
QPushButton:hover { background:#203f75; border:1px solid #8d7aff; }
QPushButton:pressed { background:#3827a8; }
QPushButton:disabled { color:#71819d; background:#111d32; border-color:#26334b; }
QPushButton#Primary { color:white; border:1px solid #ff9b38;
 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ff9b38,stop:.55 #f47721,stop:1 #c94d0b);
 font-size:11pt; font-weight:850; }
QPushButton#Primary:hover { background:#ffad55; }
QPushButton#NavActive { background:#c95b12; color:white; border:1px solid #ffc078; font-weight:850; }
QTextEdit, QLineEdit, QComboBox, QSpinBox { background:#07142c; color:#f4f7ff;
 border:1px solid #2a4d7c; border-radius:9px; padding:9px; }
QTextEdit:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border:1px solid #ff9b38; }
QComboBox QAbstractItemView { background:#0c1c3b; color:white; selection-background-color:#b94c0b; }
QTableWidget { background:#07142c; alternate-background-color:#0d2041; color:#eaf2ff;
 border:1px solid #253e6a; border-radius:10px; gridline-color:#1a3155; selection-background-color:#243d7b; }
QHeaderView::section { background:#102448; color:#c6dcff; border:0; padding:10px 6px; font-weight:800; }
QProgressBar { background:#1a2b4a; color:white; border:0; border-radius:6px;
 text-align:center; min-height:14px; max-height:14px; }
QProgressBar::chunk { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #ffad42,stop:1 #f47721); border-radius:6px; }
QCheckBox { color:#c7d9f5; spacing:7px; }
"""

LIGHT_STYLE = r"""
* { font-family: "Segoe UI"; font-size: 10pt; }
QMainWindow, QWidget { background:#eef3ff; color:#35251a; }
QFrame#Sidebar { background:#ffffff; border:1px solid #d5e0f6; border-radius:18px; }
QFrame#Panel { background:#ffffff; border:1px solid #cedcf6; border-radius:15px; }
QFrame#Hero { border:1px solid #ffc078; border-radius:20px;
 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ffe5cd,stop:.5 #f4f8ff,stop:1 #dceeff); }
QFrame#MiniPanel { background:#f8fbff; border:1px solid #d6e2f7; border-radius:13px; }
QLabel#Brand { font-size:21pt; font-weight:900; color:#b84c0b; }
QLabel#Heading { font-size:22pt; font-weight:850; color:#142a60; }
QLabel#HeroTitle { font-size:27pt; font-weight:900; color:#1a2870; }
QLabel#Section { font-size:12pt; font-weight:800; color:#182c5b; }
QLabel#Muted { color:#5b6f99; }
QLabel#Metric { font-size:19pt; font-weight:900; color:#1a2e65; }
QLabel#Accent { color:#d65b0a; font-weight:800; }
QPushButton { background:#fffaf6; color:#57301b; border:1px solid #f1c49f;
 border-radius:10px; padding:10px 12px; font-weight:650; }
QPushButton:hover { background:#fff0e2; border:1px solid #ff9b38; }
QPushButton:pressed { background:#ffe0c2; }
QPushButton:disabled { color:#99a8c7; background:#f2f5fb; border-color:#dfe7f6; }
QPushButton#Primary { color:white; border:1px solid #8a75ff;
 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ff9b38,stop:.55 #f47721,stop:1 #c94d0b);
 font-size:11pt; font-weight:850; }
QPushButton#Primary:hover { background:#ffad55; }
QPushButton#NavActive { background:#c95b12; color:white; border:1px solid #ffc078; font-weight:850; }
QTextEdit, QLineEdit, QComboBox, QSpinBox { background:#fffdfb; color:#35251a;
 border:1px solid #f1c49f; border-radius:9px; padding:9px; }
QTextEdit:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border:1px solid #f47721; }
QComboBox QAbstractItemView { background:white; color:#35251a; selection-background-color:#ffe0c2; }
QTableWidget { background:#fffdfb; alternate-background-color:#fff1e6; color:#35251a;
 border:1px solid #f1c49f; border-radius:10px; gridline-color:#f5d9c2; selection-background-color:#ffe2ca; }
QHeaderView::section { background:#ffe5d0; color:#75411f; border:0; padding:10px 6px; font-weight:800; }
QProgressBar { background:#e1e9f8; color:#35251a; border:0; border-radius:6px;
 text-align:center; min-height:14px; max-height:14px; }
QProgressBar::chunk { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #20c997,stop:1 #168dff); border-radius:6px; }
QCheckBox { color:#405782; spacing:7px; }
"""


def load_json(path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError):
        pass
    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(path)


def find_ffmpeg():
    found = shutil.which("ffmpeg")
    if found:
        return str(Path(found).resolve().parent)

    candidates = [
        APP_DIR / "bin",
        APP_DIR / "_internal" / "bin",
        Path(sys.executable).parent / "bin",
        Path.cwd() / "bin",
    ]
    for folder in candidates:
        if (folder / "ffmpeg.exe").is_file():
            return str(folder)
        if (folder / "ffmpeg").is_file():
            return str(folder)
    return None


def normalize_url(value):
    value = value.strip().strip("<>()[]{}\"'")
    if not value:
        return ""
    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value
    return value


def platform_for(url):
    try:
        host = (urlparse(url).hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        if host.startswith("m."):
            host = host[2:]

        if host == "youtu.be" or host.endswith(("youtube.com", "youtube-nocookie.com")):
            return "YouTube"
        if host == "instagram.com" or host.endswith(".instagram.com") or host == "instagr.am":
            return "Instagram"
        if host == "fb.watch" or host.endswith(".fb.watch") or host == "facebook.com" or host.endswith(".facebook.com"):
            return "Facebook"
        if host == "tiktok.com" or host.endswith(".tiktok.com"):
            return "TikTok"
    except ValueError:
        pass
    return None


def extract_urls(text):
    parts = re.split(r"[\r\n\t ]+", text.strip())
    found = []
    for part in parts:
        if not part:
            continue
        url = normalize_url(part.rstrip(".,;!?"))
        if platform_for(url):
            found.append(url)
    return found


def find_payment_image(filename):
    """Look for a QR image in common project locations."""
    roots = [
        APP_DIR,
        Path.cwd(),
        Path.home() / "Documents" / "PythonSetupTest",
    ]

    candidates = []
    for base in roots:
        candidates.extend([
            base / "assets" / "payments" / filename,
            base / "assets" / filename,
            base / "payments" / filename,
            base / filename,
        ])

    for path in candidates:
        try:
            if path.is_file():
                return path
        except OSError:
            pass

    # Search a few likely folders without scanning the entire drive.
    for base in roots:
        if not base.is_dir():
            continue
        try:
            for path in base.rglob("*"):
                if path.is_file() and path.name.casefold() == filename.casefold():
                    return path
        except (OSError, PermissionError):
            continue
    return None


class DownloadWorker(QThread):
    progress_changed = Signal(int, int, str)
    status_changed = Signal(int, str)
    item_finished = Signal(int, str, str)
    all_finished = Signal()

    def __init__(self, jobs, folder, quality):
        super().__init__()
        self.jobs = jobs
        self.folder = folder
        self.quality = quality
        self.resume_event = threading.Event()
        self.resume_event.set()
        self.stop_requested = threading.Event()
        self.current_row = None

    def pause(self):
        self.resume_event.clear()

    def resume(self):
        self.resume_event.set()

    def stop(self):
        self.stop_requested.set()
        self.resume_event.set()

    def progress_hook(self, row, data):
        while not self.resume_event.is_set():
            if self.stop_requested.is_set():
                raise yt_dlp.utils.DownloadError("Stopped by user")
            self.msleep(150)

        if self.stop_requested.is_set():
            raise yt_dlp.utils.DownloadError("Stopped by user")

        status = data.get("status")
        if status == "downloading":
            downloaded = data.get("downloaded_bytes") or 0
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            percent = int(downloaded * 100 / total) if total else 0
            details = []
            if data.get("speed"):
                details.append(f"{data['speed'] / 1048576:.2f} MB/s")
            if data.get("eta") is not None:
                details.append(f"ETA {int(data['eta'])}s")
            if total:
                details.append(f"{downloaded / 1048576:.1f} / {total / 1048576:.1f} MB")
            self.progress_changed.emit(row, max(0, min(100, percent)), " | ".join(details) or "Downloading...")
        elif status == "finished":
            self.progress_changed.emit(row, 100, "Processing file...")

    def run(self):
        os.makedirs(self.folder, exist_ok=True)
        ffmpeg_dir = find_ffmpeg()

        for row, url in self.jobs:
            if self.stop_requested.is_set():
                break

            self.current_row = row
            self.status_changed.emit(row, "Preparing")

            options = {
                "outtmpl": os.path.join(self.folder, "%(title).180B [%(id)s].%(ext)s"),
                "noplaylist": True,
                "windowsfilenames": True,
                "retries": 3,
                "fragment_retries": 3,
                "continuedl": True,
                "nopart": False,
                "overwrites": False,
                "quiet": True,
                "no_warnings": False,
                "socket_timeout": 30,
                "progress_hooks": [lambda data, r=row: self.progress_hook(r, data)],
            }

            if ffmpeg_dir:
                options["ffmpeg_location"] = ffmpeg_dir

            if self.quality == "Best available":
                options["format"] = "bestvideo*+bestaudio/best"
                if ffmpeg_dir:
                    options["merge_output_format"] = "mp4"
            elif self.quality in ("1080p", "720p", "480p"):
                height = {"1080p": 1080, "720p": 720, "480p": 480}[self.quality]
                options["format"] = (
                    f"bestvideo*[height<={height}]+bestaudio/"
                    f"best[height<={height}]/best"
                )
                if ffmpeg_dir:
                    options["merge_output_format"] = "mp4"
            elif self.quality == "MP3 Audio":
                if not ffmpeg_dir:
                    self.status_changed.emit(row, "Failed")
                    self.item_finished.emit(row, "Failed", "FFmpeg is required for MP3 conversion.")
                    self.current_row = None
                    continue
                options["format"] = "bestaudio/best"
                options["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]

            try:
                self.status_changed.emit(row, "Downloading")
                with yt_dlp.YoutubeDL(options) as downloader:
                    result = downloader.download([url])

                if self.stop_requested.is_set():
                    self.status_changed.emit(row, "Stopped")
                    self.item_finished.emit(row, "Stopped", "Stopped by user. Partial file may be resumable.")
                    break

                if result:
                    raise yt_dlp.utils.DownloadError("Downloader reported an unsuccessful result.")

                self.status_changed.emit(row, "Completed")
                self.progress_changed.emit(row, 100, "Finished")
                self.item_finished.emit(row, "Completed", "Download finished")

            except Exception as exc:
                if self.stop_requested.is_set():
                    self.status_changed.emit(row, "Stopped")
                    self.item_finished.emit(row, "Stopped", "Stopped by user. Try again to resume if possible.")
                    break

                message = str(exc).replace("\n", " ").strip()
                self.status_changed.emit(row, "Failed")
                self.item_finished.emit(row, "Failed", message[:220] or "Download failed")
            finally:
                self.current_row = None

        self.all_finished.emit()


class ClipNovaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("assets", "icons", "ClipNova.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setWindowTitle("ClipNova | Video Downloader")
        self.resize(1440, 900)
        self.setMinimumSize(1050, 700)

        self.download_folder = DEFAULT_FOLDER
        self.worker = None
        self.dark_mode = True
        self.selected_platform = "Auto Detect"
        self.active_page = "Home"
        self.payment_method = "Meezan Bank"

        os.makedirs(self.download_folder, exist_ok=True)

        self.nav_buttons = {}
        self.build_ui()
        self.apply_theme()
        self.show_page("Home")
        # Validate any saved license against the online server after the UI appears.
        QTimer.singleShot(700, self.validate_saved_license)

    def panel(self, parent_layout, object_name="Panel", margins=(16, 14, 16, 14)):
        frame = QFrame()
        frame.setObjectName(object_name)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(*margins)
        layout.setSpacing(11)
        parent_layout.addWidget(frame)
        return frame, layout

    def label(self, text, object_name=None, wrap=False):
        item = QLabel(text)
        if object_name:
            item.setObjectName(object_name)
        item.setWordWrap(wrap)
        return item

    def button(self, text, callback, primary=False):
        btn = QPushButton(text)
        if primary:
            btn.setObjectName("Primary")
        btn.clicked.connect(callback)
        return btn

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(10)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(225)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(13, 17, 13, 14)
        side.setSpacing(8)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(9)
        logo_icon = QLabel()
        logo_icon.setFixedSize(38, 38)
        logo_icon.setScaledContents(True)
        logo_png = resource_path("assets", "icons", "ClipNova_Icon.png")
        if logo_png.exists():
            logo_icon.setPixmap(QPixmap(str(logo_png)))
        else:
            logo_icon.setText("▶")
            logo_icon.setObjectName("Brand")
        logo_row.addWidget(logo_icon)
        logo = QLabel("ClipNova")
        logo.setObjectName("Brand")
        logo.setWordWrap(False)
        logo.setMinimumWidth(0)
        logo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        logo_row.addWidget(logo, 1)
        side.addLayout(logo_row)

        tagline = self.label("DOWNLOAD  •  CONVERT  •  ENJOY", "Muted")
        tagline.setWordWrap(True)
        side.addWidget(tagline)
        side.addSpacing(18)

        nav_items = [
            ("Home", "⌂", "Home"),
            ("Download", "↓", "Download"),
            ("History", "◷", "History"),
            ("Pricing", "♛", "Pricing"),
            ("License", "⌕", "License"),
            ("Payment", "▤", "Payment"),
            ("Support", "☏", "Support"),
        ]

        for key, icon, title in nav_items:
            btn = QPushButton(f"{icon}   {key}")
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked=False, page=key: self.show_page(page))
            side.addWidget(btn)
            self.nav_buttons[key] = btn

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        side.addWidget(sep)

        for key in ["Privacy Policy", "Terms & Conditions", "EULA / License", "About Us", "Contact Us"]:
            btn = QPushButton(key)
            btn.setMinimumHeight(33)
            btn.setStyleSheet("text-align:left;")
            btn.clicked.connect(lambda checked=False, page=key: self.show_page(page))
            side.addWidget(btn)
            self.nav_buttons[key] = btn

        side.addStretch()

        pro, pro_layout = self.panel(side, "MiniPanel", (12, 12, 12, 12))
        pro_layout.addWidget(self.label("♛  UPGRADE CLIPNOVA", "Section"))
        pro_layout.addWidget(self.label("Review plans and payment options.", "Muted", True))
        pro_layout.addWidget(self.button("View Plans  →", lambda: self.show_page("Pricing"), True))
        side.addWidget(self.label("ClipNova • Windows", "Muted"))

        outer.addWidget(sidebar)

        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.page_host = QWidget()
        self.page_layout = QVBoxLayout(self.page_host)
        self.page_layout.setContentsMargins(6, 6, 6, 6)
        self.page_layout.setSpacing(12)
        self.content_scroll.setWidget(self.page_host)
        outer.addWidget(self.content_scroll, 1)

    def clear_page(self):
        while self.page_layout.count():
            item = self.page_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def add_page_header(self, title, subtitle):
        row = QHBoxLayout()
        labels = QVBoxLayout()
        labels.addWidget(self.label(title, "Heading"))
        labels.addWidget(self.label(subtitle, "Muted", True))
        row.addLayout(labels, 1)
        theme = self.button(
            "☼ Light / Dark",
            self.toggle_theme
        )
        row.addWidget(theme, 0, Qt.AlignmentFlag.AlignTop)
        self.page_layout.addLayout(row)

    def show_page(self, page):
        self.active_page = page
        self.clear_page()

        for key, btn in self.nav_buttons.items():
            btn.setObjectName("NavActive" if key == page else "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if page == "Home":
            self.build_home()
        elif page == "Download":
            self.build_download_page()
        elif page == "History":
            self.build_history_page()
        elif page == "Pricing":
            self.build_pricing_page()
        elif page == "Payment":
            self.build_payment_page(self.payment_method)
        elif page == "License":
            self.build_license_page()
        elif page == "Support" or page == "Contact Us":
            self.build_support_page()
        elif page == "Privacy Policy":
            self.build_legal_page(page)
        elif page == "Terms & Conditions":
            self.build_legal_page(page)
        elif page == "EULA / License":
            self.build_legal_page(page)
        elif page == "About Us":
            self.build_legal_page(page)
        else:
            self.page_layout.addWidget(self.label("Page not found.", "Heading"))

        self.page_layout.addStretch()

    def build_home(self):
        hero, hero_layout = self.panel(self.page_layout, "Hero", (25, 24, 25, 24))
        hero_layout.addWidget(self.label("CLIPNOVA", "HeroTitle"))
        hero_layout.addWidget(self.label("Your All-in-One Video Downloader", "Section"))
        hero_layout.addWidget(self.label(
            "Download and manage supported video links from TikTok, YouTube, "
            "Facebook and Instagram. Choose quality and save files to your PC.",
            "Muted", True
        ))
        hero_buttons = QHBoxLayout()
        hero_buttons.addWidget(self.button("↓  Open Download Center", lambda: self.show_page("Download"), True))
        hero_buttons.addWidget(self.button("♛  View Plans", lambda: self.show_page("Pricing")))
        hero_layout.addLayout(hero_buttons)

        self.add_page_header("Welcome to ClipNova", "A cleaner workspace for downloads, payments and license details.")

        grid = QGridLayout()
        grid.setSpacing(12)
        cards = [
            ("01", "Download Queue", "Add multiple video links and track their progress.", "Download"),
            ("02", "Pricing Plans", "Compare the available plans.", "Pricing"),
            ("03", "Payment Methods", "View each transfer method and its QR code.", "Payment"),
            ("04", "License Activation", "Enter a license key to activate this local installation.", "License"),
        ]
        for index, (number, title, desc, target) in enumerate(cards):
            card = QFrame()
            card.setObjectName("Panel")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(18, 18, 18, 18)
            layout.addWidget(self.label(number, "Accent"))
            layout.addWidget(self.label(title, "Section"))
            layout.addWidget(self.label(desc, "Muted", True))
            layout.addStretch()
            layout.addWidget(self.button("Open  →", lambda checked=False, p=target: self.show_page(p), True))
            grid.addWidget(card, index // 2, index % 2)
        self.page_layout.addLayout(grid)

        features, fl = self.panel(self.page_layout)
        fl.addWidget(self.label("BUILT FOR YOUR WORKFLOW", "Section"))
        feature_row = QHBoxLayout()
        for title, desc in [
            ("Multiple Platforms", "Supported public links"),
            ("Queue Controls", "Pause, resume and stop"),
            ("Quality Options", "Available formats"),
        ]:
            card = QFrame()
            card.setObjectName("MiniPanel")
            cl = QVBoxLayout(card)
            cl.addWidget(self.label(title, "Section"))
            cl.addWidget(self.label(desc, "Muted", True))
            feature_row.addWidget(card)
        fl.addLayout(feature_row)

        self.page_layout.addWidget(self.label(
            "Please download only content you own or are authorized to save.",
            "Muted"
        ))

    def build_download_page(self):
        self.add_page_header("Download Center", "Paste one or more supported links and manage your queue.")

        link_panel, link_layout = self.panel(self.page_layout)
        link_layout.addWidget(self.label("SELECT PLATFORM", "Section"))

        platform_row = QHBoxLayout()
        self.platform_buttons = {}
        for name, glyph in [
            ("TikTok", "♪"), ("YouTube", "▶"),
            ("Facebook", "f"), ("Instagram", "◎")
        ]:
            btn = QPushButton(f"{glyph}  {name}")
            btn.setMinimumHeight(42)
            btn.clicked.connect(lambda checked=False, n=name: self.select_platform(n))
            platform_row.addWidget(btn)
            self.platform_buttons[name] = btn
        link_layout.addLayout(platform_row)

        self.auto_detect = QCheckBox("Auto-detect platform (allow mixed links)")
        self.auto_detect.setChecked(True)
        self.auto_detect.toggled.connect(self.on_auto_detect_changed)
        link_layout.addWidget(self.auto_detect)

        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText(
            "Paste video URL(s) here — one link per line. "
            "Supported: TikTok, YouTube, Facebook and Instagram."
        )
        self.url_input.setMinimumHeight(90)
        self.url_input.setMaximumHeight(125)
        link_layout.addWidget(self.url_input)

        controls = QHBoxLayout()
        self.quality = QComboBox()
        self.quality.addItems(["Best available", "1080p", "720p", "480p", "MP3 Audio"])
        controls.addWidget(self.label("Quality"))
        controls.addWidget(self.quality)

        self.folder_display = QLineEdit(self.download_folder)
        self.folder_display.setReadOnly(True)
        controls.addWidget(self.folder_display, 1)
        controls.addWidget(self.button("Browse", self.choose_folder))
        controls.addWidget(self.button("Paste", self.paste_clipboard))
        controls.addWidget(self.button("＋ Add to Queue", self.add_to_queue, True))
        link_layout.addLayout(controls)

        queue_panel, queue_layout = self.panel(self.page_layout)
        qtop = QHBoxLayout()
        qtop.addWidget(self.label("DOWNLOAD QUEUE", "Section"))
        qtop.addStretch()
        qtop.addWidget(self.button("Clear Queue", self.clear_queue))
        queue_layout.addLayout(qtop)

        self.queue_summary = self.label("Total: 0  •  Completed: 0  •  Downloading: 0  •  Failed: 0", "Muted")
        queue_layout.addWidget(self.queue_summary)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Platform", "Video Link", "Status", "Progress", "Details"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(240)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        queue_layout.addWidget(self.table)

        self.overall = QProgressBar()
        self.overall.setRange(0, 100)
        queue_layout.addWidget(self.overall)

        actions = QHBoxLayout()
        self.start_button = self.button("▶ Download", self.start_downloads, True)
        self.pause_button = self.button("Ⅱ Pause", self.pause_downloads)
        self.resume_button = self.button("▶ Resume", self.resume_downloads)
        self.stop_button = self.button("■ Stop", self.stop_downloads)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        for btn in [self.start_button, self.pause_button, self.resume_button, self.stop_button]:
            actions.addWidget(btn)
        actions.addWidget(self.button("Open Download Folder", self.open_folder))
        queue_layout.addLayout(actions)

        self.status_line = self.label("Ready — paste a link to begin.", "Muted")
        queue_layout.addWidget(self.status_line)

    def on_auto_detect_changed(self, checked):
        if checked:
            self.selected_platform = "Auto Detect"

    def select_platform(self, name):
        self.selected_platform = name
        self.auto_detect.setChecked(False)
        self.status_line.setText(f"{name} selected. Paste a {name} link, or enable Auto-detect for mixed links.")

    def paste_clipboard(self):
        self.url_input.insertPlainText(QApplication.clipboard().text())

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Download Folder", self.download_folder)
        if folder:
            self.download_folder = folder
            self.folder_display.setText(folder)

    def add_to_queue(self):
        raw = self.url_input.toPlainText().strip()
        if not raw:
            QMessageBox.information(self, "No links", "Paste one or more video links first.")
            return

        urls = extract_urls(raw)
        if not urls:
            QMessageBox.warning(self, "Unsupported links", "Enter a supported Facebook, TikTok, YouTube or Instagram URL.")
            return

        existing = {
            self.table.item(row, 1).text()
            for row in range(self.table.rowCount())
            if self.table.item(row, 1)
        }
        added = 0
        duplicates = 0

        for url in urls:
            if url in existing:
                duplicates += 1
                continue

            platform = platform_for(url)
            if not self.auto_detect.isChecked() and self.selected_platform != platform:
                QMessageBox.warning(
                    self, "Platform mismatch",
                    f"This link appears to be {platform}, not {self.selected_platform}."
                )
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, value in enumerate([platform, url, "Queued", "0%", "Waiting to start"]):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
            self.table.setRowHeight(row, 30)
            existing.add(url)
            added += 1

        self.url_input.clear()
        self.update_metrics()
        self.status_line.setText(f"Added {added} link(s). Duplicate links skipped: {duplicates}.")

    def update_metrics(self):
        if not hasattr(self, "table"):
            return
        total = self.table.rowCount()
        counts = {}
        for row in range(total):
            item = self.table.item(row, 2)
            status = item.text() if item else "Unknown"
            counts[status] = counts.get(status, 0) + 1
        self.queue_summary.setText(
            f"Total: {total}  •  Completed: {counts.get('Completed', 0)}"
            f"  •  Downloading: {counts.get('Downloading', 0)}"
            f"  •  Failed: {counts.get('Failed', 0)}"
        )

    def start_downloads(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "Already running", "Use Pause, Resume or Stop.")
            return

        jobs = []
        for row in range(self.table.rowCount()):
            status = self.table.item(row, 2).text()
            if status not in ("Completed", "Downloading", "Preparing"):
                jobs.append((row, self.table.item(row, 1).text()))

        if not jobs:
            QMessageBox.information(self, "Nothing to download", "Add links to the queue first.")
            return

        os.makedirs(self.download_folder, exist_ok=True)
        self.worker = DownloadWorker(jobs, self.download_folder, self.quality.currentText())
        self.worker.status_changed.connect(self.on_status)
        self.worker.progress_changed.connect(self.on_progress)
        self.worker.item_finished.connect(self.on_item_finished)
        self.worker.all_finished.connect(self.on_all_finished)

        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.resume_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_line.setText(f"Starting {len(jobs)} download(s)...")
        self.worker.start()

    def pause_downloads(self):
        if self.worker and self.worker.isRunning():
            self.worker.pause()
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)
            self.status_line.setText("Pause requested.")

    def resume_downloads(self):
        if self.worker and self.worker.isRunning():
            self.worker.resume()
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)
            self.status_line.setText("Resume requested.")

    def stop_downloads(self):
        if self.worker and self.worker.isRunning():
            answer = QMessageBox.question(
                self, "Stop downloads?",
                "Stop the current transfer? Partial files may be resumable.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if answer == QMessageBox.StandardButton.Yes:
                self.worker.stop()
                self.pause_button.setEnabled(False)
                self.resume_button.setEnabled(False)
                self.stop_button.setEnabled(False)
                self.status_line.setText("Stopping safely. Please wait...")

    def on_status(self, row, status):
        if row < self.table.rowCount():
            self.table.item(row, 2).setText(status)
            self.update_metrics()

    def on_progress(self, row, percent, details):
        if row < self.table.rowCount():
            self.table.item(row, 3).setText(f"{percent}%")
            self.table.item(row, 4).setText(details)
            self.overall.setValue(percent)

    def on_item_finished(self, row, status, message):
        if row < self.table.rowCount():
            self.table.item(row, 2).setText(status)
            self.table.item(row, 4).setText(message)
        self.update_metrics()

    def on_all_finished(self):
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        remaining = sum(
            1 for row in range(self.table.rowCount())
            if self.table.item(row, 2).text() in ("Queued", "Stopped")
        )
        self.status_line.setText(f"Finished. Remaining queued/stopped items: {remaining}.")
        self.update_metrics()
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def clear_queue(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Downloads running", "Stop downloads and wait before clearing.")
            return
        if not self.table.rowCount():
            return
        answer = QMessageBox.question(
            self, "Clear queue?", "Remove all queued items?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.table.setRowCount(0)
            self.overall.setValue(0)
            self.update_metrics()
            self.status_line.setText("Queue cleared.")

    def open_folder(self):
        os.makedirs(self.download_folder, exist_ok=True)
        try:
            if sys.platform == "win32":
                os.startfile(self.download_folder)
            else:
                subprocess.Popen(["xdg-open", self.download_folder])
        except Exception as exc:
            QMessageBox.warning(self, "Folder error", str(exc))

    def build_history_page(self):
        self.add_page_header("Download History", "History for the current app session.")
        panel, layout = self.panel(self.page_layout)
        layout.addWidget(self.label("CURRENT SESSION", "Section"))

        if not hasattr(self, "table") or self.table.rowCount() == 0:
            layout.addWidget(self.label("No downloads in this session yet.", "Muted", True))
            return

        history = QTableWidget(self.table.rowCount(), 4)
        history.setHorizontalHeaderLabels(["Platform", "Video Link", "Status", "Details"])
        history.setAlternatingRowColors(True)
        history.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        history.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        for row in range(self.table.rowCount()):
            for col, source_col in enumerate((0, 1, 2, 4)):
                source = self.table.item(row, source_col)
                history.setItem(row, col, QTableWidgetItem(source.text() if source else ""))
        layout.addWidget(history)

    def build_pricing_page(self):
        self.add_page_header("Pricing Plans", "Compare daily and total download quotas before choosing a plan. Payment confirmation is manual.")

        free_card = QFrame()
        free_card.setObjectName("Hero")
        free_row = QHBoxLayout(free_card)
        free_row.setContentsMargins(18, 16, 18, 16)
        free_labels = QVBoxLayout()
        free_labels.addWidget(self.label("FREE • AD-SUPPORTED", "Section"))
        free_labels.addWidget(self.label("PKR 0", "Accent"))
        free_labels.addWidget(self.label(FREE_PLAN_DETAILS, "Muted", True))
        free_row.addLayout(free_labels, 1)
        free_row.addWidget(self.button("Use Free Plan", lambda: QMessageBox.information(self, "Free plan", "Free plan details: 100 videos/day. When the daily quota is reached, a verified rewarded ad is intended to unlock one additional video. Rewarded-ad provider integration and server-side quota enforcement must be enabled before this is available in a public release."), True))
        self.page_layout.addWidget(free_card)

        for name, price, detail in PLANS:
            card = QFrame()
            card.setObjectName("Panel")
            row = QHBoxLayout(card)
            row.setContentsMargins(18, 16, 18, 16)
            labels = QVBoxLayout()
            labels.addWidget(self.label(name, "Section"))
            labels.addWidget(self.label(price, "Accent"))
            labels.addWidget(self.label(detail, "Muted", True))
            row.addLayout(labels, 1)
            choose = self.button(
                "Choose Plan  →",
                lambda checked=False, plan=name: self.choose_plan(plan),
                True
            )
            row.addWidget(choose)
            self.page_layout.addWidget(card)

        note, nl = self.panel(self.page_layout, "MiniPanel")
        nl.addWidget(self.label("How activation works", "Section"))
        nl.addWidget(self.label(
            "1. Select a plan.  2. Pay using one of the displayed methods. "
            "3. Send the receipt to support. 4. After payment confirmation, "
            "request your license key and enter it on the License page.",
            "Muted", True
        ))

    def choose_plan(self, plan):
        self.selected_plan = plan
        self.show_page("Payment")

    def build_payment_page(self, method=None):
        method = method if method in PAYMENT_METHODS else "Meezan Bank"
        self.payment_method = method
        self.add_page_header("Secure Payment Options", "Choose one method below. Each payment method has its own details and QR image.")

        selector, selector_layout = self.panel(self.page_layout)
        selector_layout.addWidget(self.label("SELECT PAYMENT METHOD", "Section"))
        row = QHBoxLayout()
        for name, details in PAYMENT_METHODS.items():
            btn = QPushButton(f"{name}\n{details['description']}")
            btn.setMinimumHeight(65)
            btn.clicked.connect(lambda checked=False, n=name: self.show_page_payment(n))
            row.addWidget(btn)
        selector_layout.addLayout(row)

        self.render_payment_method(method)

        crypto, crypto_layout = self.panel(self.page_layout, "MiniPanel")
        crypto_layout.addWidget(self.label("Cryptocurrency", "Section"))
        crypto_layout.addWidget(self.label(
            "Crypto payments are not enabled yet because verified wallet addresses and QR codes "
            "have not been supplied. Do not send funds to an unverified address.",
            "Muted", True
        ))

    def show_page_payment(self, method):
        self.payment_method = method
        self.show_page("Payment")

    def render_payment_method(self, method):
        data = PAYMENT_METHODS[method]
        card, layout = self.panel(self.page_layout, "Panel", (20, 18, 20, 18))
        layout.addWidget(self.label(method, "Heading"))
        layout.addWidget(self.label(data["description"], "Accent"))

        body = QHBoxLayout()
        details_layout = QVBoxLayout()
        details_layout.addWidget(self.label("PAYMENT DETAILS", "Section"))
        details_layout.addWidget(self.label(f"Account title: {data['title']}", None, True))

        copy_text = [f"Payment method: {method}", f"Account title: {data['title']}"]
        for label_text, value in data["details"]:
            details_layout.addWidget(self.label(f"{label_text}: {value}", None, True))
            copy_text.append(f"{label_text}: {value}")

        details_layout.addSpacing(8)
        details_layout.addWidget(self.label(
            "After payment, contact support and send your transaction receipt. "
            "Your license is issued after payment verification.",
            "Muted", True
        ))

        copy_btn = self.button("Copy Payment Details", lambda: self.copy_text("\n".join(copy_text)), True)
        details_layout.addWidget(copy_btn)
        details_layout.addWidget(self.button("Open WhatsApp Support", lambda: self.open_url("https://wa.me/923139818400")))
        body.addLayout(details_layout, 1)

        qr_path = find_payment_image(data["qr"])
        if qr_path:
            pixmap = QPixmap(str(qr_path))
        else:
            pixmap = QPixmap()

        qr_box = QFrame()
        qr_box.setObjectName("MiniPanel")
        qr_layout = QVBoxLayout(qr_box)
        qr_layout.setContentsMargins(12, 12, 12, 12)
        qr_layout.addWidget(self.label("SCAN TO PAY", "Section"))

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setMinimumSize(220, 220)
        image_label.setMaximumSize(250, 250)

        if not pixmap.isNull():
            image_label.setPixmap(pixmap.scaled(
                220, 220,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            image_label.setToolTip(str(qr_path))
            qr_layout.addWidget(image_label)
            qr_layout.addWidget(self.label(f"Image: {qr_path.name}", "Muted"))
        else:
            image_label.setText("QR image not found")
            image_label.setWordWrap(True)
            image_label.setStyleSheet("border:1px dashed #8496ba;border-radius:10px;padding:20px;")
            qr_layout.addWidget(image_label)
            expected = self.label(
                f"Expected filename:\n{data['qr']}\n\n"
                "Place it in:\nassets/payments/\n\n"
                "Full expected path:\n"
                f"{resource_path('assets', 'payments', data['qr'])}",
                "Muted", True
            )
            qr_layout.addWidget(expected)

        body.addWidget(qr_box, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(body)

        note, note_layout = self.panel(self.page_layout, "MiniPanel")
        note_layout.addWidget(self.label("Important", "Section"))
        note_layout.addWidget(self.label(
            "Please verify the account title and number before transferring. "
            "Keep your receipt. Do not send money if the displayed details do not match "
            "the payment instructions you received.",
            "Muted", True
        ))

    def copy_text(self, text):
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Payment details copied to clipboard.")

    def build_license_page(self):
        self.add_page_header("License Activation", "Enter a license key after your payment has been verified.")

        current = load_json(ACTIVE_LICENSE_FILE, {})
        panel, layout = self.panel(self.page_layout)
        layout.addWidget(self.label("YOUR LICENSE", "Section"))

        if current.get("key") and current.get("plan"):
            layout.addWidget(self.label(f"Plan: {current.get('plan', 'Unknown')}", "Accent"))
            layout.addWidget(self.label(f"License key: {current.get('key', '')}", "Muted", True))
            layout.addWidget(self.label("Status: Activated on this local installation", "Accent"))
        else:
            layout.addWidget(self.label("Status: No active license on this installation.", "Muted", True))

        activate, activate_layout = self.panel(self.page_layout)
        activate_layout.addWidget(self.label("ACTIVATE A LICENSE KEY", "Section"))
        activate_layout.addWidget(self.label(
            "Enter the license key supplied by the seller. Activation is checked by the online ClipNova license server.",
            "Muted", True
        ))

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("Example: CN-AB12-CD34-EF56")
        activate_layout.addWidget(self.license_input)
        activate_layout.addWidget(self.button("Activate License", self.activate_license, True))

        admin, admin_layout = self.panel(self.page_layout, "MiniPanel")
        admin_layout.addWidget(self.label("SELLER / ADMIN TOOLS", "Section"))
        admin_layout.addWidget(self.label(
            "The local manager below is a development tool. It does not securely verify licenses "
            "across separate customer computers without an online verification service.",
            "Muted", True
        ))
        admin_layout.addWidget(self.button("Open Local License Manager", self.open_license_manager))

        support, support_layout = self.panel(self.page_layout)
        support_layout.addWidget(self.label("Need a key?", "Section"))
        support_layout.addWidget(self.label(
            "Select a plan, complete payment, and send your receipt to support. "
            "A key should only be issued after the payment is verified.",
            "Muted", True
        ))
        support_layout.addWidget(self.button("Contact WhatsApp Support", lambda: self.open_url("https://wa.me/923139818400")))

   
    def validate_saved_license(self):
        """Check the saved license with the server without changing device assignments."""
        current = load_json(ACTIVE_LICENSE_FILE, {})
        key = str(current.get("key", "")).strip().upper()
        device_id = str(current.get("device_id", "")).strip()
        if not key or not device_id:
            return

        server_url = "https://clipnova-license-server.immrilyas.workers.dev"
        try:
            response = requests.post(
                f"{server_url}/license/validate",
                json={"license_key": key, "device_id": device_id},
                timeout=8,
            )
            try:
                result = response.json()
            except ValueError:
                result = {}

            if response.ok and result.get("success") and result.get("valid"):
                current["plan"] = result.get("plan", current.get("plan", "Unknown"))
                current["expires_at"] = result.get("expires_at", current.get("expires_at"))
                current["last_verified_at"] = __import__("datetime").datetime.now().isoformat(timespec="seconds")
                save_json(ACTIVE_LICENSE_FILE, current)
                return

            detail = result.get("detail", result.get("message", "The saved license could not be verified."))
            QMessageBox.warning(
                self, "License verification failed",
                f"The license server did not validate this saved license.\n\n{detail}\n\n"
                "Your saved license file has not been deleted. Open License and activate a valid key if needed."
            )
        except requests.exceptions.RequestException:
            # Do not lock the user out solely because the server/network is temporarily unavailable.
            QMessageBox.warning(
                self, "License server unavailable",
                "ClipNova could not verify the saved license online at startup.\n"
                "Check your internet connection and try again. The saved license was not changed."
            )

    def activate_license(self):
        import uuid
        import requests
        from pathlib import Path

        key = self.license_input.text().strip().upper()

        if not key:
            QMessageBox.warning(
                self, "Missing key", "Enter your license key first."
            )
            return

        # Development server: local PC only
        server_url = "https://clipnova-license-server.immrilyas.workers.dev"

        # Keep a stable device ID for this PC
        app_data = Path.home() / "AppData" / "Local" / "ClipNova"
        app_data.mkdir(parents=True, exist_ok=True)
        device_file = app_data / "device_id.txt"

        if device_file.exists():
            device_id = device_file.read_text(encoding="utf-8").strip()
        else:
            device_id = str(uuid.uuid4())
            device_file.write_text(device_id, encoding="utf-8")

        try:
            response = requests.post(
                f"{server_url}/license/activate",
                json={
                    "license_key": key,
                    "device_id": device_id
                },
                timeout=15
            )

            try:
                result = response.json()
            except ValueError:
                result = {}

            if response.ok and result.get("success"):
                plan = result.get("plan", "Unknown")

                save_json(ACTIVE_LICENSE_FILE, {
                    "key": key,
                    "plan": plan,
                    "device_id": device_id,
                    "expires_at": result.get("expires_at"),
                    "activated_at": __import__("datetime").datetime.now().isoformat(
                        timespec="seconds"
                    ),
                })

                QMessageBox.information(
                    self, "Activated",
                    f"License activated successfully!\nPlan: {plan}"
                )
                self.show_page("License")
            else:
                message = result.get(
                    "message",
                    result.get("detail", "The license could not be activated.")
                )
                QMessageBox.warning(self, "Activation failed", str(message))

        except requests.exceptions.RequestException as exc:
            QMessageBox.critical(
                self, "Server unavailable",
                "Could not complete the request to the ClipNova license server.\n"
                f"Details: {exc}"
            )

    def build_support_page(self):
        self.add_page_header("Support Center", "Contact support about payments, license activation or app issues.")

        card, layout = self.panel(self.page_layout)
        layout.addWidget(self.label("WE'RE HERE TO HELP", "Heading"))
        layout.addWidget(self.label(
            "For payment confirmation, include the selected plan, payment method, transaction receipt "
            "and the email or contact information you want associated with your order.",
            "Muted", True
        ))
        layout.addWidget(self.button("WhatsApp  •  +92 313 9818400", lambda: self.open_url("https://wa.me/923139818400"), True))
        layout.addWidget(self.button("Email  •  immrilyas@gmail.com", lambda: self.open_url("mailto:immrilyas@gmail.com")))

        faq, faq_layout = self.panel(self.page_layout)
        faq_layout.addWidget(self.label("COMMON QUESTIONS", "Section"))
        questions = [
            ("Where do I enter my key?", "Open License from the sidebar, enter your key and press Activate License."),
            ("Why is my QR code missing?", "Make sure the image filename matches the expected filename and the image is in assets/payments."),
            ("When will my license be issued?", "After the seller verifies your payment and issues the key."),
            ("Does activation sync across PCs?", "License activations are managed by the online ClipNova license server and are subject to the device limit on your plan."),
        ]
        for question, answer in questions:
            faq_layout.addWidget(self.label(question, "Section"))
            faq_layout.addWidget(self.label(answer, "Muted", True))

    def build_legal_page(self, page):
        self.add_page_header(page, "ClipNova information and policies.")
        panel, layout = self.panel(self.page_layout)
        content = {
            "Privacy Policy": """
ClipNova Privacy Policy

1. Information handled
ClipNova processes the video links that you enter and the download settings you select. Downloaded files are saved to the local folder selected in the application.

2. Local processing
This desktop build does not provide a ClipNova user-account service. Downloading is performed through yt-dlp and the source platform. The source platform may process requests according to its own policies.

3. Payment informationexcept requests.exceptions.Timeout:
            QMessageBox.warning(
                self, "Request timed out",
                "The license server took too long to respond. Please try again."
            )
        except requests.exceptions.RequestException as exc:
            QMessageBox.critical(
                self, "Connection error", str(exc)
            )

        dlg.setWindowTitle("ClipNova | Local License Manager")
        dlg.resize(720, 610)
        dlg.setStyleSheet(self.styleSheet())
        root = QVBoxLayout(dlg)

        root.addWidget(self.label("Local License Manager", "Heading"))
        root.addWidget(self.label(
            "Development prototype only. Keys created here are stored in this PC's local database. "
            "This is not secure production licensing and does not sync to customer devices.",
            "Muted", True
        ))

        form, form_layout = self.panel(root)
        form_layout.addWidget(self.label("GENERATE LICENSE", "Section"))
        plan_box = QComboBox()
        plan_box.addItems([p[0] for p in PLANS])
        form_layout.addWidget(plan_box)

        months = QSpinBox()
        months.setRange(0, 120)
        months.setValue(12)
        months.setSpecialValueText("Lifetime")
        form_layout.addWidget(self.label("Validity in months (0 = lifetime)", "Muted"))
        form_layout.addWidget(months)

        key_output = QLineEdit()
        key_output.setReadOnly(True)
        form_layout.addWidget(key_output)

        def generate_key():
            alphabet = string.ascii_uppercase + string.digits
            parts = ["".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(4)]
            key = "CN-" + "-".join(parts)
            licenses = load_json(LICENSE_FILE, {})
            while key in licenses:
                parts = ["".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(4)]
                key = "CN-" + "-".join(parts)

            months_value = months.value()
            expiry = None
            if months_value > 0:
                from datetime import datetime, timedelta
                expiry = (datetime.now() + timedelta(days=30 * months_value)).date().isoformat()

            licenses[key] = {
                "plan": plan_box.currentText(),
                "revoked": False,
                "expires": expiry,
                "created_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
            }
            save_json(LICENSE_FILE, licenses)
            key_output.setText(key)
            refresh_table()
            QMessageBox.information(
                dlg, "Key created",
                "The key was saved in this PC's local license database.\n\n"
                "It will not activate on another PC unless that installation has the corresponding record."
            )

        form_layout.addWidget(self.button("Generate New Key", generate_key, True))
        form_layout.addWidget(self.button("Copy Generated Key", lambda: self.copy_text(key_output.text())))

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["License Key", "Plan", "Status", "Expiry"])
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        root.addWidget(table, 1)

        def refresh_table():
            licenses = load_json(LICENSE_FILE, {})
            table.setRowCount(0)
            for key, entry in licenses.items():
                row = table.rowCount()
                table.insertRow(row)
                status = "Revoked" if entry.get("revoked") else "Active"
                values = [key, entry.get("plan", ""), status, entry.get("expires") or "Lifetime"]
                for col, value in enumerate(values):
                    table.setItem(row, col, QTableWidgetItem(str(value)))

        def revoke_selected():
            row = table.currentRow()
            if row < 0:
                QMessageBox.information(dlg, "Select key", "Select a license from the table first.")
                return
            key_item = table.item(row, 0)
            if not key_item:
                return
            key = key_item.text()
This build does not include an integrated payment gateway. Payments are arranged manually. Do not enter banking passwords, card security codes, cryptocurrency seed phrases or private keys into the app.

4. Data storage
The local prototype may store license records on this computer. Protect access to your Windows account and files.

5. Advertising and rewarded downloads
The planned free tier may show ads. If rewarded ads are enabled, an extra download should be granted only after the ad provider verifies a completed ad. Ads are not intended for paid plans. These features depend on the active release and configured ad provider; this source build does not itself prove that an ad provider is integrated.

6. Contact
For privacy questions, contact immrilyas@gmail.com.
""",
            "Terms & Conditions": """
ClipNova Terms and Conditions

1. Authorized use
Use ClipNova only for content you own or have permission to download. Respect copyright, platform terms and applicable laws.

2. Platform availability
Supported sites may change their technical systems. A link, format or quality that works today may not work later.

3. Downloads and conversion
Available formats depend on the source, yt-dlp support and whether FFmpeg is installed. No particular quality or availability is guaranteed.

4. Payments and plans
Displayed prices describe the plans offered by the seller. Payment must be verified before a license is issued. Do not assume that clicking a plan button completes a purchase.

5. Plan quotas and ads
The currently planned quotas are: Free 100/day; Monthly Starter 300/day and 15,000/month; Monthly Premium 800/day and 40,000/month; Lifetime Starter Plus 1,000/day and 80,000 lifetime; Lifetime Ultra Pro unlimited. Paid plans are intended to be ad-free. Quotas and rewarded-ad access are enforceable only when server-side quota and ad verification services are deployed and active. Do not rely on the displayed plan card alone as proof of enforcement.

6. License
A valid license is subject to its stated plan and terms. Do not redistribute keys or attempt to bypass license restrictions.

7. Contact
For questions, contact immrilyas@gmail.com.
""",
            "EULA / License": """
ClipNova End User License Agreement

1. License grant
Subject to the plan purchased and verified by the seller, the user may install and use the licensed ClipNova application for the permitted purpose.

2. Restrictions
Do not claim ownership of the application, redistribute paid builds without authorization, or use the application to violate others' rights.

3. License activation
This build includes a local development license manager. Local records are not a secure online licensing service and do not automatically synchronize between computers.

4. No guarantee of service
External platforms, codecs and download methods can change. The application may require updates to continue working.

5. Termination
A license may be revoked according to the applicable purchase terms.

6. Contact
For licensing questions, contact immrilyas@gmail.com.
""",
            "About Us": """
About ClipNova

ClipNova is a Windows desktop interface for managing video downloads from supported URLs. It is built with Python, PySide6 and yt-dlp.

Features include:
• A download queue
• Quality selection where supported
• Download progress and status information
• A selectable destination folder
• Payment information and license activation screens

This source build contains plan descriptions, but those descriptions alone do not enforce download quotas. Payment verification is manual. Server-side quota tracking and verified rewarded-ad integration must be deployed and tested before advertising the quota system as fully enforced.

Contact: immrilyas@gmail.com
WhatsApp: +92 313 9818400
""",
        }
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(content.get(page, "Information not available."))
        text.setMinimumHeight(440)
        layout.addWidget(text)

    def open_url(self, url):
        webbrowser.open(url)

    def apply_theme(self):
        self.setStyleSheet(DARK_STYLE if self.dark_mode else LIGHT_STYLE)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        current = self.active_page
        if current:
            self.show_page(current)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            answer = QMessageBox.question(
                self, "Downloads running",
                "Downloads are still running. Stop and close ClipNova?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.worker.stop()
            self.worker.wait(5000)
            if self.worker.isRunning():
                QMessageBox.warning(self, "Still stopping", "Wait for the download to stop and try again.")
                event.ignore()
                return
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setFont(QFont("Segoe UI", 10))
    window = ClipNovaWindow()
    window.setWindowOpacity(0.0)
    window.show()
    window._intro_animation = QPropertyAnimation(window, b"windowOpacity", window)
    window._intro_animation.setDuration(420)
    window._intro_animation.setStartValue(0.0)
    window._intro_animation.setEndValue(1.0)
    window._intro_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    window._intro_animation.start()
    sys.exit(app.exec())

if __name__ == "__main__":

    main()