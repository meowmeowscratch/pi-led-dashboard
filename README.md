# Pi LED Dashboard

Control lights from your phone! This project reads a color value from the internet and displays it on a strip of NeoPixel LEDs connected to your Raspberry Pi. Change the color on the meow meow scratch website, and the lights update within seconds. It works the opposite way from the other projects — instead of sending sensor data UP to the cloud, it pulls data DOWN to control hardware.

---

## What you'll learn

- **How NeoPixel (WS2812B) LED strips work** — individually addressable LEDs that can each show any color, all controlled from a single data wire.
- **PWM (Pulse Width Modulation)** — the technique the Pi uses to send precisely timed signals to the LED strip. The data pin rapidly switches on and off in specific patterns to tell each LED what color to display.
- **Hex color codes and RGB values** — how colors are represented as numbers (like `#ff0000` for red) and how to convert between hex and the red/green/blue values that LEDs understand.
- **Polling an API** — how to repeatedly check a web endpoint for new data on a timer.
- **The difference between reading from and writing to an API** — most projects in this collection *write* sensor data to the cloud. This one *reads* data from the cloud to control hardware. That distinction matters for authentication (more on that below).

---

## What you'll need

### Hardware

- **Raspberry Pi (any model with GPIO pins)** — This is the small computer that runs the code and controls the LEDs. Any Pi with the 40-pin GPIO header will work (Pi 3, Pi 4, Pi Zero W, etc.).

- **A NeoPixel (WS2812B) LED strip** — Each LED can be individually controlled to show any color. They chain together on a single data wire. Look for strips labeled "WS2812B" or "NeoPixel." The default code is set up for 8 LEDs, but you can change the `LED_COUNT` variable to match your strip.

- **A 5V external power supply (for strips longer than 8 LEDs)** — NeoPixels are power-hungry! Each LED can draw up to 60mA at full white brightness. Don't try to power a long strip from the Pi's 5V pin — it can't provide enough current and you might damage the Pi. For a short strip of 8 or fewer LEDs at low brightness, the Pi's 5V pin is usually fine.

- **Jumper wires** — Short wires with connectors on the ends, used to hook everything together. You'll need at least 3: one for data, one for power, and one for ground.

### Important wiring note

> **Connect the GND of the Pi and the GND of the power supply together!** This is called a "common ground" — without it, the data signal won't work. The Pi and the LED strip need to share the same electrical reference point, or the LEDs won't understand the data being sent to them.

### Software

