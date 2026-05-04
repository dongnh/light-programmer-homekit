"""Entry point — wires HAP driver and accessories."""
import argparse
import hashlib
import json
import logging
import signal

from pyhap.accessory_driver import AccessoryDriver

from .accessory import build_bridge
from .programmer_client import ProgrammerClient


def _stable_mac(seed: str) -> str:
    """Derive a deterministic locally-administered MAC from `seed` so that
    factory-resetting accessory.state does not generate a new HomeKit device id
    (which leaves stale mDNS records behind and confuses Apple Home)."""
    h = hashlib.sha256(seed.encode()).digest()
    octets = list(h[:6])
    octets[0] = (octets[0] & 0xFC) | 0x02  # locally administered, unicast
    return ":".join(f"{b:02X}" for b in octets)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, help="Path to config JSON")
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args()

    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    with open(args.config) as f:
        cfg = json.load(f)

    client = ProgrammerClient(cfg["programmer_url"])
    bridge_name = cfg.get("bridge_name", "Light Programmer")
    mac = cfg.get("mac") or _stable_mac(f"homekit-bridge:{bridge_name}")
    logging.info(f"Using stable MAC {mac} for bridge '{bridge_name}'")
    driver = AccessoryDriver(
        port=cfg.get("port", 51826),
        persist_file=cfg.get("state_path", "./accessory.state"),
        address=cfg.get("address"),
        mac=mac,
    )
    bridge, _, _ = build_bridge(driver, bridge_name, client)
    driver.add_accessory(accessory=bridge)

    signal.signal(signal.SIGTERM, lambda *_: driver.stop())
    driver.start()


if __name__ == "__main__":
    main()
