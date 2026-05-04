"""HomeKit accessory definitions."""
import logging

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SWITCH

from . import __version__
from .programmer_client import ProgrammerClient

MANUFACTURER = "dongnh"
MODEL = "LightProgrammerBridge"


def _set_info(accessory: Accessory, serial: str, model: str) -> None:
    """HomeKit requires non-empty Manufacturer/Model/Serial/FirmwareRevision —
    Apple Home drops the session and shows 'No Response' otherwise."""
    info = accessory.get_service("AccessoryInformation")
    info.configure_char("Manufacturer", value=MANUFACTURER)
    info.configure_char("Model", value=model)
    info.configure_char("SerialNumber", value=serial)
    info.configure_char("FirmwareRevision", value=__version__)


class _ModeSwitch(Accessory):
    category = CATEGORY_SWITCH

    def __init__(self, driver, display_name: str, client: ProgrammerClient,
                 field: str):
        super().__init__(driver, display_name)
        self.client = client
        self.field = field  # 'auto' or 'kill'

        _set_info(self, serial=f"lp-{field}", model=f"LightProgrammer{field.capitalize()}Switch")
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
    _set_info(bridge, serial="lp-bridge", model=MODEL)
    auto_sw = _ModeSwitch(driver, "LP Auto", client, "auto")
    kill_sw = _ModeSwitch(driver, "LP Kill", client, "kill")
    bridge.add_accessory(auto_sw)
    bridge.add_accessory(kill_sw)
    return bridge, auto_sw, kill_sw
