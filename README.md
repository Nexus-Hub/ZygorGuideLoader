# ZygorGuideLoader 🐉

**Modular Optimizer to eliminate loading screen lag in World of Warcraft when using Zygor.**
By default, Zygor Guides loads every every guide into memory during startup. This causes FPS drops and client freezes during load.

<p align="center">
  <img src="https://i.imgur.com/nZxY3dS.png" alt="ZygorGuideLoader by Nexus">
</p>

<p align="center">
  <img src="https://i.imgur.com/qIFmGZE.png" alt="ZygorGuideLoader by Nexus">
</p>

**ZygorGuideLoader** is a standalone utility that comments guides on `Autoload.xml`
<p align="center">
  <img src="https://i.imgur.com/yqoy3xt.png" alt="ZygorGuideLoader by Nexus">
</p>

**In-Game** Midnight only enabled.
<p align="center">
  <img src="https://i.imgur.com/zNuatVP.png" alt="ZygorGuideLoader by Nexus">
</p>

**In-Game** Midnight only enabled. TWW and others expansions disabled (Not loaded).
<p align="center">
  <img src="https://i.imgur.com/EuTqT3E.png" alt="ZygorGuideLoader by Nexus">
</p>

## ✨ Features

### 📂 Guide Manager
Comments guides preventing them from loading to save CPU cycles during character load or /reload:
- **Expansion Toggles:** Instantly enable/disable expansions like **TWW** or **DRAGONFLIGHT** guides.
- **Category Filtering:** Toggle off specific guide categories (e.g., disable _Leveling_ or _Dailies_ if you don't use them).

### 🛠️ Utilities

- **Cache Cleaner:** One-click button to safely delete the WoW `_retail_/Cache` folder to fix stale data issues.
- **Smart Backups:** Automatically creates `_Official_Backup.xml` file on the first run.
- **Restore Original:** Factory reset button to revert all changes and restore the addon to its original state.
- **Modern GUI:** Sleek, dark-themed interface built with `customtkinter`.

## 🚀 How to Use

1. Download the latest `ZygorGuideLoader.exe` from the [Releases](../../releases) tab.
2. Run the executable.
3. Click **"Select World of Warcraft Folder"** (the app will attempt to auto-detect your path via Windows Registry).
4. Toggle OFF guides you don't use (e.g., Titles) to disable them in the engine.
5. Click **"Patch & Ready!"**.
6. Launch World of Warcraft.

## ⚠️ Known Limitations & Disclaimer

- **Search & Featured Page:** Disabling guide categories will prevent the in-game Search and will be shown as not available in-game.

- **Manual Control:** This loader acts as a manual workaround for performance optimization. Until Zygor implements native on-demand guide loading or lazy loading for their internal modules, these functional trade-offs are necessary to reduce startup times and memory bloat.

## It is recommended to only leave the guides you are currently using enabled (e.g., "Leveling") to maintain a balance between functionality and performance.

## 💻 Development & Compilation

If you want to run the source code or compile it yourself:

### Prerequisites

- **Python 3.10+**
- `customtkinter` library

### Installation

```bash
git clone https://github.com/Nexus-Hub/ZygorGuideLoader.git
pip install customtkinter
python main.py
```

### Compiling to .exe

To build the standalone executable with the embedded icon:

```bash
python -m PyInstaller --noconsole --onefile --collect-all customtkinter --icon=favicon.ico --add-data "favicon.ico;." main.py
```

The executable will be generated inside the `/dist/` directory.

---

📝 Developed by <img src="favicon.ico" width="20" height="20"> **cadmnexus**.
