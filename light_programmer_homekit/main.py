"""Entry point — wires HAP driver and accessories."""
import argparse
import hashlib
import json
import logging
import signal
import time

from pyhap.accessory_driver import AccessoryDriver

from .accessory import (
    build_bridge, DEFAULT_PREFIX, DEFAULT_POLL_INTERVAL, DEFAULT_FAIL_THRESHOLD,
)
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

    client = ProgrammerClient(cfg["programmer_url"],
                              api_key=cfg.get("programmer_api_key"))
    bridge_name = cfg.get("bridge_name", "Light Programmer")
    prefix = cfg.get("notify_prefix", DEFAULT_PREFIX)
    interval = cfg.get("poll_interval", DEFAULT_POLL_INTERVAL)
    fail_threshold = cfg.get("fail_threshold", DEFAULT_FAIL_THRESHOLD)

    # HomeKit accessories are fixed at pairing time, so the light set must be
    # known before driver.start(). Retry while light-programmer boots — both run
    # as launchd services and may come up together.
    lights = None
    for attempt in range(30):  # ~90s
        lights = client.get_lights()
        if lights is not None:
            break
        logging.info("Waiting for light-programmer /lights (attempt %d)…", attempt + 1)
        time.sleep(3)
    reachable = lights is not None
    if not reachable:
        logging.warning(
            "light-programmer unreachable at startup; exposing only the system "
            "sensor. Restart this bridge once light-programmer is up to pick up "
            "the per-light sensors."
        )
        lights = []
    logging.info("Building bridge '%s' with %d light sensor(s)", bridge_name, len(lights))

    mac = cfg.get("mac") or _stable_mac(f"homekit-bridge:{bridge_name}")
    logging.info(f"Using stable MAC {mac} for bridge '{bridge_name}'")
    driver = AccessoryDriver(
        port=cfg.get("port", 51826),
        persist_file=cfg.get("state_path", "./accessory.state"),
        address=cfg.get("address"),
        mac=mac,
    )
    bridge = build_bridge(driver, bridge_name, client, lights,
                          reachable=reachable, prefix=prefix, interval=interval,
                          fail_threshold=fail_threshold)
    driver.add_accessory(accessory=bridge)

    signal.signal(signal.SIGTERM, lambda *_: driver.stop())
    driver.start()


if __name__ == "__main__":
    main()
