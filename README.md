# ClipNova — Windows Desktop App

ClipNova is a PySide6 desktop downloader for supported Facebook and TikTok URLs, powered by yt-dlp.

## What's included in this update
- Orange/amber accent theme replacing the previous purple/blue accent palette.
- A subtle fade-in when the app opens.
- Pricing cards that clearly describe Free, Monthly Starter, Monthly Premium, Lifetime Starter Plus, and Lifetime Ultra Pro quotas.
- EULA, Privacy Policy, Terms & Conditions drafts.
- `ClipNova_Setup.iss` for building a Windows installer with Inno Setup 6.
- Existing logo, icon, downloader, and online license activation files retained.

## Build the app on Windows
1. Install Python 3.11 or 3.12 (64-bit recommended).
2. Open this folder in a terminal and run `py -3 -m pip install -r requirements.txt` (or use your existing `.venv`).
3. Run `build_exe.bat`. PyInstaller output should be in `dist\ClipNova\`.
4. Install Inno Setup 6, open `ClipNova_Setup.iss`, and compile it.
5. Installer output should be in `installer_output\ClipNova_Setup_1.1.0.exe`.

## Important release status
The quota text in the UI documents the intended policy; it is not itself a secure quota enforcement system. Server-side quota tracking, atomic reservation/completion counting, and verified rewarded-ad callbacks still need to be implemented and deployed on the license server before publishing these limits as technically enforced. No real ad provider is configured in this package. Do not claim rewarded ads work until provider integration and verification are tested.

The legal documents are draft templates, not legal advice. Review them against the actual data flows and local law before commercial distribution. Verify payment details before release. Do not distribute `.env` files, databases, virtual environments, or server secrets with the desktop app.

## Plan policy currently shown
- Free: 100 downloads/day; ads intended; each verified completed rewarded ad should unlock 1 extra download after the daily quota.
- Monthly Starter: 300/day and 15,000/month; no ads.
- Monthly Premium: 800/day and 40,000/month; no ads.
- Lifetime Starter Plus: 1,000/day and 80,000 lifetime; no ads.
- Lifetime Ultra Pro: unlimited daily and lifetime downloads; no ads.

For technical limits, platform availability, and permitted use, consult the Terms and Conditions in the app and `Terms_and_Conditions.txt`.
