import asyncio
import logging
import keyboard
import time
from typing import Dict, Callable
from pypresence import Presence
from memory import MemoryManager
from offsets import Offsets

log = logging.getLogger(__name__)

class Trainer:
    """Async trainer loop with Discord Rich Presence and hotkey handling."""

    def __init__(self) -> None:
        self.mem = MemoryManager()
        self.offsets = Offsets()
        self.running = False
        self.features: Dict[str, bool] = {
            "esp": False,
            "aimbot": False,
            "no_terror": False,
            "fast_vault": False,
            "fast_pallet": False,
            "skill_check_bot": False,
            "infinite_bloodpoints": False,
            "unlock_perks": False,
            "unlock_skins": False,
            "auto_farm": False,
        }
        self.hotkey_actions: Dict[str, Callable] = {
            "f1": self._toggle_esp,
            "f3": self._toggle_aimbot,
            "f4": self._toggle_no_terror,
            "f5": self._toggle_fast_vault,
            "f6": self._toggle_fast_pallet,
            "f7": self._toggle_skill_check,
            "f8": self._toggle_infinite_bp,
            "f9": self._unlock_perks_once,
            "f10": self._unlock_skins_once,
            "f11": self._toggle_auto_farm,
        }
        self.discord_rpc = None
        self.client_id = "123456789012345678"
        try:
            self.discord_rpc = Presence(self.client_id)
            self.discord_rpc.connect()
        except Exception as e:
            log.warning(f"Discord RPC connection failed: {e}")

    async def attach_to_game(self) -> bool:
        await asyncio.to_thread(self.mem.attach)
        if self.mem.attached:
            self._update_discord("In‑game", "Attached")
            return True
        return False

    def _update_discord(self, state: str, details: str) -> None:
        if self.discord_rpc:
            try:
                self.discord_rpc.update(state=state, details=details,
                                        large_image="dbd_logo",
                                        start=int(time.time()))
            except Exception:
                pass

    def _toggle_esp(self) -> None:
        self.features["esp"] = not self.features["esp"]
        log.info(f"ESP {'enabled' if self.features['esp'] else 'disabled'}")

    def _toggle_aimbot(self) -> None:
        self.features["aimbot"] = not self.features["aimbot"]
        log.info(f"Aimbot {'enabled' if self.features['aimbot'] else 'disabled'}")

    def _toggle_no_terror(self) -> None:
        self.features["no_terror"] = not self.features["no_terror"]
        log.info(f"No Terror Radius {'enabled' if self.features['no_terror'] else 'disabled'}")

    def _toggle_fast_vault(self) -> None:
        self.features["fast_vault"] = not self.features["fast_vault"]
        log.info(f"Fast Vault {'enabled' if self.features['fast_vault'] else 'disabled'}")

    def _toggle_fast_pallet(self) -> None:
        self.features["fast_pallet"] = not self.features["fast_pallet"]
        log.info(f"Fast Pallet {'enabled' if self.features['fast_pallet'] else 'disabled'}")

    def _toggle_skill_check(self) -> None:
        self.features["skill_check_bot"] = not self.features["skill_check_bot"]
        log.info(f"Skill Check Bot {'enabled' if self.features['skill_check_bot'] else 'disabled'}")

    def _toggle_infinite_bp(self) -> None:
        self.features["infinite_bloodpoints"] = not self.features["infinite_bloodpoints"]
        log.info(f"Infinite Bloodpoints {'enabled' if self.features['infinite_bloodpoints'] else 'disabled'}")

    def _unlock_perks_once(self) -> None:
        if self.mem.attached:
            addr = self.mem.base_address + self.offsets.PERK_UNLOCK_FLAG
            self.mem.write_int(addr, 1)
            log.info("Perks unlocked")
            self.features["unlock_perks"] = True

    def _unlock_skins_once(self) -> None:
        if self.mem.attached:
            addr = self.mem.base_address + self.offsets.SKIN_UNLOCK_FLAG
            self.mem.write_int(addr, 1)
            log.info("Skins unlocked")
            self.features["unlock_skins"] = True

    def _toggle_auto_farm(self) -> None:
        self.features["auto_farm"] = not self.features["auto_farm"]
        log.info(f"Auto Farm {'enabled' if self.features['auto_farm'] else 'disabled'}")

    async def trainer_loop(self) -> None:
        """High‑frequency memory writes for active cheats."""
        while self.running:
            if not self.mem.attached:
                await asyncio.sleep(0.5)
                continue
            try:
                if self.features["no_terror"]:
                    self.mem.write_float(
                        self.mem.base_address + self.offsets.TERROR_RADIUS, 0.0
                    )
                if self.features["fast_vault"]:
                    self.mem.write_float(
                        self.mem.base_address + self.offsets.VAULT_SPEED_MULT, 3.0
                    )
                if self.features["fast_pallet"]:
                    self.mem.write_float(
                        self.mem.base_address + self.offsets.PALLET_SPEED_MULT, 3.0
                    )
                if self.features["infinite_bloodpoints"]:
                    self.mem.write_int(
                        self.mem.base_address + self.offsets.BLOODPOINTS, 9999999
                    )
                if self.features["skill_check_bot"]:
                    self.mem.write_int(
                        self.mem.base_address + self.offsets.SKILLCHECK_PERFECT, 1
                    )
            except Exception as e:
                log.error(f"Trainer loop error: {e}")
            await asyncio.sleep(0.05)

    def register_hotkeys(self) -> None:
        for key, action in self.hotkey_actions.items():
            keyboard.add_hotkey(key, action)
        keyboard.add_hotkey("f2", self.stop)

    def start(self) -> None:
        self.running = True
        self.register_hotkeys()
        self._update_discord("In‑game", "Trainer active")
        asyncio.ensure_future(self.trainer_loop())

    def stop(self) -> None:
        self.running = False
        keyboard.unhook_all()
        self._update_discord("Idle", "Trainer stopped")
        if self.mem.attached:
            self.mem.detach()
        log.info("Trainer stopped")
