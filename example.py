from epd2in13 import EPD_2in13_V4_Landscape

epd = EPD_2in13_V4_Landscape()
epd.Clear()

epd.fill(0xFF)
epd.text("Waveshare", 0, 10, 0x00)
epd.text("ePaper-2.13_V4", 0, 20, 0x00)
epd.text("Raspberry Pico", 0, 30, 0x00)
epd.text("Hello World", 0, 40, 0x00)
epd.display(epd.buffer)
epd.delay_ms(2000)

epd.vline(5, 55, 60, 0x00)
epd.vline(100, 55, 60, 0x00)
epd.hline(5, 55, 95, 0x00)
epd.hline(5, 115, 95, 0x00)
epd.line(5, 55, 100, 115, 0x00)
epd.line(100, 55, 5, 115, 0x00)
epd.display(epd.buffer)
epd.delay_ms(2000)

epd.rect(130, 10, 40, 80, 0x00)
epd.fill_rect(190, 10, 40, 80, 0x00)
epd.Display_Base(epd.buffer)
epd.delay_ms(2000)

epd.init()
for i in range(0, 10):
    epd.fill_rect(175, 105, 10, 10, 0xFF)
    epd.text(str(i), 177, 106, 0x00)
    epd.displayPartial(epd.buffer)

print("sleep")
epd.init()
epd.Clear()
epd.delay_ms(2000)
epd.sleep()

epd = EPD_2in13_V4_Portrait()
epd.Clear()

epd.fill(0xFF)
epd.text("Waveshare", 0, 10, 0x00)
epd.text("ePaper-2.13_V4", 0, 30, 0x00)
epd.text("Raspberry Pico", 0, 50, 0x00)
epd.text("Hello World", 0, 70, 0x00)
epd.display(epd.buffer)
epd.delay_ms(2000)

epd.vline(10, 90, 60, 0x00)
epd.vline(90, 90, 60, 0x00)
epd.hline(10, 90, 80, 0x00)
epd.hline(10, 150, 80, 0x00)
epd.line(10, 90, 90, 150, 0x00)
epd.line(90, 90, 10, 150, 0x00)
epd.display(epd.buffer)
epd.delay_ms(2000)

epd.rect(10, 180, 50, 40, 0x00)
epd.fill_rect(60, 180, 50, 40, 0x00)
epd.Display_Base(epd.buffer)
epd.delay_ms(2000)

epd.init()
for i in range(0, 10):
    epd.fill_rect(40, 230, 40, 10, 0xFF)
    epd.text(str(i), 60, 230, 0x00)
    epd.displayPartial(epd.buffer)

print("sleep")
epd.init()
epd.Clear()
epd.delay_ms(2000)
epd.sleep()
