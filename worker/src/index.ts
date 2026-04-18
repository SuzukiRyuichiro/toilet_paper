// Phase 1: Worker scaffolding with hardcoded fake bitmaps
// Establishes the wire format (3 × SCREEN_SIZE bytes concatenated) before real data

import { BitmapRenderer, SCREEN_SIZE } from "./renderer";

function createFakeScreen(title: string, body: string): Uint8Array {
  const r = new BitmapRenderer();
  r.clear();

  // Title bar (black fill)
  r.fillRect(0, 0, 250, 16, true);
  r.drawText(title, 4, 4, 1, 200);

  // Divider line
  r.hline(0, 249, 18, true);

  // Body text
  r.drawText(body, 4, 24, 1, 242);

  return r.getSlice();
}

export default {
  async fetch(_request: Request): Promise<Response> {
    // Stub data — replace with real KV reads in Phase 2
    const weatherBmp = createFakeScreen("WEATHER", "TOKYO 24C RAIN PM");
    const rubbishBmp = createFakeScreen("RUBBISH", "TODAY: BURNABLE");
    const newsBmp = createFakeScreen("NEWS", "1. NASA ANNOUNCES...");

    const response = new Uint8Array(SCREEN_SIZE * 3);
    response.set(weatherBmp, 0);
    response.set(rubbishBmp, SCREEN_SIZE);
    response.set(newsBmp, SCREEN_SIZE * 2);

    return new Response(response, {
      headers: { "Content-Type": "application/octet-stream" },
    });
  },
};