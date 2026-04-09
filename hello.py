# Hello World for Waveshare 2.13" V4 e-Paper on Raspberry Pi Pico 2 W

from machine import Pin, SPI
import framebuf
import utime


EPD_WIDTH       = 122  # Actual display width (will round to 128)
EPD_HEIGHT      = 250  # Actual display height

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13


class EPD_2in13_V4_Landscape(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        
        # Round width up to multiple of 8
        if EPD_WIDTH % 8 == 0:
            self.width = EPD_WIDTH
        else:
            self.width = (EPD_WIDTH // 8) * 8 + 8
        self.height = EPD_HEIGHT

        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.buffer = bytearray(self.height * self.width // 8)
        # NOTE: For landscape, swap width/height and use MONO_VLSB
        super().__init__(self.buffer, self.height, self.width, framebuf.MONO_VLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)

    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        print("e-Paper busy")
        self.delay_ms(10)
        while self.digital_read(self.busy_pin) == 1:
            self.delay_ms(10)
        print("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x22)
        self.send_data(0xF7)
        self.send_command(0x20)
        self.ReadBusy()

    def SetWindows(self, Xstart, Ystart, Xend, Yend):
        self.send_command(0x44)
        self.send_data((Xstart >> 3) & 0xFF)
        self.send_data((Xend >> 3) & 0xFF)
        self.send_command(0x45)
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0xFF)
        self.send_data(Yend & 0xFF)
        self.send_data((Yend >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E)
        self.send_data((x >> 3) & 0xFF)
        self.send_command(0x4F)
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.ReadBusy()

    def init(self):
        print("Initializing display...")
        self.reset()
        self.ReadBusy()

        self.send_command(0x12)  # SWRESET
        self.ReadBusy()

        self.send_command(0x01)  # Driver output control
        self.send_data((self.height - 1) & 0xFF)
        self.send_data(((self.height - 1) >> 8) & 0xFF)
        self.send_data(0x00)

        self.send_command(0x11)  # Data entry mode
        self.send_data(0x07)

        self.SetWindows(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x3C)  # Border waveform
        self.send_data(0x05)

        self.send_command(0x18)  # Temperature sensor
        self.send_data(0x80)

        self.ReadBusy()
        print("Display initialized!")

    def Clear(self):
        self.send_command(0x24)
        self.send_data1([0xFF] * self.height * int(self.width / 8))
        self.TurnOnDisplay()

    def display(self, image):
        self.send_command(0x24)
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10)
        self.send_data(0x01)
        self.delay_ms(100)
        print("Display sleeping")


# ============ HELLO WORLD ============

print("Starting Hello World...")

# Create display object
epd = EPD_2in13_V4_Landscape()

# Clear to white
epd.Clear()

# Fill white background
epd.fill(0xFF)

# Draw text (built-in 8x8 font)
# For landscape: x goes 0-249 (height), y goes 0-121 (width)
# Actually in landscape, the coordinates are swapped
epd.text("Hello World!", 10, 10, 0x00)
epd.text("Raspberry Pico", 10, 30, 0x00)
epd.text("2.13 e-Paper", 10, 50, 0x00)

# Draw a border rectangle
epd.rect(5, 5, 110, 70, 0x00)

# Show on display
epd.display(epd.buffer)

print("Done!")
utime.sleep(2)

# Optional: clear and sleep
# epd.Clear()
# epd.sleep()

print("Finished!")
