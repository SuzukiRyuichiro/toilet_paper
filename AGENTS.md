# Repository Guidelines

## Project Overview

MicroPython application for Raspberry Pi Pico 2 W that displays the International Space Station's real-time location on a Waveshare 2.13" e-Paper display.

## Project Structure

```
.
├── main.py              # Main application (auto-runs on boot)
├── config.py            # WiFi credentials (gitignored, create from example)
├── config.py.example    # Template for config.py
├── hello.py             # Simple text demo for the e-paper display
├── clean.py             # Display cleanup utilities
├── pico_sdk_import.cmake # Pico SDK CMake import
└── README.md            # Setup and usage documentation
```

## Development Workflow

### Configuration

Copy the example config and add your WiFi credentials:

```bash
cp config.py.example config.py
```

Edit `config.py` with your network details. This file is gitignored and must never be committed.

### Deployment

Upload files to the Pico using Thonny IDE:
1. Connect the Pico via USB
2. Open Thonny and select the Pico interpreter
3. Upload `main.py` and `config.py` to the root filesystem
4. Press **Run** (F5) or reset the Pico to start

### Running Locally

The application runs directly on the Pico hardware. Use Thonny's Shell for interactive debugging. Press **Ctrl+C** to stop the loop.

## Coding Style

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Keep under 100 characters
- **Imports**: Group standard library, then third-party, then local
- **Constants**: UPPER_CASE for configuration values (e.g., `REFRESH_INTERVAL`, `EPD_WIDTH`)
- **Classes**: PascalCase (e.g., `EPD_2in13_V4_Landscape`)
- **Comments**: Use `# ============ SECTION ============` style for major blocks

## Hardware Configuration

Pin mappings for the Waveshare 2.13" V4 display:

| Display | Pico GPIO |
|---------|-----------|
| VCC     | 3.3V      |
| GND     | GND       |
| DIN     | GP10      |
| CLK     | GP11      |
| CS      | GP9       |
| DC      | GP8       |
| RST     | GP12      |
| BUSY    | GP13      |

## Commit Guidelines

- Use concise, descriptive commit messages
- Format: `<type>: <description>` (e.g., `fix: correct SPI initialization timing`)
- Types: `feat`, `fix`, `refactor`, `docs`, `test`

## Security Notes

- Never commit `config.py` or any file containing credentials
- Verify `.gitignore` includes sensitive files before committing
- Use `config.py.example` for sharing configuration structure without values
