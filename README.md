# ZygorGuideLoader 🐉

**Modular Guide Loading to reduce CPU strain and eliminate loading screen lag in World of Warcraft.**

By default, Zygor Guides loads every single module (Achievements, Leveling, Dungeons, Pets, etc.) into your RAM during the loading screen. For high-end setups aiming for maximum performance, this causes massive FPS drops and client freezes (up to 4+ seconds of lag).

**ZygorGuideLoader** is a standalone utility that patches the `Autoload.xml` file, allowing you to load only the specific content you need for your current session.

## ✨ Features

- **Faster loading time:** Eliminates UI bottlenecking during loading.
- **Master Faction Toggles:** New switches to instantly enable/disable **Alliance**, **Horde**, or **Neutral** guides globally.
- **Modern GUI:** Sleek, dark-themed interface built with `customtkinter`.
- **Persistent State:** Automatically detects your current guide status and remembers your last selection.
- **Smart Backups:** Creates a `Autoload_Official_Backup.xml` on the first run to ensure you can always revert to the original state.
- **Dynamic Interface:** The application window automatically resizes based on the number of guide categories detected.

## 🚀 How to Use (For Standard Users)

1. Download the latest `ZygorGuideLoader.exe` from the [Releases](../../releases) tab.
2. Run the executable
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

### Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/ZygorGuideLoader.git](https://github.com/YourUsername/ZygorGuideLoader.git)
   cd ZygorGuideLoader
   Install requirements:
   ```

Bash
pip install customtkinter
Run the script:

Bash
python main.py
Compiling to .exe
To build the standalone executable yourself with the embedded icon, run the following command in your terminal:

Bash
pyinstaller --noconsole --onefile --collect-all customtkinter --icon=favicon.ico main.py
The executable will be generated inside the /dist/ directory.

📝 Author
Developed by cadmnexus.
