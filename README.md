# ISS Tracker for Raspberry Pi Pico 2 W + Waveshare e-Paper

Displays the current location of the International Space Station on a 2.13" e-ink display.

## Setup

### 1. WiFi Configuration

Copy the example config file and add your WiFi credentials:

```bash
cp config.py.example config.py
```

Edit `config.py` with your actual WiFi credentials:

```python
SSID = "YourActualNetworkName"
PASSWORD = "YourActualPassword"
```

**Note:** `config.py` is gitignored and won't be committed.

### 2. Upload to Pico

In Thonny, upload **both files** to the Pico:
- `iss_display.py`
- `config.py`

### 3. Run

Click the **Run** button (or press F5) in Thonny to start the tracker.

The display will:
- Connect to WiFi
- Fetch ISS location every 30 seconds
- Update the e-ink screen with coordinates and JST timestamp

## Files

- `iss_display.py` - Main application code
- `config.py` - WiFi credentials (gitignored, create from example)
- `config.py.example` - Template for config.py
- `hello.py` - Simple text demo
- `wifi_connect.py` - WiFi connection test

## Hardware

- Raspberry Pi Pico 2 W
- Waveshare 2.13" V4 e-Paper display
- Wiring: VCC→3.3V, GND→GND, DIN→GP10, CLK→GP11, CS→GP9, DC→GP8, RST→GP12, BUSY→GP13

## Stopping

Press **Ctrl+C** in the Thonny Shell to stop the loop, or unplug the Pico.
