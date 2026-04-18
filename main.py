from epd2in13 import EPD_2in13_V4_Landscape
from japanese import draw_text

epd = EPD_2in13_V4_Landscape()
epd.Clear()

epd.fill(0xFF)
draw_text(epd, "こんにちは世界", 0, 20)
draw_text(epd, "ハローワールド", 0, 30, 2)

epd.display(epd.buffer)

epd.delay_ms(10000)

epd.Clear()
