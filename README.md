# ZygorGuideLoader 🐉

**Modular Guide Loading to reduce CPU strain and eliminate loading screen lag in World of Warcraft.**

<p align="center">
  <img src="https://i.imgur.com/wMwsM5e.png" alt="ZygorGuideLoader">
</p>

By default, Zygor Guides loads every single module (Achievements, Leveling, Dungeons, Pets, etc.) into your RAM during the loading screen. For high-end setups aiming for maximum performance, this causes massive FPS drops and client freezes (up to 4+ seconds of lag).

**ZygorGuideLoader** is a standalone utility that patches the `Autoload.xml` file, allowing you to load only the specific content you need for your current session.

## ✨ Features

- **Faster Loading Time:** Eliminates CPU bottlenecks during loading screens.
- **Master Faction Toggles:** New switches to instantly enable/disable **Alliance**, **Horde**, or **Neutral** guides globally.
- **Modern GUI:** Sleek, dark-themed interface built with `customtkinter`.
- **Persistent State:** Automatically detects your current guide status and remembers your last selection.
- **Smart Backups:** Creates a `Autoload_Official_Backup.xml` on the first run to ensure you can always revert to the original state.

## 🚀 How to Use (For Standard Users)

1. Download the latest `ZygorGuideLoader.exe` from the [Releases](../../releases) tab.
2. Run the executable.
3. Click **"Select World of Warcraft Folder"** (the app will attempt to auto-detect your path via the Windows Registry).
4. Use the **Master Toggles** at the top to filter by Faction.
5. Manually toggle off specific categories (e.g., disable _PetsMounts_ or _Achievements_ to save memory).
6. Click **"Patch & Ready!"**.
7. Experience faster loading times.

## 💻 Development & Compilation

If you want to run the source code or compile it yourself:

### Prerequisites

- **Python 3.10+**
- `customtkinter` library

### Cloning the repository:\*\*

git clone [https://github.com/Nexus-Hub/ZygorGuideLoader.git](https://github.com/Nexus-Hub/ZygorGuideLoader.git)
Install requirements: pip install customtkinter
Run the script: python main.py

Compiling to .exe
To build the standalone executable yourself with the embedded icon, run the following command in your terminal:
python -m PyInstaller --noconsole --onefile --collect-all customtkinter --icon=favicon.ico --add-data "favicon.ico;." main.py

The executable will be generated inside the /dist/ directory.

📝 **Author** Developed by **cadmnexus**. <img src="favicon.ico" width="20" height="20">
