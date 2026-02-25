"""
Pi LED Dashboard
================
Reads color data from a public meow meow scratch endpoint
and displays it on a NeoPixel LED strip. Update the endpoint
from your phone or browser to change the lights!

Wiring (NeoPixel strip → Pi):
  DIN → GPIO18 (pin 12) — must be PWM-capable
  VCC → 5V external supply (not the Pi's 5V for long strips)
  GND → GND (shared with Pi)

Setup:
  sudo pip install -r requirements.txt   # needs root for NeoPixels
  sudo MEOW_USERNAME="jake" python led_dashboard.py
"""

import os
import sys
import time
from rpi_ws281x import PixelStrip, Color
from meow_sdk import Meow, MeowError

USERNAME = os.environ.get("MEOW_USERNAME")
if not USERNAME:
    print("Set MEOW_USERNAME environment variable")
    sys.exit(1)

APP = "pi-led-dashboard"
ENDPOINT = "colors"
POLL_INTERVAL = 3  # seconds

# LED strip config
LED_COUNT = 8
LED_PIN = 18
LED_BRIGHTNESS = 50

api = Meow(username=USERNAME)
strip = PixelStrip(LED_COUNT, LED_PIN, brightness=LED_BRIGHTNESS)
strip.begin()


def hex_to_color(hex_str):
    """Convert a hex color string like '#ff0000' to a Color object."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        return Color(0, 0, 0)
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return Color(r, g, b)


def set_all(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


def main():
    print(f"LED dashboard running — polling every {POLL_INTERVAL}s")
    print("Press Ctrl+C to stop\n")

    last_color = None

    try:
        while True:
            try:
                data = api.get(APP, ENDPOINT)
                color_hex = data.get("color", "#000000")

                if color_hex != last_color:
                    set_all(hex_to_color(color_hex))
                    print(f"Color set to {color_hex}")
                    last_color = color_hex

            except MeowError as e:
                print(f"Fetch failed: {e}")

            time.sleep(POLL_INTERVAL)
    finally:
        set_all(Color(0, 0, 0))


if __name__ == "__main__":
    main()
