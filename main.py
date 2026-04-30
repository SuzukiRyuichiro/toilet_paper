import time

import framebuf
import network
import urequests as requests

from config import PASSWORD, SSID
from epd2in13 import EPD_2in13_V4_Landscape
from text import draw_japanese_text

# Connect to wifi
wlan = network.WLAN(network.WLAN.IF_STA)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

wether_data = requests.get(
    url="https://epd-display.dragon-aka-scooter.workers.dev/"
).json()

epd = EPD_2in13_V4_Landscape()
epd.Clear()

epd.fill(0xFF)

for index, item in enumerate(wether_data):
    # 1. アイコンの描画
    epd.blit(
        framebuf.FrameBuffer(
            bytearray([bit ^ 0xFF for bit in item["weather"]["icon"]]),
            32,
            32,
            framebuf.MONO_HMSB,
        ),
        10,
        10 + 40 * index,
    )

    # 2. 日付の描画
    date_str_raw = item["date"]  # "2026-04-30T00:00:00.000Z"
    year = int(date_str_raw[0:4])
    month = int(date_str_raw[5:7])
    day = int(date_str_raw[8:10])
    tm = time.localtime(time.mktime((year, month, day, 0, 0, 0, 0, 0)))
    month_zen = "".join(["０１２３４５６７８９"[int(c)] for c in str(month)])
    day_zen = "".join(["０１２３４５６７８９"[int(c)] for c in str(day)])
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    weekday_zen = weekdays[tm[6]]
    date_str = (
        f"{month_zen}月{day_zen}日（{weekday_zen}） {item['weather']['description']}"
    )
    draw_japanese_text(epd, date_str, 52, 12 + 40 * index)

    # 3. 温度と降水量の描画
    max_temp_zen = "".join(
        ["０１２３４５６７８９"[int(c)] for c in str(int(item["temperature_2m_max"]))]
    )
    min_temp_zen = "".join(
        ["０１２３４５６７８９"[int(c)] for c in str(int(item["temperature_2m_min"]))]
    )
    rain_zen = "".join(
        ["０１２３４５６７８９"[int(c)] for c in str(int(item["precipitation_sum"]))]
    )
    temp_str = f"最高{max_temp_zen}℃　最低{min_temp_zen}℃　{rain_zen} ｍｍ"
    draw_japanese_text(epd, temp_str, 52, 28 + 40 * index)

epd.display(epd.buffer)
epd.delay_ms(30000)

epd.Clear()
