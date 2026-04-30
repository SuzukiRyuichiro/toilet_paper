import framebuf
from misakifont import MisakiFont


def banner(epd, text):
    mf = MisakiFont()
    buf = []
    for char in text:
        code = ord(char)
        fontdata = mf.font(code, False)
        width = 8 if mf.isZenkaku(code) else 4
        for w in range(width):
            data = 0
            for row in range(8):
                if fontdata[row] & (0x80 >> w):
                    # 前回の修正：垂直方向のビット順序(VLSB)に合わせる
                    data |= 0x01 << row
            buf.append(data)
    return buf


# 日本語テキストを特定の座標に描画する補助関数
def draw_japanese_text(epd, text, x, y):
    font_buf = banner(epd, text)
    # textの文字数によってバッファの長さが変わるため、動的に幅を指定
    width = len(font_buf)
    if width == 0:
        return

    epd.blit(
        framebuf.FrameBuffer(
            bytearray([i ^ 0xFF for i in font_buf]), width, 8, framebuf.MONO_VLSB
        ),
        x,
        y,
    )
