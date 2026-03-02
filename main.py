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
myappid = "nexus.zygorloader.app.3.0"
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# Set up the modern dark theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"

# Exclusively allowed categories mapped by the user
ALLOWED_CATEGORIES = [
    "LEVELING",
    "DAILIES",
    "DUNGEONS",
    "GEAR",
    "PROFESSIONS",
    "ACHIEVEMENTS",
    "PETS AND MOUNTS",
    "TITLES",
    "REPUTATIONS",
    "EVENTS",
    "GOLD",
    "POINTS OF INTEREST",
    "TALENT ADVISOR",
]

# Expansions and their identifying keywords inside the script filenames
EXPANSIONS = {
    "CATA": ["CATA"],
    "MOP": ["MOP"],
    "WOD": ["WOD"],
    "LEGION": ["LEGION", "LEG_"],
    "BFA": ["BFA"],
    "SHADOWLANDS": ["SHADOW"],
    "DRAGONFLIGHT": ["DRAGON"],
    "TWW": ["TWW"],
    "MID": ["MID"],
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
        self.geometry("540x880")  # Expanded to fit the new expansions grid beautifully
        self.resizable(False, False)

        icon_path = resource_path("favicon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                pass

        self.zygor_path = ""
        self.official_xml = ""
        self.target_xml = ""
        self.toggles = {}
        self.exp_toggles = {}
        self.saved_toggles = {}
        self.saved_exp_toggles = {}

        # --- UI LAYOUT ---
        self.lbl_title = ctk.CTkLabel(
            self, text="Zygor Guide Loader", font=("Arial", 24, "bold")
        )
        self.lbl_title.pack(pady=(20, 10))

        self.btn_browse = ctk.CTkButton(
            self, text="Select World of Warcraft Folder", command=self.browse_folder
        )
        self.btn_browse.pack(pady=5)

        self.lbl_path = ctk.CTkLabel(
            self, text="Detecting WoW...", text_color="gray", font=("Arial", 10)
        )
        self.lbl_path.pack(pady=5)

        # --- CONTAINER FOR MAIN UI ---
        self.main_ui = ctk.CTkFrame(self, fg_color="transparent")

        # --- EXPANSIONS GRID ---
        ctk.CTkLabel(
            self.main_ui,
            text="--- EXPANSIONS ---",
            font=("Arial", 14, "bold"),
            text_color="#17a2b8",
        ).pack(pady=(5, 5))

        self.frame_expansions = ctk.CTkFrame(self.main_ui, fg_color="transparent")
        self.frame_expansions.pack(pady=0, padx=20, fill="x")
        self.frame_expansions.grid_columnconfigure((0, 1, 2), weight=1)

        # --- GUIDE CATEGORIES ---
        ctk.CTkLabel(
            self.main_ui,
            text="--- GUIDE CATEGORIES ---",
            font=("Arial", 14, "bold"),
            text_color="#28a745",
        ).pack(pady=(15, 5))

        # --- SCROLLABLE CATEGORY LIST ---
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.main_ui, width=400, height=300, fg_color="transparent"
        )
        self.scrollable_frame.pack(pady=5, padx=20, fill="both", expand=True)

        # --- CENTERED TOGGLE ALL BUTTONS ---
        self.frame_toggle_container = ctk.CTkFrame(self.main_ui, fg_color="transparent")
        self.frame_toggle_container.pack(pady=10, fill="x")

        self.inner_toggle_btns = ctk.CTkFrame(
            self.frame_toggle_container, fg_color="transparent"
        )
        self.inner_toggle_btns.pack(anchor="center")

        self.btn_all_on = ctk.CTkButton(
            self.inner_toggle_btns,
            text="Toggle All ON",
            width=120,
            height=28,
            command=lambda: self.toggle_all_state(True),
            fg_color="#3b3b3b",
            hover_color="#4b4b4b",
            font=("Arial", 12, "bold"),
        )
        self.btn_all_on.pack(side="left", padx=10)

        self.btn_all_off = ctk.CTkButton(
            self.inner_toggle_btns,
            text="Toggle All OFF",
            width=120,
            height=28,
            command=lambda: self.toggle_all_state(False),
            fg_color="#3b3b3b",
            hover_color="#4b4b4b",
            font=("Arial", 12, "bold"),
        )
        self.btn_all_off.pack(side="left", padx=10)

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
            width=180,
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
            width=140,
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
        self.btn_cache.pack(pady=(0, 20))

        # Initialization
        self.load_config()
        if not self.zygor_path:
            self.auto_detect_wow()

        if not self.zygor_path:
            self.lbl_path.configure(
                text="Please select your World of Warcraft folder to continue."
            )
            self.after(200, self.browse_folder)

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
                self.setup_files()
        except Exception:
            pass

    def load_config(self):
        self.saved_toggles = {}
        self.saved_exp_toggles = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    saved_path = data.get("zygor_path", "")
                    if saved_path and os.path.exists(
                        os.path.join(saved_path, "Autoload.xml")
                    ):
                        self.zygor_path = saved_path
                        self.saved_toggles = data.get("toggles", {})
                        self.saved_exp_toggles = data.get("exp_toggles", {})
                        self.setup_files()
            except Exception as e:
                print(f"Config load error: {e}")

    def save_config(self):
        try:
            data = {
                "zygor_path": self.zygor_path,
                "toggles": {cat: var.get() for cat, var in self.toggles.items()},
                "exp_toggles": {
                    exp: var.get() for exp, var in self.exp_toggles.items()
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
                    "Could not find Zygor Guides. Ensure you selected the 'World of Warcraft' folder.",
                )
                return

            self.zygor_path = zygor_addon_path
            self.setup_files()
            self.save_config()

    def setup_files(self):
        self.main_ui.pack(fill="both", expand=True)
        self.lbl_path.configure(text=f"Path: ...{self.zygor_path[-45:]}")

        self.target_xml = os.path.join(self.zygor_path, "Autoload.xml")
        self.official_xml = os.path.join(
            self.zygor_path, "Autoload_Official_Backup.xml"
        )

        # 1. Backup Autoload (Create fresh backup if missing)
        if not os.path.exists(self.official_xml):
            try:
                shutil.copy2(self.target_xml, self.official_xml)
            except Exception as e:
                messagebox.showerror(
                    "Backup Error", f"Failed to create guide backup: {e}"
                )
                return

        self.load_categories()

    def load_categories(self):
        self.toggles.clear()
        self.exp_toggles.clear()

        # Build UI Switches for Expansions Grid
        for widget in self.frame_expansions.winfo_children():
            widget.destroy()

        exp_keys = list(EXPANSIONS.keys())
        for i, exp in enumerate(exp_keys):
            row, col = divmod(i, 3)
            is_on = self.saved_exp_toggles.get(exp, True)
            var = ctk.BooleanVar(value=is_on)
            switch = ctk.CTkSwitch(
                self.frame_expansions, text=exp, variable=var, font=("Arial", 12)
            )
            switch.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            self.exp_toggles[exp] = var

        # Build UI Switches for Guide Categories
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for cat in ALLOWED_CATEGORIES:
            is_on = self.saved_toggles.get(cat, True)
            var = ctk.BooleanVar(value=is_on)
            switch = ctk.CTkSwitch(
                self.scrollable_frame, text=cat, variable=var, font=("Arial", 14)
            )
            switch.pack(pady=5, padx=20, anchor="w")
            self.toggles[cat] = var

    def patch_xml(self):
        if not self.official_xml or not os.path.exists(self.official_xml):
            messagebox.showerror(
                "Error", "Official backup missing. Please restart the app."
            )
            return

        self.save_config()

        try:
            with open(self.official_xml, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read source file: {e}")
            return

        new_lines = []

        # Start default state as INCLUDES to enforce scripts mapped prior to leveling are non-commented
        current_category = "INCLUDES"

        for line in lines:
            line_strip = line.strip()

            if not line_strip:
                new_lines.append(line)
                continue

            # Check if line is a category header
            if (
                line_strip.startswith("<!--")
                and line_strip.endswith("-->")
                and not re.search(r"<Script\s+file=", line_strip, re.IGNORECASE)
            ):
                possible_cat = line_strip[4:-3].strip()

                # Only change the master tracking category if it's explicitly one of the allowed categories, or INCLUDES.
                if possible_cat in ALLOWED_CATEGORIES or possible_cat == "INCLUDES":
                    current_category = possible_cat

                new_lines.append(line)  # Write the category comment unchanged
                continue

            # Check if line contains a script
            if re.search(r"<Script\s+file=", line_strip, re.IGNORECASE):

                # Explicitly separate Talent Advisor so it detaches from POINTS OF INTEREST
                if "TalentAdvisor" in line_strip:
                    current_category = "TALENT ADVISOR"

                # 1. CATEGORY ENABLEMENT
                if current_category == "INCLUDES":
                    category_enabled = True
                else:
                    var = self.toggles.get(current_category)
                    category_enabled = var.get() if var else True

                # 2. EXPANSION ENABLEMENT
                expansion_enabled = True
                matched_expansions = []
                # Check line for expansion keywords
                line_upper = line_strip.upper()
                for exp, keywords in EXPANSIONS.items():
                    if any(kw in line_upper for kw in keywords):
                        matched_expansions.append(exp)

                # If the file belongs to specific expansion(s), at least one must be toggled ON
                if matched_expansions:
                    expansion_enabled = any(
                        self.exp_toggles[exp].get() for exp in matched_expansions
                    )

                # Final state requires both to be true (or if it's a general/base file without an expansion string, it just checks category)
                is_enabled = category_enabled and expansion_enabled

                # Capture exact leading whitespace to preserve original formatting
                leading_ws = line[: len(line) - len(line.lstrip())]

                # SAFELY UNCOMMENT: Find the script tag and remove wrapping comments.
                # This ignores trailing inline comments like `<!-- Everyone gets this -->`
                clean_strip = re.sub(
                    r"<!--\s*(<Script\s+file=[^>]+>)\s*-->",
                    r"\1",
                    line_strip,
                    flags=re.IGNORECASE,
                )

                if is_enabled:
                    new_lines.append(f"{leading_ws}{clean_strip}\n")
                else:
                    # SAFELY COMMENT: Find only the pure `<Script...>` tag and wrap it
                    commented_strip = re.sub(
                        r"(<Script\s+file=[^>]+>)",
                        r"<!-- \1 -->",
                        clean_strip,
                        flags=re.IGNORECASE,
                    )
                    new_lines.append(f"{leading_ws}{commented_strip}\n")
                continue

            # Anything else (e.g., standard XML wrappers like <Ui>)
            new_lines.append(line)

        try:
            with open(self.target_xml, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            messagebox.showinfo(
                "Success", "Guides Optimized! Autoload.xml patched perfectly."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def clear_wow_cache(self):
        if not self.zygor_path:
            messagebox.showerror(
                "Error", "Please detect or select your WoW folder first."
            )
            return

        try:
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

    def toggle_all_state(self, state):
        for var in self.toggles.values():
            var.set(state)
        for var in self.exp_toggles.values():
            var.set(state)

    def restore_official_backups(self):
        if not os.path.exists(self.official_xml):
            messagebox.showerror(
                "Error", "Backup missing. Re-select your WoW folder to recreate it."
            )
            return

        if messagebox.askyesno(
            "Zygor Reset",
            "Restore Zygor to official version? (This re-enables all modules)",
        ):
            try:
                shutil.copy2(self.official_xml, self.target_xml)
                for var in self.toggles.values():
                    var.set(True)
                for var in self.exp_toggles.values():
                    var.set(True)
                self.save_config()
                messagebox.showinfo("Success", "Zygor restored to original state.")
            except Exception as e:
                messagebox.showerror("Error", f"Restore failed: {e}")


if __name__ == "__main__":
    app = ZygorLoaderApp()
    app.mainloop()
