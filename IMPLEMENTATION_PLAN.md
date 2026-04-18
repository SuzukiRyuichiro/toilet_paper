# EPD Info Display — Implementation Plan

## Overview

A Raspberry Pi Pico 2 W + Waveshare 2.13" V4 e-paper display that cycles through 3 information screens (Weather, Rubbish Duty, News), with all data aggregation and rendering handled by a Cloudflare Worker.

## Architecture

```
Pico (deep sleep) ──Wake every 1h──→ Fetch bitmap from Worker → Update EPD → Sleep
                                           │
Worker (Cron every 30min) ────────────────┘
     │
     ├──→ Weather API ──┐
     ├──→ Rubbish API ─┼→ Render to 1-bit bitmap → Cache in KV
     └──→ News API ─────┘
```

## Display Specs

- **Resolution:** 250×122 pixels (landscape)
- **Color:** 1-bit (black/white only)
- **Font:** Misaki 8×8 (Japanese), rendered server-side by Worker
- **Capacity at 8px:** ~28 chars × 12 lines (with 2px padding)
- **Capacity at 16px:** ~15 chars × 7 lines

## Screen Layouts

### Screen 1: Weather
```
┌─────────────────────────────┐
│ WEATHER              12:34  │  ← HH:MM staleness timestamp
│─────────────────────────────│
│ TOKYO          24°C         │  ← 16px
│ Rain PM  Hum: 65%           │
│─────────────────────────────│
│ TOMORROW                    │
│ 25°/18°  Sunny              │
│─────────────────────────────│
│ 3-DAY                       │
│ Wed:22° Rain                │
│ Thu:20° Cloudy              │
│ Fri:23° Sun                 │
└─────────────────────────────┘
```

### Screen 2: Rubbish Duty
```
┌─────────────────────────────┐
│ RUBBISH DUTY         12:34  │
│─────────────────────────────│
│ TODAY                       │  ← 16px
│ BURNABLE                    │  ← 16px
│─────────────────────────────│
│ DUTY: TARO YAMADA           │
│─────────────────────────────│
│ THIS WEEK          Taro     │
│ Mon  Burnable      Hanako   │
│ Wed  Plastic        Jiro    │
│ Fri  Recyclable              │
└─────────────────────────────┘
```

### Screen 3: News
```
┌─────────────────────────────┐
│ WORLD NEWS           12:34  │
│─────────────────────────────│
│ 1. NASA announces           │
│    new Mars mission         │
│─────────────────────────────│
│ 2. Tech stocks rise         │
│    after earnings           │
│─────────────────────────────│
│ 3. Japan GDP up 2%          │
│    Q1 forecast              │
│─────────────────────────────│
│ 4. Olympics 2028            │
│    LA venue update     NHK  │
└─────────────────────────────┘
```

## Implementation Steps

### 1. Cloudflare Worker — Data Aggregation

**Endpoint:** `GET /`

**Cron trigger:** Every 30 minutes, fetch fresh data from external APIs and store in KV.

**External data sources:**
- **Weather:** OpenWeatherMap API or similar (current + 3-day forecast)
- **Rubbish Duty:** A predefined schedule (static JSON in Worker or KV) mapping dates to duty person + category
- **News:** RSS feed or News API (top 4 headlines, truncated to fit)

**Worker responsibilities:**
1. On cron: fetch all 3 APIs, normalize, store in KV
2. On GET request: read cached data from KV, render to 1-bit bitmap (250×122), return as binary response

### 2. Worker — Bitmap Rendering

**Why bitmap from Worker:**
- Pico code stays minimal (~20 lines: fetch + display)
- No font files or rendering logic needed on Pico
- Layout changes deploy server-side only (no re-flashing Pico)
- Payload: ~4KB per screen, trivial over WiFi

**Rendering approach:**
- Custom pure-JS 1-bit bitmap renderer (~50 lines), no external canvas libraries
- Worker-side Misaki font data embedded as a JS constant (~12KB for all 1710 glyphs)
- Worker renders all text including Japanese directly onto the bitmap

**Bitmap byte order (`MONO_HLSB`):**
- Worker outputs pixels in standard top-down, left-to-right, LSB-first order
- Pico wraps the bytes in MicroPython's `framebuf.FrameBuffer` and calls `epd.display()`
- The existing EPD driver handles all internal byte reordering for landscape mode

**Response format — all 3 screens in one request:**
```
[bitmap1 (4000 bytes)][bitmap2 (4000 bytes)][bitmap3 (4000 bytes)]
```
Total response size: ~12KB raw binary. No compression. Pico splits the response into 3 chunks and cycles through them locally using `lightsleep()`.

**Offline fallback:**
- If the Worker is unreachable, Pico displays a hardcoded "OFFLINE" static bitmap stored in flash

