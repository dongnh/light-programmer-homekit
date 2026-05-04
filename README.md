# homekit-bridge

HomeKit bridge for [light-programmer](https://github.com/dongnh/light_programmer).
Exposes a small set of switches to Apple Home so the home automation policy
can be controlled from anywhere via Siri / Home app / iCloud:

- **Auto Mode** — toggle the programmer's scheduling loop on/off.
- **All Off** — kill switch; programmer turns every device off and stays off
  until Auto Mode is re-enabled.

## Architecture

```
 Apple Home  ─┐
 Siri        ─┼──► homekit-bridge ──HTTP──► light-programmer ──► matter_webcontrol ──► devices
 Automation  ─┘   (HAP accessory)         (/mode, /kill)
```

The bridge is a thin HTTP client. All policy state (Auto Mode flag, Kill flag)
lives in `light-programmer`. The bridge can crash or be restarted without
affecting the control loop.

## Install

```bash
pip install -e .
```

## Run

```bash
homekit-bridge --config examples/config.json
```

On first start, the bridge prints a HomeKit setup code. Pair via the Home app
("Add Accessory" → "More options").

## Configuration

See [`examples/config.json`](examples/config.json). Fields:

| Field | Default | Description |
|-------|---------|-------------|
| `programmer_url` | `http://127.0.0.1:7860` | Base URL of light-programmer's HTTP API. |
| `bridge_name` | `Light Programmer` | Display name in Apple Home. |
| `port` | `51826` | HAP port. |
| `state_path` | `./accessory.state` | Where to persist HomeKit pairing. |
| `poll_interval` | `5` | Seconds between state polls (to keep Apple Home in sync if mode changes from MCP/CLI). |

## Programmer contract

The bridge expects light-programmer to expose:

- `GET /mode` → `{"auto": bool, "kill": bool}`
- `POST /mode` body `{"auto": bool}` → `{"auto": bool}`
- `POST /kill` body `{"kill": bool}` → `{"kill": bool}`

These endpoints are added in light-programmer ≥ 0.6.0.

## Status

Pre-alpha. Schema and endpoints may change before 1.0.
