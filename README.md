# ClipNova — Python Video Downloader for Windows

**ClipNova** is a Windows video downloader application built with Python, PySide6, and yt-dlp. It is being developed to provide a desktop interface for managing supported media downloads, download queues, and video quality options.

Explore the source code, development progress, and setup instructions for this Python desktop application.

> **Project status:** Under development. Features, installation steps, and platform compatibility should be verified against the current source code before release.

## Key Features

- **Desktop interface:** A graphical Windows application built with PySide6.
- **Media downloads:** Uses yt-dlp to process supported media URLs.
- **Multiple platforms:** Designed to support compatible URLs from YouTube, Facebook, TikTok, and Instagram, subject to platform restrictions and current extractor support.
- **Download queue:** Organize supported download tasks in the application.
- **Quality options:** Provides configured media quality and audio download options where supported.
- **Download management:** Includes download controls and history features where implemented in the current version.
- **Python source code:** A codebase for developers interested in Python desktop applications and media-download tools.

Feature availability may change during development.

## Technology Stack

- **Python** — application programming language
- **PySide6** — desktop graphical user interface
- **yt-dlp** — supported media extraction and download engine
- **FFmpeg** — media processing and audio/video conversion when required
- **PyInstaller** — packaging Python applications for distribution
- **Requests** — HTTP requests where used by the application

## System Requirements

- Windows 10 or Windows 11
- A compatible Python version
- Git, if cloning the repository
- An internet connection for supported online downloads
- FFmpeg when required by the selected media format or processing feature

Check the project files for the currently tested Python version and dependencies.

## Installation Guide

### 1. Clone the Repository

Open PowerShell or Command Prompt and run:

```bash
git clone https://github.com/immrilyas/clipnova.git
cd clipnova
```

### 2. Create a Virtual Environment

```bash
py -m venv .venv
```

### 3. Activate the Environment

For PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

For Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Run ClipNova

If `app.py` is the application's current entry point, run:

```bash
python app.py
```

These instructions must be checked against the latest repository files before being used for a public release.

## FFmpeg Setup

Some media formats and audio/video processing operations require FFmpeg.

Install FFmpeg using a trusted source, ensure the required executable is accessible to ClipNova, and follow the setup instructions appropriate for your Windows environment.

## Troubleshooting

**Dependency installation fails**

Confirm that the virtual environment is activated, then run:

```bash
python -m pip check
```

**Python cannot find a required module**

Install the project's dependencies inside the active virtual environment:

```bash
python -m pip install -r requirements.txt
```

**A media URL cannot be downloaded**

The URL may be unsupported, private, unavailable, region-restricted, or affected by a change in the source platform. Check the current yt-dlp version and use only content you are authorized to access.

**FFmpeg is not detected**

Check that FFmpeg is installed and accessible to the application.

## Development

ClipNova is an evolving Python desktop application. Contributions, bug reports, and suggestions can help improve its reliability, usability, and documentation.

Before submitting a change:

1. Test the affected functionality.
2. Keep credentials, private configuration, and local license data out of Git.
3. Update documentation when setup instructions or features change.
4. Avoid claiming compatibility with platforms or features that have not been tested.

## Responsible Use

Use ClipNova only for content you own or are authorized to download. Follow the terms of service of the relevant platforms, applicable copyright laws, and local regulations.

ClipNova is an independent project and is not affiliated with or endorsed by YouTube, Facebook, TikTok, or Instagram.

## License

A public software license has not yet been specified. Until a license is added to the repository, do not assume that the source code is available for unrestricted reuse, modification, or redistribution.

## Project

**Repository:** https://github.com/immrilyas/clipnova

**Developer:** [@immrilyas](https://github.com/immrilyas)

For bug reports and feature suggestions, use the repository's GitHub Issues section when it is enabled.
