# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

MicroPython app for Raspberry Pi Pico 2 W + Waveshare 2.13" V4 e-paper display. The display cycles through 3 information screens (Weather, Rubbish Duty, News). All data aggregation and bitmap rendering is done by a Cloudflare Worker; the Pico is a pure display client.

**Target hardware:** Pico 2 W with display on SPI(1) (GP10=CLK, GP11=MOSI), GPIO: CS=9, DC=8, RST=12, BUSY=13

## Architecture

```
Cloudflare Worker (cron 30min)
  ├── fetch weather/rubbish/news
  └── render → 1-bit bitmap (250×122, MONO_HLSB)
        ↓ cached in KV
Pico 2 W (deep sleep, wakes hourly)
  ├── connect WiFi
  ├── fetch 12KB (3 bitmaps × 4000 bytes concatenated)
  ├── cycle: display bitmap → lightsleep 20min → next
  └── deep sleep until next hourly wake
```

**Bitmap format:** 250 (width) × 122 (height) × 1-bit = 4000 bytes per screen. Worker outputs `MONO_HLSB` (standard row-major, LSB-first). Pico wraps bytes in MicroPython `framebuf.FrameBuffer` and calls `epd.display()` — the existing `EPD_2in13_V4_Landscape` driver handles the internal landscape byte reordering.

**Response format:** `GET /` returns all 3 bitmaps concatenated (~12KB total, no compression).

## Commands

```bash
# Deploy Worker to Cloudflare
wrangler deploy

# Watch Worker logs
wrangler log

# Check Worker secret values
wrangler secret list
```

No build step for Pico code — files are uploaded directly to the device via Thonny or `ampy`.

## Known Bugs

- `japanese.py:12` — `epd.width | 122` is a bitwise OR, not a comparison. Text boundary check never triggers. Fix: `epd.width` (which is 128).
- `japanese.py` — `font_size` parameter scales pixel positions but not pixel size. At size 2, each font pixel is placed 2 positions apart instead of drawing a 2×2 block. Affects sizes > 1.

## Style

- 4 spaces, no tabs, lines under 100 chars
- Classes: PascalCase (`EPD_2in13_V4_Landscape`)
- Constants: UPPER_CASE
- Hardware pin mappings: RST=12, DC=8, CS=9, BUSY=13, SPI=SPI(1) @ 4MHz

## Commit Style

One concise sentence. No co-author lines. Example: `Add weather fetcher stub`

## Config

`config.py` (gitignored) holds WiFi credentials and `WORKER_URL`. Copy from `config.py.example`.