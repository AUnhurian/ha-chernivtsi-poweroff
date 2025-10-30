[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua/)

![HA Lviv PowerOff Logo](https://github.com/tsdaemon/ha-lviv-poweroff/blob/827c15582bb64c70568f6f7b322e926feeaa2592/icons/icon.png?raw=true)

# ⚡️ Home Assistant Chernivtsi PowerOff

An integration for electricity shutdown schedules of [ChernivtsiOblEnergo][chernivtsioblenergo].

This integration for [Home Assistant][home-assistant] provides information about planned electricity shutdowns of [ChernivtsiOblEnergo][chernivtsioblenergo] in Chernivtsi oblast:
calendar of planned shutdowns, and sensors for current state and next power on/off events.

**💡 Note:** This project is not affiliated with [ChernivtsiOblEnergo][chernivtsioblenergo] in any way. This integration is developed by an individual.
Provided data may be incorrect or misleading, follow the official channels for reliable information.

> This integration is inspired by [ha-yasno-outages](https://github.com/denysdovhan/ha-yasno-outages) by [Denys Dovhan](https://github.com/denysdovhan).

## Installation

The quickest way to install this integration is via [HACS][hacs-url] by clicking the button below:

[![Add to HACS via My Home Assistant][hacs-install-image]][hasc-install-url]

If it doesn't work, adding this repository to HACS manually by adding this URL:

1. Visit **HACS** → **Integrations** → **...** (in the top right) → **Custom repositories**
1. Click **Add**
1. Paste `https://github.com/oppenheimer14/ha-chernivtsi-poweroff` into the **URL** field
1. Chose **Integration** as a **Category**
1. **Chernivtsi PowerOff** will appear in the list of available integrations. Install it normally.

## Usage

This integration is configurable via UI. On **Devices and Services** page, click **Add Integration** and search for **Chernivtsi PowerOff**.

Select your group (1..12) in the configuration. The integration parses the official schedule on [oblenergo.cv.ua][chernivtsioblenergo].

Then you can add the integration to your dashboard and see the information about the next planned outages.

![Sensors](https://github.com/tsdaemon/ha-lviv-poweroff/blob/827c15582bb64c70568f6f7b322e926feeaa2592/pics/example_sensor.png?raw=true)

Integration also provides a calendar view of planned outages. You can add it to your dashboard as well via [Calendar card][calendar-card].

![Calendar](https://github.com/tsdaemon/ha-lviv-poweroff/blob/827c15582bb64c70568f6f7b322e926feeaa2592/pics/example_calendar.png?raw=true)

<!-- References -->

[chernivtsioblenergo]: https://oblenergo.cv.ua/
[home-assistant]: https://www.home-assistant.io/
[hacs-url]: https://github.com/hacs/integration
[hasc-install-url]: https://my.home-assistant.io/redirect/hacs_repository/?owner=oppenheimer14&repository=ha-chernivtsi-poweroff&category=integration
[hacs-install-image]: https://my.home-assistant.io/badges/hacs_repository.svg
[calendar-card]: https://www.home-assistant.io/dashboards/calendar/

ha-yasno-outages
