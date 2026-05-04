"""HomeKit accessory definitions.

Each switch uses both `setter_callback` (when iPhone toggles) and
`getter_callback` (when iPhone polls). Reading on demand keeps Apple Home in
sync with mode changes that originate outside the bridge (MCP/CLI) without
needing a background thread that races with HAP's event loop.
"""
import logging

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SWITCH

from .programmer_client import ProgrammerClient


class _ModeSwitch(Accessory):
    category = CATEGORY_SWITCH

    def __init__(self, driver, display_name: str, client: ProgrammerClient,
                 field: str):
        super().__init__(driver, display_name)
        self.client = client
        self.field = field  # 'auto' or 'kill'

        serv = self.add_preload_service("Switch")
        # Seed initial value from the programmer once at startup; after that we
        # rely on setter_callback to keep state in sync. A getter_callback would
        # block HAP-python's event loop on every poll and trip Apple Home's
        # "No Response" timeout.
        try:
            initial = bool(client.get_mode().get(field, False))
        except Exception as e:
            logging.warning(f"[{display_name}] initial state read failed: {e}")
            initial = False
        self.char_on = serv.configure_char(
            "On", setter_callback=self._set_on, value=initial,
        )

    def _set_on(self, value: bool):
        try:
            if self.field == "auto":
                self.client.set_auto(value)
            else:
                self.client.set_kill(value)
        except Exception as e:
            logging.error(f"[{self.display_name}] failed to push state: {e}")


def build_bridge(driver: AccessoryDriver, name: str,
                 client: ProgrammerClient) -> tuple[Bridge, _ModeSwitch, _ModeSwitch]:
    bridge = Bridge(driver, name)
    auto_sw = _ModeSwitch(driver, "Auto Mode", client, "auto")
    kill_sw = _ModeSwitch(driver, "All Off", client, "kill")
    bridge.add_accessory(auto_sw)
    bridge.add_accessory(kill_sw)
    return bridge, auto_sw, kill_sw
