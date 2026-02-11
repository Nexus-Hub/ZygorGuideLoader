# ZygorGuideLoader 🐉

**Modular Guide & Engine Optimizer to eliminate loading screen lag in World of Warcraft.**

<p align="center">
  <img src="https://i.imgur.com/wMwsM5e.png" alt="ZygorGuideLoader">
</p>

````markdown
By default, Zygor Guides loads every single module (Talent Advisor, Pet Battles, 3D Models, etc.) and every guide into memory during startup. For high-end setups aiming for maximum performance, this causes massive FPS drops, Lua garbage collection spikes, and client freezes.

**ZygorGuideLoader** is a standalone utility that patches both `Autoload.xml` (Guides) and `files-Retail.xml` (Engine Modules), allowing you to strip the addon down to the bare essentials.

## ✨ Features

### 🚀 Zygor Lite
Disable  internal modules to save CPU cycles:
- **Talent Advisor:** Disable the background talent calculation engine.
- **Pet Battles:** Remove pet battle logic and data.
- **World Quests:** Disable the heavy world quest tracking module.
- **3D Model Viewer:** Remove the creature model viewer frame.
- **Titan Panel:** Disable the overlay integration.

### 📂 Guide Manager
- **Master Faction Toggles:** Instantly enable/disable **Alliance** or **Horde** guides globally.
- **Category Filtering:** Manually toggle off specific guide categories (e.g., disable *Leveling* or *Dailies* if you don't use them).

### 🛠️ Utilities
- **Cache Cleaner:** One-click button to safely delete the WoW `_retail_/Cache` folder to fix stale data issues.
- **Smart Backups:** Automatically creates `_Official_Backup.xml` files on the first run.
- **Restore Original:** Factory reset button to revert all changes and restore the addon to its original state.
- **Modern GUI:** Sleek, dark-themed interface built with `customtkinter`.

## 🚀 How to Use

1. Download the latest `ZygorGuideLoader.exe` from the [Releases](../../releases) tab.
2. Run the executable.
3. Click **"Select World of Warcraft Folder"** (the app will attempt to auto-detect your path via Windows Registry).
4. **Lite Settings:** Toggle OFF features you don't use (e.g., Pet Battles, Talent Advisor) to disable them in the engine.
5. **Guide Settings:** Use the Faction switches or the list below to select which guides to load.
6. Click **"Patch & Ready!"**.
7. Launch World of Warcraft.

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
````

### Compiling to .exe

To build the standalone executable with the embedded icon:

```bash
python -m PyInstaller --noconsole --onefile --collect-all customtkinter --icon=favicon.ico --add-data "favicon.ico;." main.py
```

The executable will be generated inside the `/dist/` directory.

---

📝 **Author**
Developed by <img src="favicon.ico" width="20" height="20"> **cadmnexus**.
