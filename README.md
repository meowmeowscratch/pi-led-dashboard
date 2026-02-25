# Pi LED Dashboard

Read color data from a public [meow meow scratch](https://meowmeowscratch.com) endpoint and display it on a NeoPixel LED strip. Change the color from your phone — the Pi picks it up automatically!

This is the reverse of most projects here: instead of *sending* sensor data, it *reads* from the API to control hardware.

## Wiring

| NeoPixel strip | Connection |
|---------------|-----------|
| DIN           | GPIO18 (pin 12) |
| VCC           | 5V external power supply |
| GND           | GND (shared with Pi) |

For strips longer than 8 LEDs, use an external 5V supply — don't power them from the Pi directly.

## Setup

```bash
sudo pip install -r requirements.txt
sudo MEOW_USERNAME="your-username" python led_dashboard.py
```

Needs `sudo` because NeoPixels require root access on the Pi.

## API setup

Create a **public** app called `pi-led-dashboard` with a **static** endpoint called `colors`. Set the payload to:

```json
{"color": "#ff0000"}
```

Change the hex color value to update the LEDs.
