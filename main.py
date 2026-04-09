# ISS Tracker for Raspberry Pi Pico 2 W + Waveshare 2.13" V4 e-Paper
# Auto-runs on boot when named main.py
# Clears display on exit/interrupt

from machine import Pin, SPI
import network
import socket
import json
import time
import framebuf
import sys

# ============ CONFIGURATION ============
try:
    from config import SSID, PASSWORD
except ImportError:
    SSID = "YOUR_WIFI_NAME"
    PASSWORD = "YOUR_WIFI_PASSWORD"
    print("Warning: config.py not found")

REFRESH_INTERVAL = 30  # seconds

# ============ E-PAPER DRIVER ============
EPD_WIDTH = 122
EPD_HEIGHT = 250

RST_PIN = 12
DC_PIN = 8
CS_PIN = 9
BUSY_PIN = 13


class EPD_2in13_V4_Landscape(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)

        if EPD_WIDTH % 8 == 0:
            self.width = EPD_WIDTH
        else:
            self.width = (EPD_WIDTH // 8) * 8 + 8
        self.height = EPD_HEIGHT

        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.height, self.width, framebuf.MONO_VLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

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
        self.reset()
        self.ReadBusy()
        self.send_command(0x12)
        self.ReadBusy()
        self.send_command(0x01)
        self.send_data((self.height - 1) & 0xFF)
        self.send_data(((self.height - 1) >> 8) & 0xFF)
        self.send_data(0x00)
        self.send_command(0x11)
        self.send_data(0x07)
        self.SetWindows(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)
        self.send_command(0x3C)
        self.send_data(0x05)
        self.send_command(0x18)
        self.send_data(0x80)
        self.ReadBusy()
        print("Display ready")

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


# ============ WIFI & HTTP ============


def connect_wifi():
    print("Connecting to WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("Waiting...")
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError("WiFi connection failed")

    status = wlan.ifconfig()
    print(f"Connected! IP: {status[0]}")
    return wlan


def fetch_iss_location():
    """Fetch ISS current location from open-notify API"""
    print("Fetching ISS location...")

    try:
        addr_info = socket.getaddrinfo("api.open-notify.org", 80)[0]
    except:
        addr = ("23.253.146.138", 80)
    else:
        addr = addr_info[4]

    s = socket.socket()
    s.settimeout(10)
    s.connect(addr)

    request = b"GET /iss-now.json HTTP/1.1\r\nHost: api.open-notify.org\r\nConnection: close\r\n\r\n"
    s.send(request)

    response = b""
    while True:
        try:
            chunk = s.recv(1024)
            if not chunk:
                break
            response += chunk
        except:
            break
    s.close()

    response_str = response.decode("utf-8")

    if "\r\n\r\n" in response_str:
        body = response_str.split("\r\n\r\n", 1)[1]
    else:
        body = response_str

    data = json.loads(body)

    if data.get("message") == "success":
        iss_data = data["iss_position"]
        return iss_data["latitude"], iss_data["longitude"]
    else:
        raise RuntimeError("API returned error")


def update_display(epd, lat, lon):
    """Update the e-ink display with ISS location"""
    epd.fill(0xFF)  # White background

    # Draw border
    epd.rect(5, 5, 240, 110, 0x00)

    # Title
    epd.text("ISS TRACKER", 10, 10, 0x00)

    # Show coordinates
    epd.text(f"Lat: {lat}", 15, 35, 0x00)
    epd.text(f"Lon: {lon}", 15, 55, 0x00)

    # Timestamp in JST
    epd.text("Updated:", 15, 80, 0x00)
    t = time.time()
    tm = time.localtime(t)
    time_str = "{:02d}:{:02d}:{:02d}".format(tm[3], tm[4], tm[5])
    epd.text(time_str, 15, 95, 0x00)

    # Show on display
    epd.display(epd.buffer)


# ============ CLEANUP ON EXIT ============


def cleanup_display(epd):
    """Clear display and put to sleep on exit"""
    print("\nCleaning up...")
    try:
        epd.fill(0xFF)  # White
        epd.text("Stopped", 10, 50, 0x00)
        epd.display(epd.buffer)
        time.sleep(2)
        epd.Clear()  # Full clear
        epd.sleep()
        print("Display cleared and sleeping")
    except Exception as e:
        print(f"Cleanup error: {e}")


# ============ MAIN ============


def main():
    epd = None

    try:
        # Connect to WiFi
        connect_wifi()

        # Initialize display
        print("Initializing display...")
        epd = EPD_2in13_V4_Landscape()
        epd.Clear()

        # Main loop - refresh every 30 seconds
        refresh_count = 0
        while True:
            print(f"\n=== Refresh #{refresh_count + 1} ===")

            # Fetch ISS location
            try:
                lat, lon = fetch_iss_location()
                print(f"ISS Location: {lat}, {lon}")
            except Exception as e:
                print(f"Error fetching data: {e}")
                lat, lon = "Error", "Error"

            # Update display
            print("Updating display...")
            update_display(epd, lat, lon)

            refresh_count += 1
            print(f"Waiting {REFRESH_INTERVAL} seconds...")
            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Always clean up the display, even if error
        if epd:
            cleanup_display(epd)
        print("Goodbye!")
        sys.exit()


if __name__ == "__main__":
    main()
