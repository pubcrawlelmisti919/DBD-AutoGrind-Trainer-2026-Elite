import json
from pathlib import Path
from typing import Dict
from pydantic_settings import BaseSettings

class TrainerConfig(BaseSettings):
    """Persistent trainer configuration."""
    theme: str = "dark"
    accent_color: str = "#8b0000"
    hotkeys: Dict[str, str] = {
        "toggle_gui": "insert",
        "exit_trainer": "f2",
        "toggle_esp": "f1",
        "toggle_aimbot": "f3"
    }
    auto_start: bool = False
    minimize_to_tray: bool = True

    class Config:
        env_prefix = "DBD_TRAINER_"
        env_file = ".env"
        env_file_encoding = "utf-8"

    def save_to_file(self, filepath: Path = Path("config.json")) -> None:
        with open(filepath, "w") as f:
            json.dump(self.dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filepath: Path = Path("config.json")) -> "TrainerConfig":
        if filepath.exists():
            with open(filepath, "r") as f:
                data = json.load(f)
            return cls(**data)
        return cls()
