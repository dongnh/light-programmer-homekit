# Light Programmer for HomeKit

See your [light-programmer](https://github.com/dongnh/light_programmer) lights' health from the Home app.

## Overview

One sensor per light, plus one for the whole system. That is the entire interface.

Every light light-programmer manages appears in Apple Home as a sensor named "Communication to <light>". While the system can reach the light, the sensor reads open; when the light drops off — loses power, falls off the mesh — it reads closed. Turn on notifications for it in the Home app and you hear about it the moment it happens.

A system sensor named "Light Programmer" reports the daemon itself: open while it answers, closed when it stops. That one is the bridge's own check, so you are told even when the daemon is the thing that died.

The sensors respond to Home automations and to anyone you have shared the home with. No SSH, no log tailing — the house tells you when a light goes quiet.

## How it works

The bridge is intentionally thin. It holds no state of its own. Every poll is one HTTP call to light-programmer's `/lights`, which lists each light by the name you gave it and whether the system can currently reach it; the bridge mirrors that onto the sensors. light-programmer reads that reachability from matter_webcontrol, so a light that goes offline surfaces here within a poll.

The polarity is deliberate. A reachable light reads as open, a lost one as closed, so Apple's fixed wording — "<name> Opened" or "<name> Closed" — reads as plain English about the connection.

Pairing survives restarts. The HomeKit identity is derived from the bridge name, not the pairing file, so the accessory stays the same across reinstalls. Apple Home fixes the accessory set at pairing time, so the bridge learns the light list once at startup — add a light to light-programmer and restart the bridge to surface its sensor.

## Requirements

macOS or Linux on the same LAN as an Apple Home Hub. Python 3.10 or later. A reachable light-programmer 0.15.0 or newer (the release that serves `/lights`), launched with mode state enabled.

## Installation

Install the package into a virtual environment, then run the bridge with a config file pointing at your light-programmer instance.

On first launch the bridge prints a HomeKit setup code. In the Home app, choose Add Accessory, then More options, then Light Programmer, and enter the code. The sensors appear in your default room. Open any one and turn on its notifications to be alerted when that light — or the whole system — drops off.

## Configuration

A small JSON file. The fields you might touch are the programmer URL, the bridge name shown in Apple Home, the HAP port, the poll interval, `notify_prefix` — the text prepended to each light's name (default "Communication to ") — and `fail_threshold`, the number of consecutive failed `/lights` polls before the system sensor is declared down (default 3). The threshold debounces a single transient timeout so a brief light-programmer blip does not fire a false notification; recovery is immediate on the first good poll.

The light names themselves come from light-programmer's config, not here. The bridge name seeds the stable HomeKit MAC; changing it forces a fresh pairing. Pick a name you will keep.

A sample config lives in the examples directory.

## Status

Pre-alpha. Schema and endpoints may change before 1.0.

## Related projects

[light-programmer](https://github.com/dongnh/light_programmer) — the schedule brain this bridge watches.

[matter_webcontrol](https://github.com/dongnh/matter_webcontrol) — the Matter controller that reports each device's online/offline state.

## License

MIT