### 3. KV Storage

KV keys: `weather`, `rubbish`, `news`. Each value is a JSON string with `updated_at` (Unix timestamp) and the raw data.

KV is used instead of D1 because:
- Simpler key-value model fits this use case perfectly
- Faster cold-start reads (no SQLite initialization)
- No schema migrations needed

### 4. Pico — Client Code

**Flow:**
1. Wake from deep sleep
2. Connect WiFi (using `config.py` credentials)
3. HTTP GET to Worker endpoint
4. Receive ~12KB response, split into 3 × 4000-byte bitmaps
5. Store current screen index to flash (persist across deep sleep resets)
6. Wrap first bitmap in `framebuf.FrameBuffer`, call `epd.display()`
7. Sleep for 20 minutes via `lightsleep()`
8. On wake: load next bitmap, display, repeat
9. After all 3 shown: deep sleep for remaining time until next 1h cycle
10. If Worker unreachable at any point: display "OFFLINE" fallback bitmap

**Fallback bitmap:**
- A ~4000-byte "OFFLINE" or "?" bitmap hardcoded as a Python bytes literal in flash
- Displayed when the Worker doesn't respond

**Power budget:**
- WiFi active: ~100mA × 5s per wake cycle
- Deep sleep: ~1.3µA
- lightsleep (screen cycling): ~1.5mA (no WiFi, keeps display state)
- Estimated: ~3.3 mAh/day on battery

**Screen rotation:**
- Option A: Pico cycles screens by waking every 20 minutes (3 screens × 20min = 1h)
- Option B: Pico wakes every 1h, fetches all 3 screens, uses `machine.lightsleep()` to cycle locally
- **Recommended: Option B** — all 3 screens arrive in one request; no WiFi reconnect needed between screens

### 5. Configuration

**Pico side (`config.py`):**
```python
WIFI_SSID = "..."
WIFI_PASSWORD = "..."
WORKER_URL = "https://epd-display.YOUR-SUBDOMAIN.workers.dev"
```

**Worker side (wrangler.toml env vars):**
- `WEATHER_API_KEY`
- `NEWS_API_KEY` (if needed)
- KV binding for cache namespace

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Render location | Worker (bitmap) | Pico stays minimal, layout changes deploy server-side |
| Bitmap renderer | Custom pure-JS (~50 lines) | `@napi-rs/canvas` incompatible with Workers |
| Japanese font | Embedded in Worker (~12KB Misaki) | Worker renders all text including Japanese |
| Cache storage | KV | Simpler than D1, faster cold-start |
| Bitmap byte order | MONO_HLSB | Worker display-agnostic, Pico uses FrameBuffer |
| Compression | None | 12KB raw is trivial over WiFi |
| Response format | Single concatenated binary (12KB) | One HTTP request, all 3 screens |
| Staleness | HH:MM timestamp on each screen | User always knows how recent the data is |
| Worker failure | Hardcoded "OFFLINE" bitmap | Graceful degradation, no confused blank screen |
| Screen cycling | lightsleep on Pico | No WiFi reconnect between screens |

## Files to Create/Modify

### Cloudflare Worker (new project)
- `src/index.ts` — Worker entry: cron handler + HTTP handler
- `src/renderer.ts` — Custom 1-bit bitmap renderer (~50 lines)
- `src/font-misaki.ts` — Misaki 8×8 font data as JS constant (~12KB)
- `src/weather.ts` — Weather API fetch + normalize
- `src/rubbish.ts` — Rubbish schedule lookup
- `src/news.ts` — News fetch + truncate
- `wrangler.toml` — KV binding, cron schedule, env vars

### Pico (modify existing)
- `main.py` — Rewrite: WiFi connect → fetch 12KB → split 3 bitmaps → cycle with lightsleep
- `config.py.example` — Add `WORKER_URL` field
- `epd2in13.py` — No changes (existing driver works)
- `japanese.py` — Fix bitwise OR bug on line 12 (`epd.width | 122` → `epd.width`); fix font scaling so size > 1 draws proper 2×2 pixel blocks
- `misakifont/` — No changes (Misaki now lives in Worker, but these stay for future Pico-side use if ever needed)
- `epdconfig.py` — Keep (not used by Pico but may be useful for Linux SBCs)

## Risks & Mitigations

- **WiFi connection failures:** Retry 3× with backoff, then display offline bitmap and sleep
- **Worker cold start:** KV cached data means response is fast even on cold start
- **API rate limits:** Cron every 30min = 48 requests/day per API, well within free tiers
- **E-paper ghosting:** Use full refresh (not partial) every cycle; accept ~2s refresh time
- **Pico deep sleep resets state:** Persist current screen index to flash before sleeping