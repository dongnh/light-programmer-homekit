# Light Programmer for HomeKit

Control [light-programmer](https://github.com/dongnh/light_programmer) from the Home app.

## Overview

Two switches in Apple Home. That is the entire interface.

LP Auto turns the schedule on or off. When off, lights stay where they are. When on, the daemon resumes following your circadian schedule on the next tick.

LP Kill takes everything dark. Every configured light goes off and stays off until LP Auto comes back on.

Both switches respond to Siri, to scheduled Home automations, and to anyone you have shared the home with. No SSH. No config files. No API calls. The house behaves the way you ask, from the room you are in.

## How it works

The bridge is intentionally thin. It holds no state. Every switch flip is a single HTTP call to light-programmer, and the daemon owns the truth. If the bridge crashes or restarts, your lights keep running on the last decision made.

Pairing survives restarts. The HomeKit identity is derived from the bridge name, not from the pairing file, so the accessory stays the same accessory across reinstalls.

A short poll keeps the Home app in sync when something else flips the mode flags — another bridge, a script, or the daemon itself on boot.

## Requirements

macOS or Linux on the same LAN as an Apple Home Hub. Python 3.10 or later. A reachable light-programmer 0.6.0 or newer, launched with mode state enabled.

## Installation

Install the package into a virtual environment, then run the bridge with a config file pointing at your light-programmer instance.

On first launch the bridge prints a HomeKit setup code. In the Home app, choose Add Accessory, then More options, then Light Programmer, and enter the code. The two switches appear in your default room.

## Configuration

A small JSON file. The defaults are sensible; the fields you might touch are the programmer URL, the bridge name shown in Apple Home, the HAP port, and the poll interval.

The bridge name seeds the stable HomeKit MAC. Changing it forces a fresh pairing. Pick a name you will keep.

A sample config lives in the examples directory.

## Status

Pre-alpha. Schema and endpoints may change before 1.0.

## Related projects

[light-programmer](https://github.com/dongnh/light_programmer) — the schedule brain this bridge controls.

[matter_webcontrol](https://github.com/dongnh/matter_webcontrol) — the Matter controller light-programmer drives.

## License

MIT
