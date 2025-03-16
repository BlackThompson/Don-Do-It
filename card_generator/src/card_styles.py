from reportlab.lib.units import mm
from reportlab.lib import colors


def create_gradient_background(c, x, y, width, height, num_steps=50):
    """创建渐变背景"""
    for i in range(num_steps):
        ratio = i / float(num_steps)
        c.setFillColorRGB(
            0.98 - ratio * 0.08,
            0.98 - ratio * 0.08,
            1.0 - ratio * 0.05,
        )
        c.rect(
            x, y + (height * i / num_steps), width, height / num_steps, stroke=0, fill=1
        )


def draw_cutting_marks(c, x, y, width, height):
    """绘制切割辅助线"""
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(0.1 * mm)

    mark_length = 5 * mm

    # 四角切割标记
    for corner in [(x, y), (x + width, y), (x, y + height), (x + width, y + height)]:
        cx, cy = corner
        c.line(cx - mark_length, cy, cx + mark_length, cy)
        c.line(cx, cy - mark_length, cx, cy + mark_length)

    # 虚线切割线
    dash_length = 2 * mm
    space_length = 2 * mm

    # 水平虚线
    current_x = x
    while current_x < x + width:
        end_x = min(current_x + dash_length, x + width)
        c.line(current_x, y, end_x, y)
        c.line(current_x, y + height, end_x, y + height)
        current_x += dash_length + space_length

    # 垂直虚线
    current_y = y
    while current_y < y + height:
        end_y = min(current_y + dash_length, y + height)
        c.line(x, current_y, x, end_y)
        c.line(x + width, current_y, x + width, end_y)
        current_y += dash_length + space_length


def draw_border(
    c, x, y, width, height, corner_radius, line_width=0.8 * mm, color=(0.4, 0.4, 0.9)
):
    """绘制边框"""
    c.setStrokeColorRGB(*color)
    c.setLineWidth(line_width)
    c.roundRect(x, y, width, height, corner_radius)
