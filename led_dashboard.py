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

import os          # Access environment variables (like MEOW_USERNAME)
import sys         # Exit the script if configuration is missing
import time        # Sleep between polling cycles
# rpi_ws281x is the low-level NeoPixel driver for Raspberry Pi.
# - PixelStrip: represents the physical LED strip (how many LEDs, which pin, brightness)
# - Color: packs red/green/blue values into a single integer the strip understands
from rpi_ws281x import PixelStrip, Color
# meow_sdk connects to the meow meow scratch API.
# - Meow: the client we use to talk to the API
# - MeowError: the exception raised when a request fails
from meow_sdk import Meow, MeowError

# This project reads from a PUBLIC endpoint, so it uses a username instead of
# an API key. Anyone can read public endpoints -- no secret needed. The other
# projects WRITE data (which needs an API key to prove you have permission).
USERNAME = os.environ.get("MEOW_USERNAME")
if not USERNAME:
    print("Set MEOW_USERNAME environment variable")
    sys.exit(1)

APP = "pi-led-dashboard"       # The app name on meow meow scratch
ENDPOINT = "colors"             # The endpoint within that app that holds the color
POLL_INTERVAL = 3  # seconds between each check for a new color

# LED strip configuration
LED_COUNT = 8       # Number of LEDs on your strip -- change to match yours
LED_PIN = 18        # GPIO18 (physical pin 12) -- the Pi's hardware PWM pin
# Brightness 0-255. 50 is comfortably dim. Higher values draw more power and
# can be blinding! At 255 with white, each LED draws ~60mA.
LED_BRIGHTNESS = 50

# Initialize in public/read-only mode using a username.
# Compare with Meow(api_key=...) used in other projects for authenticated writes.
api = Meow(username=USERNAME)
# Create the LED strip object and initialize the hardware PWM signal.
# PWM rapidly switches the data pin on/off in precise patterns to tell each
# LED what color to show. strip.begin() starts the PWM hardware.
strip = PixelStrip(LED_COUNT, LED_PIN, brightness=LED_BRIGHTNESS)
strip.begin()


def hex_to_color(hex_str):
    """Convert a hex color string like '#ff0000' to a Color object."""
    hex_str = hex_str.lstrip("#")  # Remove the leading '#' if present
    if len(hex_str) != 6:
        return Color(0, 0, 0)     # Invalid hex -> default to off (black)
    # A hex color like '#ff0000' has 3 pairs: ff=Red, 00=Green, 00=Blue.
    # int('ff', 16) converts hex to decimal (255). We slice the string to get
    # each color pair: characters 0-1 for red, 2-3 for green, 4-5 for blue.
    r = int(hex_str[0:2], 16)     # Red:   first two hex characters
    g = int(hex_str[2:4], 16)     # Green: middle two hex characters
    b = int(hex_str[4:6], 16)     # Blue:  last two hex characters
    return Color(r, g, b)


def set_all(color):
    """Set every LED on the strip to the same color, then push the update."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)  # Queue the color for LED #i
    strip.show()  # Send all queued colors to the strip in one burst


def main():
    print(f"LED dashboard running — polling every {POLL_INTERVAL}s")
    print("Press Ctrl+C to stop\n")

    last_color = None  # Track the last color so we can detect changes

    try:
        while True:
            try:
                # Fetch the current color from the public endpoint
                data = api.get(APP, ENDPOINT)
                color_hex = data.get("color", "#000000")  # Default to black/off

                # Only update LEDs when the color actually changes. Writing to
                # every LED takes time, so skip if nothing changed.
                if color_hex != last_color:
                    set_all(hex_to_color(color_hex))
                    print(f"Color set to {color_hex}")
                    last_color = color_hex

            except MeowError as e:
                print(f"Fetch failed: {e}")

            time.sleep(POLL_INTERVAL)  # Wait before polling again
    finally:
        # Turn all LEDs off (black) when the script exits. Without this they'd
        # stay stuck on the last color -- the strip has its own memory.
        set_all(Color(0, 0, 0))


if __name__ == "__main__":
    main()
