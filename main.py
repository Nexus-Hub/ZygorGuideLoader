import os
import shutil
import re
import json
import winreg
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Set up the modern dark theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"


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
        self.geometry("500x750")
        self.resizable(False, False)

        if os.path.exists("favicon.ico"):
            try:
                self.iconbitmap(resource_path("favicon.ico"))
            except:
                pass

        self.zygor_path = ""
        self.official_xml = ""
        self.target_xml = ""
        self.categories = set()
        self.toggles = {}

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

        # --- MASTER FACTION TOGGLES ---
        self.frame_factions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_factions.pack(pady=5)

        # Variables for Master Toggles (Default True)
        self.var_neutral = ctk.BooleanVar(value=True)
        self.var_alliance = ctk.BooleanVar(value=True)
        self.var_horde = ctk.BooleanVar(value=True)

        # Neutral Switch (Yellow/Orange)
        self.sw_neutral = ctk.CTkSwitch(
            self.frame_factions,
            text="Neutral",
            variable=self.var_neutral,
            progress_color="#e0a800",
            font=("Arial", 12, "bold"),
        )
        self.sw_neutral.pack(side="left", padx=10)

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
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=420, height=350)
        self.scrollable_frame.pack(pady=15, padx=20, fill="both", expand=True)

        self.btn_patch = ctk.CTkButton(
            self,
            text="Patch & Ready!",
            command=self.patch_xml,
            fg_color="#28a745",
            hover_color="#218838",
            font=("Arial", 16, "bold"),
            height=40,
        )
        self.btn_patch.pack(pady=15)

        # Initialization
        self.auto_detect_wow()
        self.load_config()

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
                    self.var_neutral.set(data.get("faction_neutral", True))
                    self.var_alliance.set(data.get("faction_alliance", True))
                    self.var_horde.set(data.get("faction_horde", True))

            except Exception as e:
                print(f"Config load error: {e}")

    def save_config(self):
        """Saves path and faction toggle states to config.json"""
        try:
            data = {
                "zygor_path": self.zygor_path,
                "faction_neutral": self.var_neutral.get(),
                "faction_alliance": self.var_alliance.get(),
                "faction_horde": self.var_horde.get(),
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
        self.lbl_path.configure(text=f"Path: ...{self.zygor_path[-45:]}")
        self.target_xml = os.path.join(self.zygor_path, "Autoload.xml")
        self.official_xml = os.path.join(
            self.zygor_path, "Autoload_Official_Backup.xml"
        )

        if not os.path.exists(self.official_xml):
            try:
                shutil.copy2(self.target_xml, self.official_xml)
            except Exception as e:
                messagebox.showerror(
                    "Backup Error", f"Failed to create master backup: {e}"
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
                            if folder.lower() in ["images", "includes"]:
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
                        if folder.lower() not in ["images", "includes"]:
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

            calc_height = 350 + (len(sorted_cats) * 45)
            final_height = max(600, min(900, calc_height))
            self.geometry(f"500x{final_height}")

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
                elif faction == "Neutral":
                    is_faction_enabled = self.var_neutral.get()

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
            messagebox.showinfo("Success", "Loading guides optimized!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")


if __name__ == "__main__":
    app = ZygorLoaderApp()
    app.mainloop()
