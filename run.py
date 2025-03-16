from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
import math
from PIL import Image


def create_gradient_path(c, x, y, width, height, num_steps=50):
    for i in range(num_steps):
        ratio = i / float(num_steps)
        # 调整颜色值，使背景更亮
        c.setFillColorRGB(
            0.98 - ratio * 0.08,  # 从更亮的颜色开始，渐变的幅度更小
            0.98 - ratio * 0.08,
            1.0 - ratio * 0.05,  # 蓝色通道保持更高的亮度
        )
        c.rect(
            x, y + (height * i / num_steps), width, height / num_steps, stroke=0, fill=1
        )


def draw_decorative_pattern(c, x, y, size, color):
    c.setStrokeColorRGB(*color)
    c.setLineWidth(0.2 * mm)
    # 绘制装饰性圆形图案
    for i in range(3):
        radius = size - (i * size / 3)
        c.circle(x, y, radius, stroke=1, fill=0)
    # 绘制十字装饰
    line_length = size / 2
    c.line(x - line_length, y, x + line_length, y)
    c.line(x, y - line_length, x, y + line_length)


def draw_cutting_marks(c, x, y, width, height):
    # 设置切割线样式
    c.setStrokeColorRGB(0.5, 0.5, 0.5)  # 灰色切割线
    c.setLineWidth(0.1 * mm)  # 细线

    # 切割标记长度
    mark_length = 5 * mm

    # 绘制四角切割标记
    # 左上角
    c.line(x - mark_length, y + height, x, y + height)  # 水平线
    c.line(x, y + height + mark_length, x, y + height)  # 垂直线

    # 右上角
    c.line(x + width, y + height, x + width + mark_length, y + height)
    c.line(x + width, y + height + mark_length, x + width, y + height)

    # 左下角
    c.line(x - mark_length, y, x, y)
    c.line(x, y - mark_length, x, y)

    # 右下角
    c.line(x + width, y, x + width + mark_length, y)
    c.line(x + width, y - mark_length, x + width, y)

    # 绘制虚线切割线
    dash_length = 2 * mm
    space_length = 2 * mm

    # 绘制水平虚线
    current_x = x
    while current_x < x + width:
        end_x = min(current_x + dash_length, x + width)
        c.line(current_x, y, end_x, y)
        c.line(current_x, y + height, end_x, y + height)
        current_x += dash_length + space_length

    # 绘制垂直虚线
    current_y = y
    while current_y < y + height:
        end_y = min(current_y + dash_length, y + height)
        c.line(x, current_y, x, end_y)
        c.line(x + width, current_y, x + width, end_y)
        current_y += dash_length + space_length


def create_cards(filename, texts):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # 加载并调整 logo 大小
    logo_img = Image.open("Echo_Logo.png")
    # 设置 logo 的目标大小（以毫米为单位）
    logo_size = 50 * mm  # 可以调整这个值来改变 logo 大小

    # 计算宽高比
    aspect_ratio = logo_img.width / logo_img.height
    if aspect_ratio > 1:
        logo_width = logo_size
        logo_height = logo_size / aspect_ratio
    else:
        logo_height = logo_size
        logo_width = logo_size * aspect_ratio

    rows, cols = 3, 3
    margin_x, margin_y = 15 * mm, 15 * mm
    padding_x, padding_y = 8 * mm, 8 * mm

    card_width = (width - 2 * margin_x - (cols - 1) * padding_x) / cols
    card_height = (height - 2 * margin_y - (rows - 1) * padding_y) / rows

    corner_radius = 8 * mm

    # 首先绘制所有切割线
    for row in range(rows):
        for col in range(cols):
            x = margin_x + col * (card_width + padding_x)
            y = height - margin_y - (row + 1) * card_height - row * padding_y
            draw_cutting_marks(c, x, y, card_width, card_height)

    # 然后绘制卡片内容
    card_index = 0
    for row in range(rows):
        for col in range(cols):
            if card_index >= len(texts):
                break
            x = margin_x + col * (card_width + padding_x)
            y = height - margin_y - (row + 1) * card_height - row * padding_y

            # 绘制渐变背景
            create_gradient_path(c, x, y, card_width, card_height)

            # 绘制主边框
            c.setStrokeColorRGB(0.4, 0.4, 0.9)
            c.setLineWidth(0.8 * mm)
            c.roundRect(x, y, card_width, card_height, corner_radius)

            # 绘制内部边框
            inner_margin = 3 * mm
            c.setStrokeColorRGB(0.6, 0.6, 1.0)
            c.setLineWidth(0.3 * mm)
            c.roundRect(
                x + inner_margin,
                y + inner_margin,
                card_width - 2 * inner_margin,
                card_height - 2 * inner_margin,
                corner_radius / 2,
            )

            # 在卡片中心绘制 logo
            logo_x = x + (card_width - logo_width) / 2
            logo_y = y + (card_height - logo_height) / 2
            c.drawImage(
                "Echo_Logo.png", logo_x, logo_y, logo_width, logo_height, mask="auto"
            )

            card_index += 1

    c.save()


# Example Usage
texts = [f"Card {i+1}" for i in range(9)]
create_cards("cards.pdf", texts)
