from misakifont import MisakiFont


def draw_text(epd, text, x, y, font_size=1):
    """Draw a string starting at (x, y)"""
    mf = MisakiFont()
    pos_x = x
    for char in text:
        code = ord(char)
        width = 8 if mf.isZenkaku(code) else 4

        if pos_x + width > epd.width | 122:  # Screen width check
            break

        font_data = mf.font(code)
        for row in range(8):
            byte = font_data[row]
            for col in range(width):
                if byte & (0x80 >> col):
                    epd.pixel(
                        int(font_size * (pos_x + col)), int(font_size * (y + row)), 0
                    )

        pos_x += width + 1  # for spacing
