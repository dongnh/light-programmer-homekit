"""HomeKit accessory definitions."""
import logging

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SWITCH
from pyhap.accessory import Accessory

from .programmer_client import ProgrammerClient


class _ModeSwitch(Accessory):
    category = CATEGORY_SWITCH

    def __init__(self, driver, display_name: str, client: ProgrammerClient,
                 field: str):
        super().__init__(driver, display_name)
        self.client = client
        self.field = field  # 'auto' or 'kill'

        serv = self.add_preload_service("Switch")
        self.char_on = serv.configure_char(
            "On", setter_callback=self._set_on, value=False,
        )

    def _set_on(self, value: bool):
        try:
            if self.field == "auto":
                self.client.set_auto(value)
            else:
                self.client.set_kill(value)
        except Exception as e:
            logging.error(f"[{self.display_name}] failed to push state: {e}")

    def push(self, value: bool):
        """Update HomeKit-visible state without invoking the setter."""
        self.char_on.set_value(bool(value), should_notify=True)


def build_bridge(driver: AccessoryDriver, name: str,
                 client: ProgrammerClient) -> tuple[Bridge, _ModeSwitch, _ModeSwitch]:
    bridge = Bridge(driver, name)
    auto_sw = _ModeSwitch(driver, "Auto Mode", client, "auto")
    kill_sw = _ModeSwitch(driver, "All Off", client, "kill")
    bridge.add_accessory(auto_sw)
    bridge.add_accessory(kill_sw)
    return bridge, auto_sw, kill_sw
