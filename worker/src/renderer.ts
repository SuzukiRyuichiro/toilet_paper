// 1-bit bitmap renderer for Waveshare 2.13" V4 (250x122 landscape)
// Output format: MONO_HLSB (row-major, LSB-first)
// Each byte = 8 horizontal pixels (bit=1 white, bit=0 black)

import { MISAKI_FONT_TABLE, MISAKI_FONT_DATA } from "./font-misaki";

const WIDTH = 250;
const HEIGHT = 122;
const BYTES_PER_ROW = Math.ceil(WIDTH / 8); // 32 bytes
const BUFFER_SIZE = BYTES_PER_ROW * HEIGHT; // 3904 bytes

// 1710 glyphs, 7 bytes each. Tofu fallback: 0x25A1 = □
const FONT_LEN = 7;
const FONT_TOFU = 0x25a1;

function binsearch(code: number): number {
  let lo = 0;
  let hi = MISAKI_FONT_TABLE.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const c = MISAKI_FONT_TABLE[mid];
    if (c === code) return mid;
    if (c < code) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}

function getGlyph(code: number): Uint8Array {
  const idx = binsearch(code);
  const fontIdx = idx >= 0 ? idx : binsearch(FONT_TOFU);
  const offset = fontIdx * FONT_LEN;
  return MISAKI_FONT_DATA.slice(offset, offset + FONT_LEN);
}

function isZenkaku(code: number): boolean {
  return !(code >= 0x20 && code <= 0x7e) && !(code >= 0xff61 && code <= 0xff9f);
}

function hankakuToZenkaku(code: number): number {
  if (code >= 0x20 && code <= 0x7e) {
    // Basic Latin -> Full-width (offset by 0xfee0)
    return code + 0xfee0;
  }
  if (code >= 0xff61 && code <= 0xff9f) {
    // Half-width katakana -> Full-width katakana (offset by 0xff60 - 0xff61)
    return code + 0x60;
  }
  return code;
}

// Character width: 8px for zenkaku (CJK), 4px for hankaku (ASCII, half-width katakana)
function charWidth(code: number): number {
  return isZenkaku(code) ? 8 : 4;
}

export class BitmapRenderer {
  private buffer: Uint8Array;

  constructor() {
    this.buffer = new Uint8Array(BUFFER_SIZE);
  }

  // Clear all pixels to white (0xFF bytes)
  clear(): void {
    this.buffer.fill(0xff);
  }

  // Set a single pixel: x=0..249, y=0..121
  // x and y coordinates map directly to the display's landscape orientation
  setPixel(x: number, y: number, black: boolean): void {
    if (x < 0 || x >= WIDTH || y < 0 || y >= HEIGHT) return;
    const byteIndex = y * BYTES_PER_ROW + (x >> 3);
    const bitIndex = 7 - (x & 7); // MSB-first within byte
    if (black) {
      this.buffer[byteIndex] &= ~(1 << bitIndex);
    } else {
      this.buffer[byteIndex] |= 1 << bitIndex;
    }
  }

  // Draw a vertical line
  vline(x: number, y1: number, y2: number, black = true): void {
    for (let y = y1; y <= y2; y++) this.setPixel(x, y, black);
  }

  // Draw a horizontal line
  hline(x1: number, x2: number, y: number, black = true): void {
    for (let x = x1; x <= x2; x++) this.setPixel(x, y, black);
  }

  // Draw a rectangle outline
  rect(x: number, y: number, w: number, h: number, black = true): void {
    this.hline(x, x + w - 1, y, black);
    this.hline(x, x + w - 1, y + h - 1, black);
    this.vline(x, y, y + h - 1, black);
    this.vline(x + w - 1, y, y + h - 1, black);
  }

  // Draw a filled rectangle
  fillRect(x: number, y: number, w: number, h: number, black = true): void {
    for (let dy = 0; dy < h; dy++) {
      for (let dx = 0; dx < w; dx++) {
        this.setPixel(x + dx, y + dy, black);
      }
    }
  }

  // Draw text using Misaki 8x8 font
  // x, y: top-left corner of first character
  // size: 1 (native 8x8) or 2 (16x16, each pixel becomes 2x2 block)
  // Returns x coordinate after last character drawn
  drawText(text: string, x: number, y: number, size = 1, maxWidth?: number): number {
    let posX = x;

    for (const char of text) {
      let code = char.codePointAt(0) ?? 0;
      const cw = charWidth(code);

      if (maxWidth !== undefined && posX + cw * size > maxWidth) break;

      // Half-width characters: convert to full-width for font lookup
      if (!isZenkaku(code)) {
        code = hankakuToZenkaku(code);
      }

      const glyph = getGlyph(code);

      for (let row = 0; row < 8; row++) {
        const byte = glyph[row];
        for (let col = 0; col < 8; col++) {
          const black = (byte & (0x80 >> col)) !== 0;
          if (black) {
            if (size === 1) {
              this.setPixel(posX + col, y + row, true);
            } else {
              // size 2: fill 2x2 block
              this.setPixel(posX + col * 2, y + row * 2, true);
              this.setPixel(posX + col * 2 + 1, y + row * 2, true);
              this.setPixel(posX + col * 2, y + row * 2 + 1, true);
              this.setPixel(posX + col * 2 + 1, y + row * 2 + 1, true);
            }
          }
        }
      }

      posX += cw * size + size; // character width + spacing
    }

    return posX;
  }

  // Get the raw buffer (MONO_HLSB, 3904 bytes)
  getBuffer(): Uint8Array {
    return this.buffer;
  }

  // Get buffer as a slice (for concatenated multi-screen responses)
  getSlice(): Uint8Array {
    return this.buffer.slice(0, BUFFER_SIZE);
  }
}

export const SCREEN_SIZE = BUFFER_SIZE;
export { WIDTH, HEIGHT, BYTES_PER_ROW };