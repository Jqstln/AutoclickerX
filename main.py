import os
import sys
import time
import json
import threading
import requests
import tkinter as tk
from io import BytesIO
from pynput.mouse import Controller, Button
from pynput import keyboard
from PIL import Image, ImageTk
import customtkinter as ctk

# Constants and globals
mouse = Controller()
clicking = False
hotkey_start = 'f6'
hotkey_stop = 'f7'
CONFIG_PATH = os.path.join(os.getenv('APPDATA'), 'AutoclickerX', 'config.json')
ICON_URL = "https://s3.justinnn.dev/logo_mouse.ico"

# Config helpers
def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

# Click loop
def click_loop(delay, update_ui_callback):
    global clicking
    update_ui_callback(True)
    while clicking:
        mouse.click(Button.left)
        time.sleep(delay)
    update_ui_callback(False)

# Main app class
class AutoclickerXApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("AutoclickerX")
        self.root.geometry("450x360")
        self.root.resizable(False, False)

        # Load icon from URL
        try:
            icon = Image.open(BytesIO(requests.get(ICON_URL).content))
            icon = ImageTk.PhotoImage(icon)
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon)
        except:
            pass  # Skip icon on error

        self.minutes_var = ctk.IntVar()
        self.seconds_var = ctk.IntVar()
        self.ms_var = ctk.IntVar()
        self.delay = 1.0
        self.active = False

        self.load_user_config()
        self.build_ui()
        self.bind_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

    def build_ui(self):
        ctk.CTkLabel(self.root, text="AutoclickerX", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=15)

        for label, var in [("Minutes", self.minutes_var), ("Seconds", self.seconds_var), ("Milliseconds", self.ms_var)]:
            row = ctk.CTkFrame(self.root, fg_color="transparent")
            row.pack(pady=4)
            ctk.CTkLabel(row, text=label, width=100).pack(side="left")
            ctk.CTkEntry(row, textvariable=var, width=100).pack(side="left", padx=10)

        btns = [
            ("▶ Start", self.start_clicking),
            ("⏹ Stop", self.stop_clicking),
            ("🎯 Hotkeys", self.set_hotkeys),
            ("❌ Quit", self.quit_app)
        ]

        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.button_frame.pack(pady=25)

        for i, (txt, cmd) in enumerate(btns):
            btn = ctk.CTkButton(self.button_frame, text=txt, command=cmd, corner_radius=10)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            if txt == "▶ Start": self.start_btn = btn

    def calculate_delay(self):
        self.delay = self.minutes_var.get() * 60 + self.seconds_var.get() + self.ms_var.get() / 1000

    def start_clicking(self):
        global clicking
        self.calculate_delay()
        clicking = True
        threading.Thread(target=click_loop, args=(self.delay, self.set_active_state), daemon=True).start()

    def stop_clicking(self):
        global clicking
        clicking = False
        self.set_active_state(False)

    def set_active_state(self, active):
        self.active = active
        self.start_btn.configure(fg_color="#14477C" if active else ctk.ThemeManager.theme['CTkButton']['fg_color'])

    def bind_hotkeys(self):
        def on_press(key):
            try:
                if key == keyboard.Key[hotkey_start]: self.start_clicking()
                elif key == keyboard.Key[hotkey_stop]: self.stop_clicking()
            except: pass

        keyboard.Listener(on_press=on_press).start()

    def set_hotkeys(self):
        top = ctk.CTkToplevel(self.root)
        top.geometry("300x200")
        top.title("🎯 Set Hotkeys")

        entries = {}
        for label, var_name in [("Start Hotkey:", 'start'), ("Stop Hotkey:", 'stop')]:
            ctk.CTkLabel(top, text=label).pack(pady=10)
            entry = ctk.CTkEntry(top)
            entry.insert(0, globals()[f"hotkey_{var_name}"])
            entry.pack()
            entries[var_name] = entry

        def save_hotkeys():
            global hotkey_start, hotkey_stop
            hotkey_start = entries['start'].get()
            hotkey_stop = entries['stop'].get()
            top.destroy()

        ctk.CTkButton(top, text="📂 Save", command=save_hotkeys).pack(pady=15)

    def quit_app(self):
        save_config({
            "minutes": self.minutes_var.get(),
            "seconds": self.seconds_var.get(),
            "milliseconds": self.ms_var.get(),
            "hotkey_start": hotkey_start,
            "hotkey_stop": hotkey_stop
        })
        self.root.destroy()
        sys.exit()

    def load_user_config(self):
        config = load_config()
        self.minutes_var.set(config.get("minutes", 0))
        self.seconds_var.set(config.get("seconds", 0))
        self.ms_var.set(config.get("milliseconds", 0))
        global hotkey_start, hotkey_stop
        hotkey_start = config.get("hotkey_start", hotkey_start)
        hotkey_stop = config.get("hotkey_stop", hotkey_stop)

if __name__ == "__main__":
    AutoclickerXApp()