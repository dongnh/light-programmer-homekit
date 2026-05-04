"""Entry point — wires HAP driver and accessories.

The bridge has no background polling thread. Each `On` characteristic uses a
`getter_callback` that reads the programmer state on demand, so Apple Home
stays in sync with mode changes from MCP/CLI without racing with HAP-python's
asyncio loop (which is what causes "No Response" symptoms).
"""
import argparse
import json
import logging
import signal

from pyhap.accessory_driver import AccessoryDriver

from .accessory import build_bridge
from .programmer_client import ProgrammerClient


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
    driver = AccessoryDriver(
        port=cfg.get("port", 51826),
        persist_file=cfg.get("state_path", "./accessory.state"),
    )
    bridge, _, _ = build_bridge(
        driver, cfg.get("bridge_name", "Light Programmer"), client,
    )
    driver.add_accessory(accessory=bridge)

    signal.signal(signal.SIGTERM, lambda *_: driver.stop())
    driver.start()


if __name__ == "__main__":
    main()
