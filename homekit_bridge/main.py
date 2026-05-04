"""Entry point — wires HAP driver, accessories, and a poller for state sync."""
import argparse
import json
import logging
import signal
import threading
import time

from pyhap.accessory_driver import AccessoryDriver

from .accessory import build_bridge
from .programmer_client import ProgrammerClient


def _poll_loop(client: ProgrammerClient, auto_sw, kill_sw,
               interval: float, stop: threading.Event):
    """Keep HomeKit state in sync if mode flips outside the bridge (CLI/MCP)."""
    while not stop.wait(interval):
        state = client.get_mode()
        if not state:
            continue
        if "auto" in state:
            auto_sw.push(state["auto"])
        if "kill" in state:
            kill_sw.push(state["kill"])


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
    bridge, auto_sw, kill_sw = build_bridge(
        driver, cfg.get("bridge_name", "Light Programmer"), client,
    )
    driver.add_accessory(accessory=bridge)

    stop = threading.Event()
    poller = threading.Thread(
        target=_poll_loop,
        args=(client, auto_sw, kill_sw, float(cfg.get("poll_interval", 5)), stop),
        daemon=True,
    )
    poller.start()

    signal.signal(signal.SIGTERM, lambda *_: driver.stop())
    try:
        driver.start()
    finally:
        stop.set()


if __name__ == "__main__":
    main()