- **Python 3** — The programming language this script is written in. It comes pre-installed on Raspberry Pi OS.
- **A meow meow scratch account** — Sign up at [meowmeowscratch.com](https://meowmeowscratch.com) if you don't have one yet.

> **Note:** This script must be run with `sudo` because NeoPixels use PWM (Pulse Width Modulation), which requires root access on the Pi. This is a hardware-level limitation — the Pi's PWM hardware can only be accessed by the root user.

---

## Wiring diagram

```
    Raspberry Pi         NeoPixel Strip          5V Power Supply
    +-----------+        +-+--+--+--+--+        +--------+
    |           |        |                |        |        |
    | GPIO18 o--+--data--+-> DIN          |        |        |
    | (pin 12)  |        |                |        |        |
    |           |        | VCC <-----------+------- +5V     |
    |           |        |                |        |        |
    | GND    o--+--------+-> GND <---------+------- GND    |
    | (pin 6)   |        +-+--+--+--+--+        +--------+
    +-----------+

    IMPORTANT: The Pi's GND and the power supply's GND MUST be connected!
    The arrows on the LED strip show data direction -- connect to the INPUT end.
```

### Pin reference table

| NeoPixel Strip Pin | Connects to                | Notes                                                    |
|--------------------|----------------------------|----------------------------------------------------------|
| DIN (Data In)      | GPIO18 (physical pin 12)   | Must be GPIO18 — it's the Pi's hardware PWM pin          |
| VCC (Power)        | 5V external power supply   | Or Pi's 5V pin for 8 or fewer LEDs at low brightness     |
| GND (Ground)       | GND on Pi AND power supply | Both grounds must be connected together (common ground)   |

---

## How this project is different

> **Read vs. Write — this project is the reverse pattern!**
>
> Most projects in this collection SEND data to meow meow scratch (temperature, motion events, button presses, etc.). They *write* to the API, which requires an API key to prove you have permission.
>
> This project does the opposite — it READS data from the API and uses it to control hardware. Because it only reads public data, it uses `MEOW_USERNAME` (not `MEOW_API_KEY`). Anyone can read a public endpoint — no secret key needed. Think of it like a public website: anyone can visit and read it, but only the owner can edit it.
>
> In code, that looks like:
> ```python
> # Other projects (writing data — needs a secret key):
> api = Meow(api_key="your-secret-key")
> api.set(APP, ENDPOINT, {"temperature": 72})
>
> # This project (reading data — just needs a username):
> api = Meow(username="your-username")
> data = api.get(APP, ENDPOINT)
> ```

---

## Step-by-step setup

### Step 1: Install the required libraries

Open a terminal on your Raspberry Pi and run:

```bash
sudo pip install -r requirements.txt
```

**Why `sudo`?** The `rpi_ws281x` library (which controls the NeoPixels) needs to access hardware-level PWM on the Pi. That requires root (administrator) privileges. Installing with `sudo` makes the library available when you run the script as root later.

The `rpi_ws281x` library is the low-level driver that knows how to send the precisely timed signals that NeoPixel LEDs expect. Without it, Python wouldn't be able to talk to the LED strip.

### Step 2: Set up your meow meow scratch account

1. Go to [meowmeowscratch.com](https://meowmeowscratch.com) and sign up (or log in).
2. Note your **username** — you'll need it to run the script.

### Step 3: Create a PUBLIC app with a static endpoint

This is the most important setup step. The script reads color data from a specific place on meow meow scratch, so you need to create that place first.

1. Create a new app called **`pi-led-dashboard`**.
2. Make sure the app is set to **PUBLIC**. This is required because the script reads data using only a username (no API key). If the app is private, the script won't be able to read it.
3. Create a **static** endpoint called **`colors`**.
4. Set the endpoint's payload to:

```json
{"color": "#ff0000"}
```

The value `#ff0000` is a hex color code for bright red. You can change it to any hex color:
- `#00ff00` = green
- `#0000ff` = blue
- `#ff00ff` = purple
- `#ffff00` = yellow
- `#ffffff` = white (draws the most power!)
- `#000000` = off (black)

### Step 4: Understand MEOW_USERNAME vs. MEOW_API_KEY

You might have seen other projects in this collection use `MEOW_API_KEY`. Here's the difference:

| Variable         | Used for        | Who can do it        | This project? |
|------------------|-----------------|----------------------|---------------|
| `MEOW_API_KEY`   | Writing data    | Only the account owner | No            |
| `MEOW_USERNAME`  | Reading public data | Anyone             | **Yes**       |

Since this project only *reads* a public endpoint (it never writes anything), all it needs is the username of the account that owns the endpoint.

### Step 5: Run the script

```bash
sudo MEOW_USERNAME="your-username" python led_dashboard.py
```

Replace `your-username` with your actual meow meow scratch username.

**What this command does:**
- `sudo` — runs the script with root privileges (required for NeoPixel PWM access).
- `MEOW_USERNAME="your-username"` — sets an environment variable that the script reads to know which account to look up.
- `python led_dashboard.py` — runs the script.

You should see output like:

```
LED dashboard running — polling every 3s
Press Ctrl+C to stop

Color set to #ff0000
```

### Step 6: Change the color!

Go back to the meow meow scratch dashboard in your browser (or phone), edit the `colors` endpoint payload, and change the hex color value. Within 3 seconds, your LEDs will update to the new color.

---

## How the code works

### Hex-to-RGB conversion

A hex color like `#ff0000` is actually three numbers packed together:

```
  #  f f  0 0  0 0
     ^^^  ^^^  ^^^
     Red  Grn  Blu
```

- **Red** = `ff` = 255 (maximum)
- **Green** = `00` = 0 (none)
- **Blue** = `00` = 0 (none)

Each pair of characters is a number from 0 to 255, written in hexadecimal (base 16) instead of decimal (base 10). The code uses `int('ff', 16)` to convert `ff` from hex to the decimal number `255`.

The function slices the string into three pairs and converts each one:

```python
r = int(hex_str[0:2], 16)   # first two characters  -> red
g = int(hex_str[2:4], 16)   # middle two characters  -> green
b = int(hex_str[4:6], 16)   # last two characters    -> blue
```

### The polling loop with change detection

The script runs in an infinite loop, checking the API every 3 seconds:

1. **Fetch** the current color from the meow meow scratch endpoint.
2. **Compare** it to the last color we displayed.
3. **Only update the LEDs if the color changed.** Sending data to every LED takes time (each LED needs 24 bits of precisely timed data), so we skip the update if nothing changed.
4. **Wait** 3 seconds, then repeat.

This "poll and compare" pattern is simple and reliable. The change detection prevents unnecessary LED updates and reduces flicker.

### Cleanup on exit

When you press Ctrl+C to stop the script, the `finally` block runs and sets all LEDs to black (off). Without this cleanup, the LEDs would stay stuck on the last color forever — even after the script stops — because the LED strip has its own memory and keeps displaying whatever it was last told to show.

---

## Troubleshooting

### LEDs don't light up at all
- **Check your power supply.** Make sure the NeoPixel strip is getting 5V power. If you're using an external supply, make sure it's plugged in and turned on.
- **Check the data direction.** NeoPixel strips have arrows printed on them showing the data direction. You must connect to the INPUT end (the arrow should point AWAY from your wire). If you connect to the output end, nothing will happen.
- **Check the common ground.** The Pi's GND and the power supply's GND must be connected together. Without a common ground, the data signal is meaningless to the LEDs.

### Script crashes with a permission error
- **You must run with `sudo`.** NeoPixels require root access for PWM. Run:
  ```bash
  sudo MEOW_USERNAME="your-username" python led_dashboard.py
  ```

### Only the first LED works
- **Check your data pin.** The code uses GPIO18 (physical pin 12). Make sure your data wire is connected to the correct pin. GPIO18 is the Pi's hardware PWM pin — other pins won't work reliably with NeoPixels.

### Colors look wrong (e.g., red shows as green)
- **Your strip might use GRB instead of RGB.** Some NeoPixel strips expect colors in Green-Red-Blue order instead of Red-Green-Blue. If your colors are swapped, you may need to change the `Color(r, g, b)` call to `Color(g, r, b)` in the code.

### Script says "Fetch failed" or can't read the endpoint
- **Check that your app is PUBLIC.** The script reads data using only a username (no API key). If the app is private, it won't be accessible.
- **Check your username.** Make sure the `MEOW_USERNAME` value matches your meow meow scratch username exactly (it's case-sensitive).
- **Check the app and endpoint names.** The script looks for an app called `pi-led-dashboard` with an endpoint called `colors`. Make sure those names match exactly.

### LEDs flicker or show random colors
- **Check your wiring connections.** Loose jumper wires are the most common cause of flickering.
- **Shorten your data wire.** Long data wires can pick up interference. Keep the wire between the Pi and the first LED as short as possible.

---

## API setup (detailed)

This section summarizes the meow meow scratch configuration needed for this project.

1. **Create an app** named `pi-led-dashboard`.
2. **Set the app to PUBLIC.** This is essential. The script reads data using a username, not an API key, so the endpoint must be publicly readable.
3. **Create a static endpoint** named `colors`.
4. **Set the payload** to a JSON object with a `color` key containing a hex color string:

```json
{"color": "#ff0000"}
```

The hex color must:
- Start with `#` (the code strips it automatically, but include it for clarity).
- Be exactly 6 hex digits after the `#` (two for red, two for green, two for blue).
- Use valid hex characters: `0-9` and `a-f` (case doesn't matter).

To change the LED color, simply update this payload value on the meow meow scratch dashboard. The Pi will pick up the change within 3 seconds (the default polling interval).
