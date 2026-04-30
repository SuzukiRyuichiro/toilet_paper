import framebuf
from misakifont import MisakiFont


def banner(text, size=8):
    mf = MisakiFont()
    if size == 16:
        top_buf = []
        bottom_buf = []
        for char in text:
            code = ord(char)
            fontdata = mf.font(code, False)
            width = 8 if mf.isZenkaku(code) else 4
            for w in range(width):
                top_byte = 0
                bottom_byte = 0
                for row in range(8):
                    if fontdata[row] & (0x80 >> w):
                        if row < 4:
                            # bits 0-3 of original map to 0-7 of top_byte
                            top_byte |= (0x03 << (2 * row))
                        else:
                            # bits 4-7 of original map to 0-7 of bottom_byte
                            bottom_byte |= (0x03 << (2 * (row - 4)))
                # Horizontal doubling: repeat the column twice
                top_buf.append(top_byte)
                top_buf.append(top_byte)
                bottom_buf.append(bottom_byte)
                bottom_buf.append(bottom_byte)
        return top_buf + bottom_buf
    else:
        buf = []
        for char in text:
            code = ord(char)
            fontdata = mf.font(code, False)
            width = 8 if mf.isZenkaku(code) else 4
            for w in range(width):
                data = 0
                for row in range(8):
                    if fontdata[row] & (0x80 >> w):
                        data |= 0x01 << row
                buf.append(data)
        return buf


# 日本語テキストを特定の座標に描画する補助関数
def draw_japanese_text(epd, text, x, y, size=8):
    font_buf = banner(text, size)
    # textの文字数によってバッファの長さが変わるため、動的に幅を指定
    if size == 16:
        width = len(font_buf) // 2
    else:
        width = len(font_buf)
        
    if width == 0:
        return

    epd.blit(
        framebuf.FrameBuffer(
            bytearray([i ^ 0xFF for i in font_buf]), width, size, framebuf.MONO_VLSB
        ),
        x,
        y,
    )
