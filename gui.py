import customtkinter as ctk
from PIL import Image
import asyncio
import threading
import logging
import sys
import pystray
from pystray import MenuItem as item
from trainer import Trainer
from config import TrainerConfig
from web_dashboard import WebDashboard

log = logging.getLogger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class TrainerApp(ctk.CTk):
    """Main GUI window for the trainer."""

    def __init__(self) -> None:
        super().__init__()
        self.title("DBD AutoGrind Trainer 2026")
        self.geometry("900x700")
        self.resizable(True, True)
        self.config = TrainerConfig.load_from_file()
        self.trainer = Trainer()
        self.web_dash = WebDashboard(self.trainer)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # ---------- UI layout ----------
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        ctk.CTkLabel(header, text="🔪 DBD AutoGrind Trainer 2026", font=("Arial", 20, "bold"),
                     text_color=self.config.accent_color).pack(pady=10)

        # Status bar
        self.status_var = ctk.StringVar(value="Not attached")
        status_bar = ctk.CTkLabel(self, textvariable=self.status_var,
                                  fg_color="#8b0000", font=("Arial", 12), height=30)
        status_bar.grid(row=2, column=0, sticky="ew", padx=0, pady=0)

        # Main scrollable frame for feature cards
        main_frame = ctk.CTkScrollableFrame(self, fg_color="#16213e")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.feature_vars = {}
        self._build_feature_cards(main_frame)

        # Bottom control bar
        control_frame = ctk.CTkFrame(self, fg_color="#0f3460")
        control_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        self.attach_btn = ctk.CTkButton(control_frame, text="Attach to Game", command=self.attach)
        self.attach_btn.pack(side="left", padx=10, pady=10)
        self.start_btn = ctk.CTkButton(control_frame, text="Start Loop", command=self.start_loop)
        self.start_btn.pack(side="left", padx=10, pady=10)
        self.stop_btn = ctk.CTkButton(control_frame, text="Stop Loop", command=self.stop_loop, state="disabled")
        self.stop_btn.pack(side="left", padx=10, pady=10)

        # Mini console
        self.console = ctk.CTkTextbox(self, height=100, fg_color="#1a1a2e")
        self.console.grid(row=4, column=0, sticky="ew", padx=10, pady=(0,10))
        self._redirect_logging()

        # System tray
        self.tray_icon = None
        if self.config.minimize_to_tray:
            self._create_tray_icon()

    def _build_feature_cards(self, parent: ctk.CTkScrollableFrame) -> None:
        features = [
            ("ESP Wallhack", "esp"),
            ("Aimbot", "aimbot"),
            ("No Terror Radius", "no_terror"),
            ("Fast Vault", "fast_vault"),
            ("Fast Pallet", "fast_pallet"),
            ("Skill Check Bot", "skill_check_bot"),
            ("Infinite Bloodpoints", "infinite_bloodpoints"),
            ("Unlock All Perks (once)", "unlock_perks"),
            ("Unlock All Skins (once)", "unlock_skins"),
            ("Auto Bloodpoint Farm", "auto_farm"),
        ]
        for label, key in features:
            card = ctk.CTkFrame(parent, fg_color="#0f3460", corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)
            var = ctk.BooleanVar(value=self.trainer.features.get(key, False))
            switch = ctk.CTkSwitch(card, text=label, variable=var,
                                   command=lambda k=key, v=var: self.toggle_feature(k, v))
            switch.pack(side="left", padx=10, pady=10)
            self.feature_vars[key] = var

    def toggle_feature(self, key: str, var: ctk.BooleanVar) -> None:
        self.trainer.features[key] = var.get()
        log.info(f"{key} set to {var.get()}")

    def attach(self) -> None:
        threading.Thread(target=self._async_attach, daemon=True).start()

    def _async_attach(self) -> None:
        async def coro():
            success = await self.trainer.attach_to_game()
            self.status_var.set("Attached" if success else "Failed")
        asyncio.run(coro())

    def start_loop(self) -> None:
        self.trainer.start()
        self.status_var.set("Trainer active")
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.web_dash.start()

    def stop_loop(self) -> None:
        self.trainer.stop()
        self.status_var.set("Stopped")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.web_dash.stop()

    def _redirect_logging(self) -> None:
        class ConsoleHandler(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget
            def emit(self, record):
                msg = self.format(record)
                self.widget.insert("end", msg + "\n")
                self.widget.see("end")
        handler = ConsoleHandler(self.console)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logging.getLogger().addHandler(handler)

    def _create_tray_icon(self) -> None:
        img = Image.new("RGB", (16, 16), color="#8b0000")
        menu = (item("Show", self.deiconify), item("Exit", self.on_close))
        self.tray_icon = pystray.Icon("DBD Trainer", img, "DBD Trainer", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def on_close(self) -> None:
        self.trainer.stop()
        self.web_dash.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        sys.exit(0)

def launch_gui() -> None:
    app = TrainerApp()
    app.mainloop()
