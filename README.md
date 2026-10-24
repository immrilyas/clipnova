# ClipNova — Video Downloader for Windows

**ClipNova is a Python-based media downloader designed to make downloading and managing supported online media easier through a desktop application.**

ClipNova uses Python, PySide6, and yt-dlp to provide a graphical interface for supported media-download workflows.

> **Project status:** Under development. Features, supported platforms, and installation requirements are subject to testing.

## Features

- Windows desktop application with a graphical user interface
- Video and audio format selection, where supported
- Download queue and download status management
- Download progress tracking
- Pause, resume, and stop controls, subject to implementation and extractor support
- Download folder management
- Media processing support through FFmpeg, where required
- Support for compatible media sources through yt-dlp
- License management integration, subject to server configuration

## Technology Stack

- Python
- PySide6 and Qt for the desktop interface
- yt-dlp for media extraction
- FFmpeg for supported media-processing tasks
- FastAPI for the separate license-server component

## Installation Guide

### Requirements

Before installing ClipNova, make sure you have:

- A compatible Windows computer
- A supported Python version
- Git, if you want to clone the repository
- FFmpeg, if required by the selected download formats

### Step 1: Download the source code

Clone the repository or download the source code from GitHub.

```powershell
git clone https://github.com/immrilyas/clipnova.git
cd clipnova
```

### Step 2: Create a virtual environment

```powershell
py -m venv .venv
```

### Step 3: Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell activation is blocked, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### Step 4: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Run ClipNova

```powershell
python app.py
```

These instructions will be finalized after the repository's dependency list and application entry point have been verified.

## FFmpeg Setup

Some media formats and merging operations require FFmpeg. Install a compatible FFmpeg build and make sure its executable is discoverable by ClipNova.

## License Management

ClipNova's licensing functionality may require a separately configured license server. Server URLs, administrator credentials, private keys, and other secrets must never be published in the source repository.

## Troubleshooting

**Python is not recognized**

Install Python and verify that the Python launcher or executable is available.

**Dependencies cannot be installed**

Activate the project's virtual environment and check that `requirements.txt` contains the required packages.

**A media URL fails**

The source website may have changed, may require authentication, or may not be supported by the installed yt-dlp version.

**FFmpeg is not detected**

Check the FFmpeg installation and verify that ClipNova can locate its executable.

## Responsible Use

Download only content you own, have permission to download, or are legally entitled to access. Respect copyright, privacy, and the applicable terms of third-party services.

ClipNova does not promise compatibility with every website and does not authorize bypassing DRM or other access restrictions.

## Contributing

Bug reports, feature suggestions, and constructive contributions are welcome. Please provide clear reproduction steps when reporting an issue.

## Security

Do not submit API keys, passwords, license-server credentials, private user data, or production configuration files to the repository.

## Project License

No open-source license has been selected in this repository yet. Until a license is added, do not assume that the code is available for unrestricted reuse or redistribution.

## Disclaimer

ClipNova is an independent project and is not affiliated with or endorsed by YouTube, Facebook, Instagram, TikTok, or other third-party services.

---

**ClipNova — Built with Python for media-download workflows.**
