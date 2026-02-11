import os
import shutil
import re
import json
import winreg
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
import ctypes

# Set the App User Model ID so the taskbar icon displays correctly
myappid = "nexus.zygorloader.app.2.0"  # Arbitrary string
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# Set up the modern dark theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"

LITE_FEATURES = {
    "Talent Advisor": [
        "Code-Retail\\TalentAdvisor.lua",
        "Code-Retail\\TalentAdvisor-Data.lua",
    ],
    "Pet Battles": ["Code-Retail\\PetBattle.lua", "PetBattle.lua"],
    "World Quests": ["Code-Retail\\WorldQuests.lua", "WorldQuests.lua"],
    "Creature 3D Model Viewer": ["CreatureViewer.lua"],
    "Titan Panel Overlay": ["TitanZygor.xml"],
}


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ZygorLoaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZygorGuideLoader by Nexus")
        self.geometry("520x760")
        self.resizable(False, False)

        # Use resource_path to check for the icon inside the exe bundle
        icon_path = resource_path("favicon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Icon load error: {e}")

        self.zygor_path = ""
        self.official_xml = ""
        self.target_xml = ""
        self.categories = set()
        self.toggles = {}
        self.main_addon_path = ""
        self.target_files_xml = ""
        self.official_files_xml = ""
        self.lite_toggles = {}

        # --- UI LAYOUT ---
        self.lbl_title = ctk.CTkLabel(
            self, text="Zygor Guide Loader", font=("Arial", 24, "bold")
        )
        self.lbl_title.pack(pady=20)

        self.btn_browse = ctk.CTkButton(
            self, text="Select World of Warcraft Folder", command=self.browse_folder
        )
        self.btn_browse.pack(pady=10)

        self.lbl_path = ctk.CTkLabel(
            self, text="Detecting WoW...", text_color="gray", font=("Arial", 10)
        )
        self.lbl_path.pack(pady=5)

        # --- CONTAINER FOR MAIN UI (Hidden by default) ---
        self.main_ui = ctk.CTkFrame(self, fg_color="transparent")
        # Note: We do NOT pack self.main_ui here. It gets packed in setup_files()

        # --- ZYGOR LITE SETTINGS ---
        ctk.CTkLabel(
            self.main_ui,
            text="--- ZYGOR LITE SETTINGS ---",
            font=("Arial", 12, "bold"),
            text_color="#28a745",
        ).pack(pady=(10, 0))

        # Outer transparent frame filling the width
        self.frame_lite = ctk.CTkFrame(self.main_ui, width=420, fg_color="transparent")
        self.frame_lite.pack(pady=5, padx=20, fill="x")

        # Inner frame to keep the 2-column grid perfectly centered
        self.inner_lite = ctk.CTkFrame(self.frame_lite, fg_color="transparent")
        self.inner_lite.pack(anchor="center")

        for i, feature in enumerate(LITE_FEATURES.keys()):
            var = ctk.BooleanVar(value=True)
            sw = ctk.CTkSwitch(
                self.inner_lite, text=feature, variable=var, font=("Arial", 13)
            )
            sw.grid(row=i // 2, column=i % 2, padx=20, pady=8, sticky="w")
            self.lite_toggles[feature] = var

        # --- ZYGOR LITE SETTINGS ---
        ctk.CTkLabel(
            self.main_ui,
            text="--- ZYGOR GUIDE LOADER SETTINGS ---",
            font=("Arial", 12, "bold"),
            text_color="#28a745",
        ).pack(pady=(10, 0))

        # --- MASTER FACTION TOGGLES ---
        self.frame_factions = ctk.CTkFrame(self.main_ui, fg_color="transparent")
        self.frame_factions.pack(pady=5)

        # Variables for Master Toggles (Default True)
        self.var_alliance = ctk.BooleanVar(value=True)
        self.var_horde = ctk.BooleanVar(value=True)

        # Alliance Switch (Blue)
        self.sw_alliance = ctk.CTkSwitch(
            self.frame_factions,
            text="Alliance",
            variable=self.var_alliance,
            progress_color="#0070dd",
            font=("Arial", 12, "bold"),
        )
        self.sw_alliance.pack(side="left", padx=10)

        # Horde Switch (Red)
        self.sw_horde = ctk.CTkSwitch(
            self.frame_factions,
            text="Horde",
            variable=self.var_horde,
            progress_color="#C41F3B",
            font=("Arial", 12, "bold"),
        )
        self.sw_horde.pack(side="left", padx=10)

        # --- SCROLLABLE CATEGORY LIST ---
        self.scrollable_frame = ctk.CTkFrame(
            self.main_ui, width=420, fg_color="transparent"
        )
        self.scrollable_frame.pack(pady=0, padx=20, fill="x")

        # --- CENTERED TOGGLE ALL BUTTONS ---
        self.frame_toggle_container = ctk.CTkFrame(self.main_ui, fg_color="transparent")
        self.frame_toggle_container.pack(pady=10, fill="x")

        # This inner frame acts as a centered anchor
        self.inner_toggle_btns = ctk.CTkFrame(
            self.frame_toggle_container, fg_color="transparent"
        )
        self.inner_toggle_btns.pack(anchor="center")  # This is what centers the block

        self.btn_all_on = ctk.CTkButton(
            self.inner_toggle_btns,
            text="Toggle All Guides ON",
            width=120,
            height=28,
            command=lambda: self.toggle_all_categories(True),
            fg_color="#3b3b3b",
            hover_color="#4b4b4b",
            font=("Arial", 12, "bold"),
        )
        self.btn_all_on.pack(side="left", padx=10)

        self.btn_all_off = ctk.CTkButton(
            self.inner_toggle_btns,
            text="Toggle All Guides OFF",
            width=120,
            height=28,
            command=lambda: self.toggle_all_categories(False),
            fg_color="#3b3b3b",
            hover_color="#4b4b4b",
            font=("Arial", 12, "bold"),
        )
        self.btn_all_off.pack(side="left", padx=10)

        # Helper text
        ctk.CTkLabel(
            self.main_ui,
            text="(Toggling OFF disables what's selected in-game)",
            font=("Arial", 10, "italic"),
            text_color="gray",
        ).pack(pady=(0, 5))

        # --- ZYGOR LITE SETTINGS ---
        ctk.CTkLabel(
            self.main_ui,
            text="Made by cadmnexus",
            font=("Arial", 12, "bold"),
            text_color="#28a745",
        ).pack(pady=(10, 0))

        # --- ACTION BUTTONS FRAME ---
        self.frame_actions = ctk.CTkFrame(self.main_ui, fg_color="transparent")
        self.frame_actions.pack(pady=(5, 10))

        self.btn_patch = ctk.CTkButton(
            self.frame_actions,
            text="Patch & Ready!",
            command=self.patch_xml,
            fg_color="#28a745",
            hover_color="#218838",
            font=("Arial", 16, "bold"),
            width=200,
            height=40,
        )
        self.btn_patch.pack(side="left", padx=10)

        self.btn_restore = ctk.CTkButton(
            self.frame_actions,
            text="Restore Original",
            command=self.restore_official_backups,
            fg_color="#6c757d",
            hover_color="#5a6268",
            font=("Arial", 14, "bold"),
            width=150,
            height=40,
        )
        self.btn_restore.pack(side="left", padx=10)

        self.btn_cache = ctk.CTkButton(
            self.main_ui,
            text="Clear WoW Cache",
            command=self.clear_wow_cache,
            fg_color="#d9534f",
            hover_color="#c9302c",
            font=("Arial", 14, "bold"),
            height=35,
        )
        self.btn_cache.pack(pady=(0, 15))

        # Initialization
        self.auto_detect_wow()
        self.load_config()

        # If no path found after init, prompt user
        if not self.zygor_path:
            self.lbl_path.configure(
                text="Please select your World of Warcraft folder to continue."
            )
            # Use .after to ensure window is ready before opening dialog
            self.after(200, self.browse_folder)

    def get_faction(self, filename):
        """Helper to determine faction based on filename string"""
        fname_lower = filename.lower()
        if "alliance" in fname_lower:
            return "Alliance"
        elif "horde" in fname_lower:
            return "Horde"
        return "Neutral"

    def auto_detect_wow(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Blizzard Entertainment\World of Warcraft",
            )
            path, _ = winreg.QueryValueEx(key, "InstallPath")
            key.Close()

            potential_path = os.path.join(
                path,
                "_retail_",
                "Interface",
                "AddOns",
                "ZygorGuidesViewer",
                "Guides-Retail",
            )

            if os.path.exists(os.path.join(potential_path, "Autoload.xml")):
                self.zygor_path = potential_path
                self.lbl_path.configure(
                    text=f"Auto-detected: ...{self.zygor_path[-45:]}"
                )
                self.setup_files()
        except Exception:
            self.lbl_path.configure(
                text="Auto-detect failed. Please select WoW folder manually."
            )

    def load_config(self):
        """Loads path and faction toggle states from config.json"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)

                    # 1. Load Path
                    saved_path = data.get("zygor_path", "")
                    if saved_path and os.path.exists(
                        os.path.join(saved_path, "Autoload.xml")
                    ):
                        self.zygor_path = saved_path
                        self.setup_files()

                    # 2. Load Faction Toggles (Default to True if not in file)
                    self.var_alliance.set(data.get("faction_alliance", True))
                    self.var_horde.set(data.get("faction_horde", True))

                    # 3. Load Lite Features (Default to True/Enabled if not in file)
                    saved_lite = data.get("lite_settings", {})
                    for feat, var in self.lite_toggles.items():
                        var.set(saved_lite.get(feat, True))

            except Exception as e:
                print(f"Config load error: {e}")

    def save_config(self):
        """Saves path, faction, and lite toggle states to config.json"""
        try:
            data = {
                "zygor_path": self.zygor_path,
                "faction_alliance": self.var_alliance.get(),
                "faction_horde": self.var_horde.get(),
                # Extract the boolean value from each ctk.BooleanVar in the dictionary
                "lite_settings": {
                    feat: var.get() for feat, var in self.lite_toggles.items()
                },
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select World of Warcraft Folder")
        if folder:
            zygor_addon_path = os.path.join(
                folder,
                "_retail_",
                "Interface",
                "AddOns",
                "ZygorGuidesViewer",
                "Guides-Retail",
            )

            if not os.path.exists(os.path.join(zygor_addon_path, "Autoload.xml")):
                messagebox.showerror(
                    "Error",
                    "Could not find Zygor Guides. Ensure you selected the main 'World of Warcraft' folder.",
                )
                return

            self.zygor_path = zygor_addon_path
            self.save_config()
            self.setup_files()

    def setup_files(self):
        self.main_ui.pack(fill="both", expand=True)
        self.lbl_path.configure(text=f"Path: ...{self.zygor_path[-45:]}")
        self.main_addon_path = os.path.dirname(
            self.zygor_path
        )  # Gets the ZygorGuidesViewer root folder

        # Guide XMLs
        self.target_xml = os.path.join(self.zygor_path, "Autoload.xml")
        self.official_xml = os.path.join(
            self.zygor_path, "Autoload_Official_Backup.xml"
        )

        # Engine XMLs
        self.target_files_xml = os.path.join(self.main_addon_path, "files-Retail.xml")
        self.official_files_xml = os.path.join(
            self.main_addon_path, "files-Retail_Official_Backup.xml"
        )

        # 1. Backup Autoload
        if not os.path.exists(self.official_xml):
            try:
                shutil.copy2(self.target_xml, self.official_xml)
            except Exception as e:
                messagebox.showerror(
                    "Backup Error", f"Failed to create guide backup: {e}"
                )
                return

        # 2. Backup files-Retail
        if not os.path.exists(self.official_files_xml) and os.path.exists(
            self.target_files_xml
        ):
            try:
                shutil.copy2(self.target_files_xml, self.official_files_xml)
            except Exception as e:
                messagebox.showerror(
                    "Backup Error", f"Failed to create engine backup: {e}"
                )
                return

        self.load_categories()

    def load_categories(self):
        self.categories.clear()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 1. READ CURRENT STATE (Category Level only)
        folder_states = {}
        if os.path.exists(self.target_xml):
            try:
                with open(self.target_xml, "r", encoding="utf-8") as f:
                    for line in f:
                        match = re.search(
                            r'<Script\s+file=[\'"]([^\'"]+)[\'"]', line, re.IGNORECASE
                        )
                        if match:
                            folder = match.group(1).replace("/", "\\").split("\\")[0]
                            # Exclude core folders and loose files (like TalentAdvisor-Builds.lua)
                            if folder.lower() in [
                                "images",
                                "includes",
                            ] or folder.lower().endswith((".lua", ".xml")):
                                continue

                            if folder not in folder_states:
                                folder_states[folder] = False

                            if "<!--" not in line:
                                folder_states[folder] = True
            except Exception as e:
                print(f"Error reading current state: {e}")

        # 2. POPULATE UI FROM BACKUP
        try:
            with open(self.official_xml, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.search(
                        r'<Script\s+file=[\'"]([^\'"]+)[\'"]', line, re.IGNORECASE
                    )
                    if match:
                        folder = match.group(1).replace("/", "\\").split("\\")[0]
                        # Exclude core folders and loose files
                        if folder.lower() not in [
                            "images",
                            "includes",
                        ] and not folder.lower().endswith((".lua", ".xml")):
                            self.categories.add(folder)

            self.toggles.clear()
            sorted_cats = sorted(self.categories)

            for cat in sorted_cats:
                is_on = folder_states.get(cat, True)
                var = ctk.BooleanVar(value=is_on)
                switch = ctk.CTkSwitch(
                    self.scrollable_frame,
                    text=f"Load {cat}",
                    variable=var,
                    font=("Arial", 14),
                )
                switch.pack(pady=8, padx=20, anchor="w")
                self.toggles[cat] = var

            calc_height = 680 + (len(sorted_cats) * 45)
            self.geometry(f"520x{min(1100, calc_height)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {e}")

    def patch_xml(self):
        if not self.official_xml or not os.path.exists(self.official_xml):
            messagebox.showerror(
                "Error", "Official backup missing. Please restart the app."
            )
            return

        # Save config immediately when patching so user preferences persist
        self.save_config()

        try:
            with open(self.official_xml, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read source file: {e}")
            return

        new_lines = []
        for line in lines:
            match = re.search(
                r'<Script\s+file=[\'"]([^\'"]+)[\'"]', line, re.IGNORECASE
            )
            if match:
                full_path = match.group(1).replace("/", "\\")
                folder = full_path.split("\\")[0]
                filename = full_path.split("\\")[-1]

                # 1. Check if the FOLDER is enabled (e.g. Leveling)
                is_folder_enabled = False
                if folder in self.toggles:
                    is_folder_enabled = self.toggles[folder].get()
                elif folder.lower() in ["images", "includes"]:
                    is_folder_enabled = True  # Always enable core folders

                # 2. Check if the FACTION is enabled (e.g. Alliance)
                faction = self.get_faction(filename)
                is_faction_enabled = True

                if faction == "Alliance":
                    is_faction_enabled = self.var_alliance.get()
                elif faction == "Horde":
                    is_faction_enabled = self.var_horde.get()

                # 3. Combine Logic: BOTH must be true to active
                should_be_active = is_folder_enabled and is_faction_enabled

                if not should_be_active:
                    # Comment out if active
                    if "<!--" not in line:
                        new_lines.append(f"<!-- {line.strip()} -->\n")
                    else:
                        new_lines.append(line)
                else:
                    # Uncomment if commented
                    if "<!--" in line:
                        clean_line = line.replace("<!--", "").replace("-->", "").strip()
                        new_lines.append(f"\t\t{clean_line}\n")
                    else:
                        new_lines.append(line)
            else:
                new_lines.append(line)

        try:
            with open(self.target_xml, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            # --- START FILES-RETAIL PATCHING ---
            if os.path.exists(self.official_files_xml):
                with open(self.official_files_xml, "r", encoding="utf-8") as f:
                    engine_lines = f.readlines()

                disabled_files = []
                for feat, var in self.lite_toggles.items():
                    if not var.get():
                        disabled_files.extend(LITE_FEATURES[feat])

                new_engine_lines = []
                seen_files = set()

                # Enhanced Protection to stabilize Gear, Gold, and Rare modules
                PROTECTED_CORE = [
                    "ZygorGuidesViewer.lua",
                    "MasterFrame.xml",
                    "Skins",
                    "Templates.xml",
                    "Functions.lua",
                    "Class.lua",
                    "Ver.lua",
                    "Localization",
                    "UiWidgets",
                    "MaintenanceFrame.xml",
                    "Options.lua",
                    "Pointer.lua",
                    "Arrows",
                    "Framework",
                    "Lib",
                    "GuideMenu.lua",
                    "Expect.lua",
                    "Notification",
                    "Item-Utils",
                    "QuestTracking",
                    "GoldUI\\Gold.xml",
                    "Events",
                    "Parser",
                ]

                for line in engine_lines:
                    line_raw = line.strip()
                    if not line_raw:
                        new_engine_lines.append(line)
                        continue

                    match = re.search(
                        r'file=[\'"]([^\'"]+)[\'"]', line_raw, re.IGNORECASE
                    )
                    should_comment = False

                    if match:
                        current_file = match.group(1).replace("/", "\\").lower()
                        is_protected = any(
                            p.lower() in current_file for p in PROTECTED_CORE
                        )
                        is_bloat = any(
                            d.lower() in current_file for d in disabled_files
                        )

                        if is_protected:
                            should_comment = False
                        elif is_bloat:
                            should_comment = True

                        if not should_comment:
                            if current_file in seen_files:
                                should_comment = True
                            else:
                                seen_files.add(current_file)

                    # 3. FINAL ASSEMBLY: Pure XML Logic
                    if should_comment:
                        # If it needs to be disabled but isn't already commented
                        if not line_raw.startswith("<!--"):
                            new_engine_lines.append(f"\t<!-- {line_raw} -->\n")
                        else:
                            new_engine_lines.append(line)
                    else:
                        # If it should be enabled but is currently commented
                        if line_raw.startswith("<!--"):
                            # Remove XML comment tags to restore the line
                            # Regex removes '<!--' at start, '-->' at end, and surrounding whitespace
                            clean = re.sub(r"^<!--\s*|\s*-->$", "", line_raw)
                            new_engine_lines.append(f"\t{clean}\n")
                        else:
                            new_engine_lines.append(line)

                with open(self.target_files_xml, "w", encoding="utf-8") as f:
                    f.writelines(new_engine_lines)
            # --- END FILES-RETAIL PATCHING ---

            messagebox.showinfo(
                "Success", "Guides & Engine Optimized! ZygorLite applied."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def clear_wow_cache(self):
        """Finds the WoW _retail_ folder and deletes the Cache directory."""
        if not self.zygor_path:
            messagebox.showerror(
                "Error", "Please detect or select your WoW folder first."
            )
            return

        try:
            # We know zygor_path contains "_retail_". Let's split the string to get the root _retail_ path.
            # Example path: C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\ZygorGuidesViewer\Guides-Retail
            if "_retail_" in self.zygor_path:
                retail_path = self.zygor_path.split("_retail_")[0] + "_retail_"
                cache_path = os.path.join(retail_path, "Cache")

                if os.path.exists(cache_path):
                    try:
                        shutil.rmtree(cache_path)
                        messagebox.showinfo(
                            "Success",
                            "WoW Cache successfully cleared!\nYour next login will rebuild it cleanly.",
                        )
                    except OSError as e:
                        # Catch WinError 32 specifically when a file is locked by the game
                        if e.winerror == 32 or "used by another process" in str(e):
                            messagebox.showwarning(
                                "Game is Running",
                                "World of Warcraft is currently running!\n\nPlease close the game completely before clearing the cache.",
                            )
                        else:
                            raise e
                else:
                    messagebox.showinfo(
                        "Info", "Cache folder is already empty or does not exist."
                    )
            else:
                messagebox.showerror(
                    "Error", "Could not locate the _retail_ directory in the path."
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear cache: {e}")

    def toggle_all_categories(self, state):
        """Sets all category toggles in the scrollable frame to True or False."""
        for var in self.toggles.values():
            var.set(state)

    def restore_official_backups(self):
        """Full factory reset of all modified Zygor files."""
        if not all(
            os.path.exists(f) for f in [self.official_xml, self.official_files_xml]
        ):
            messagebox.showerror(
                "Error", "Backups missing. Re-select your WoW folder to recreate them."
            )
            return

        if messagebox.askyesno(
            "Zygor Reset",
            "Restore Zygor to official version? (This removes all Lite optimizations)",
        ):
            try:
                # Direct overwrite from clean backups
                shutil.copy2(self.official_xml, self.target_xml)
                shutil.copy2(self.official_files_xml, self.target_files_xml)

                # Reset UI state
                self.var_alliance.set(True)
                self.var_horde.set(True)
                for var in self.lite_toggles.values():
                    var.set(True)

                self.load_categories()
                self.save_config()
                messagebox.showinfo("Success", "Zygor restored to original state.")
            except Exception as e:
                messagebox.showerror("Error", f"Restore failed: {e}")


if __name__ == "__main__":
    app = ZygorLoaderApp()
    app.mainloop()
