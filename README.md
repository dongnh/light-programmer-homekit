# Light Programmer for HomeKit

Control [light-programmer](https://github.com/dongnh/light_programmer) from the Home app. Two switches appear in Apple Home — that is the interface. Siri, automations, and shared family access come along for free.

## Apple Home is the interface

Light Programmer runs quietly in the background. The Home app is where you actually touch it.

- **LP Auto.** Turn the schedule on or off. When off, lights stay where they are; when on, the daemon resumes following your circadian schedule on the next tick.
- **LP Kill.** All off. Every configured light goes dark and stays dark until you flip LP Auto back on.

Both switches respond to Siri ("Turn off LP Auto"), to scheduled Home automations ("At sunset, turn on LP Auto"), and to anyone you've shared the home with. You never need to SSH into the server, edit a file, or call an API to change how the house behaves tonight.

## How it fits together

```
Home app, Siri,  ─►  light-programmer-homekit  ─HTTP─►  light-programmer  ─►  matter_webcontrol  ─►  lights
Home automations     (HAP accessory bridge)            (/mode, /kill)
```

The bridge is intentionally thin. It holds no state. Every flip of a switch is a single HTTP call to the daemon, and the daemon owns the truth. If the bridge crashes or you restart it, your lights keep running on whatever the last decision was. Pairing survives across restarts because the bridge's HomeKit identity is derived from the bridge name, not from the pairing file.

## Requirements

- macOS or Linux host on the same LAN as your Apple Home Hub (HomePod, Apple TV, or iPad).
- Python 3.10 or later.
- A reachable [light-programmer](https://github.com/dongnh/light_programmer) ≥ 0.6.0 with `--mode-state` enabled.

## Install

```bash
pip install -e .
```

## Run

```bash
light-programmer-homekit --config examples/config.json
```

On first launch, the bridge prints a HomeKit setup code. In the Home app, tap **Add Accessory → More options…**, choose **Light Programmer**, and enter the code. The two switches show up in your default room; move them wherever feels right.

## Configuration

See [`examples/config.json`](examples/config.json).

| Field | Default | Purpose |
|---|---|---|
| `programmer_url` | `http://127.0.0.1:7860` | Where light-programmer's mode API is reachable. |
| `bridge_name` | `Light Programmer` | The name Apple Home shows. Also seeds the stable HomeKit MAC. |
| `port` | `51826` | HAP port. Must be reachable from your Home Hub. |
| `state_path` | `./accessory.state` | Where HomeKit pairing keys live. Back this up if you care about avoiding a re-pair. |
| `poll_interval` | `5` | How often (seconds) the bridge re-reads light-programmer's mode flags, so the Home app stays in sync when something else flips them. |

Changing `bridge_name` changes the HomeKit MAC and forces a fresh pairing. Pick a name you'll keep.

## Programmer contract

The bridge talks to three endpoints on light-programmer:

- `GET /mode` → `{"auto": bool, "kill": bool}`
- `POST /mode` body `{"auto": bool}` → `{"auto": bool}`
- `POST /kill` body `{"kill": bool}` → `{"kill": bool}`

Available in light-programmer 0.6.0 and later. Pass `--mode-state /path/to/mode.json` when launching light-programmer to turn them on.

## Status

Pre-alpha. Schema and endpoints may change before 1.0.

## License

MIT
