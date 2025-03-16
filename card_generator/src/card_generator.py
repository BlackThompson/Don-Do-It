from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
from .card_styles import create_gradient_background, draw_cutting_marks, draw_border
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from PyPDF2 import PdfMerger
from PyPDF2 import PdfReader


class CardGenerator:
    def __init__(self, rows=3, cols=3, font_path=None):
        self.rows = rows
        self.cols = cols
        self.width, self.height = A4
        self.margin_x = self.margin_y = 15 * mm
        self.padding_x = self.padding_y = 8 * mm
        self.corner_radius = 8 * mm
        self.border_width = 4 * mm  # 添加边框宽度作为类属性

        # 注册中文字体
        if font_path is None:
            # 默认使用微软雅黑（如果没有指定字体路径）
            font_path = "C:/Windows/Fonts/msyh.ttc"
            bold_font_path = "C:/Windows/Fonts/msyhbd.ttc"  # 微软雅黑粗体

        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("Chinese", font_path))
            if os.path.exists(bold_font_path):
                pdfmetrics.registerFont(TTFont("ChineseBold", bold_font_path))
            else:
                print("警告：找不到粗体字体文件，将使用普通字体")
                pdfmetrics.registerFont(TTFont("ChineseBold", font_path))
        else:
            raise Exception(f"找不到字体文件: {font_path}，请指定正确的中文字体路径")

        # 计算卡片尺寸
        self.card_width = (
            self.width - 2 * self.margin_x - (self.cols - 1) * self.padding_x
        ) / self.cols
        self.card_height = (
            self.height - 2 * self.margin_y - (self.rows - 1) * self.padding_y
        ) / self.rows

    def _get_card_position(self, row, col):
        """计算卡片位置"""
        x = self.margin_x + col * (self.card_width + self.padding_x)
        y = (
            self.height
            - self.margin_y
            - (row + 1) * self.card_height
            - row * self.padding_y
        )
        return x, y

    def _calculate_font_size(self, text, max_width, max_height, start_size=48):
        """计算合适的字体大小，确保文字能够在指定宽度和高度内完整显示（支持自动换行）"""
        # 分割中英文
        chinese, english = text.split("\n")

        # 为中文和英文创建不同的样式
        def create_style(size, is_chinese=True):
            return ParagraphStyle(
                "CardText",
                fontName="ChineseBold",  # 使用粗体字体
                fontSize=size,
                leading=size * 1.2,  # 行间距
                alignment=TA_CENTER,
                spaceAfter=size * 0.3 if is_chinese else 0,  # 中文段落后有间距
                wordWrap=(
                    "CJK" if is_chinese else "Normal"
                ),  # 中文使用CJK换行，英文使用普通换行
                splitLongWords=False,  # 防止英文单词被切断
            )

        font_size = start_size
        while font_size > 12:
            # 中文使用当前字号
            chinese_style = create_style(font_size, True)
            # 英文使用较小字号（中文字号的0.5倍）
            english_style = create_style(font_size * 0.5, False)

            # 处理英文文本，在适当的位置添加换行
            words = english.split()
            processed_english = ""
            current_line = []

            for word in words:
                # 临时创建一个段落来测试宽度
                test_line = " ".join(current_line + [word])
                p_test = Paragraph(test_line, english_style)
                w, h = p_test.wrap(max_width, max_height)

                if w <= max_width:
                    current_line.append(word)
                else:
                    if current_line:  # 如果当前行有内容，添加到结果中
                        processed_english += " ".join(current_line) + "<br/>"
                        current_line = [word]
                    else:  # 如果单词太长，强制添加
                        processed_english += word + "<br/>"
                        current_line = []

            # 添加最后一行
            if current_line:
                processed_english += " ".join(current_line)

            # 创建段落对象
            p_chinese = Paragraph(chinese, chinese_style)
            p_english = Paragraph(processed_english, english_style)

            # 计算两段文字的尺寸
            w1, h1 = p_chinese.wrap(max_width, max_height)
            w2, h2 = p_english.wrap(max_width, max_height)

            total_width = max(w1, w2)
            total_height = h1 + h2

            # 如果文字能够适应指定空间，返回当前字体大小和组合的段落
            if total_width <= max_width and total_height <= max_height:
                return font_size, [p_chinese, p_english]

            font_size -= 1

        # 如果达到最小字体大小，使用最小字体
        chinese_style = create_style(12, True)
        english_style = create_style(6, False)  # 12 * 0.5

        # 使用最小字体重新处理英文文本
        words = english.split()
        processed_english = ""
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            p_test = Paragraph(test_line, english_style)
            w, h = p_test.wrap(max_width, max_height)

            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    processed_english += " ".join(current_line) + "<br/>"
                    current_line = [word]
                else:
                    processed_english += word + "<br/>"
                    current_line = []

        if current_line:
            processed_english += " ".join(current_line)

        p_chinese = Paragraph(chinese, chinese_style)
        p_english = Paragraph(processed_english, english_style)
        return 12, [p_chinese, p_english]

    def create_card_backs(
        self,
        output_file,
        logo_path,
        logo2_path,
        main_logo_size=200 * mm,
        corner_logo_size=60 * mm,
        total_cards=None,  # 新增参数：总卡片数量
    ):
        """生成卡片背面"""
        c = canvas.Canvas(output_file, pagesize=A4)
        cards_per_page = self.rows * self.cols
        total_pages = (
            (total_cards + cards_per_page - 1) // cards_per_page if total_cards else 1
        )
        current_card = 0

        # 加载logo（移到循环外以提高性能）
        main_logo = Image.open(logo2_path)
        main_aspect_ratio = main_logo.width / main_logo.height
        if main_aspect_ratio > 1:
            main_logo_width = main_logo_size
            main_logo_height = main_logo_size / main_aspect_ratio
        else:
            main_logo_height = main_logo_size
            main_logo_width = main_logo_size * main_aspect_ratio

        corner_logo = Image.open(logo_path)
        corner_aspect_ratio = corner_logo.width / corner_logo.height
        if corner_aspect_ratio > 1:
            corner_logo_width = corner_logo_size
            corner_logo_height = corner_logo_size / corner_aspect_ratio
        else:
            corner_logo_height = corner_logo_size
            corner_logo_width = corner_logo_size * corner_aspect_ratio

        for page in range(total_pages):
            # 绘制切割线
            for row in range(self.rows):
                for col in range(self.cols):
                    if total_cards and current_card >= total_cards:
                        break
                    x, y = self._get_card_position(row, col)
                    draw_cutting_marks(
                        c,
                        x - self.border_width / 2,
                        y - self.border_width / 2,
                        self.card_width + self.border_width,
                        self.card_height + self.border_width,
                    )

            # 绘制卡片内容
            for row in range(self.rows):
                for col in range(self.cols):
                    if total_cards and current_card >= total_cards:
                        break
                    x, y = self._get_card_position(row, col)

                    # 渐变背景
                    create_gradient_background(
                        c, x, y, self.card_width, self.card_height
                    )

                    # 设置边框样式
                    c.setStrokeColorRGB(0.6, 0.6, 0.95)  # 使用更浅的蓝色边框
                    c.setLineWidth(self.border_width)
                    c.rect(x, y, self.card_width, self.card_height)  # 使用直角矩形

                    # 内部边框（保持圆角）
                    inner_margin = 3 * mm
                    draw_border(
                        c,
                        x + inner_margin,
                        y + inner_margin,
                        self.card_width - 2 * inner_margin,
                        self.card_height - 2 * inner_margin,
                        self.corner_radius / 2,
                        line_width=0.3 * mm,
                        color=(0.6, 0.6, 1.0),
                    )

                    # 绘制中心Logo
                    main_logo_x = x + (self.card_width - main_logo_width) / 2
                    main_logo_y = y + (self.card_height - main_logo_height) / 2
                    c.drawImage(
                        logo2_path,
                        main_logo_x,
                        main_logo_y,
                        main_logo_width,
                        main_logo_height,
                        mask="auto",
                    )

                    # 绘制左上角Logo
                    margin = 1 * mm
                    c.drawImage(
                        logo_path,
                        x + margin,
                        y + self.card_height - corner_logo_height - margin,
                        corner_logo_width,
                        corner_logo_height,
                        mask="auto",
                    )

                    # 绘制右下角Logo
                    c.drawImage(
                        logo_path,
                        x + self.card_width - corner_logo_width - margin,
                        y + margin,
                        corner_logo_width,
                        corner_logo_height,
                        mask="auto",
                    )

                    current_card += 1

            # 如果还有更多卡片要绘制，创建新页面
            if current_card < (total_cards or float("inf")):
                c.showPage()

        c.save()

    def create_card_fronts(self, output_file, texts):
        """生成卡片正面"""
        c = canvas.Canvas(output_file, pagesize=A4)
        total_cards = len(texts)
        current_card = 0

        while current_card < total_cards:
            # 绘制所有卡片的切割线（考虑边框宽度）
            for row in range(self.rows):
                for col in range(self.cols):
                    x, y = self._get_card_position(row, col)
                    # 向外偏移半个边框宽度
                    draw_cutting_marks(
                        c,
                        x - self.border_width / 2,
                        y - self.border_width / 2,
                        self.card_width + self.border_width,
                        self.card_height + self.border_width,
                    )

            # 绘制卡片内容
            for row in range(self.rows):
                for col in range(self.cols):
                    if current_card >= total_cards:
                        break

                    x, y = self._get_card_position(row, col)

                    # 白色背景（直角）
                    c.setFillColorRGB(1, 1, 1)
                    c.rect(x, y, self.card_width, self.card_height, fill=1, stroke=0)

                    # 青色外边框（直角）
                    c.setStrokeColorRGB(0.2, 0.8, 0.8)  # 青色
                    c.setLineWidth(self.border_width)
                    c.rect(x, y, self.card_width, self.card_height)  # 使用直角矩形

                    # 计算内部区域
                    inner_margin = 8 * mm
                    bar_width = 5 * mm

                    inner_width = self.card_width - 2 * inner_margin
                    inner_height = self.card_height - 2 * inner_margin

                    # 绘制紫色装饰条
                    bar_height = inner_height * 0.3
                    bar_y = y + inner_margin + (inner_height - bar_height) / 2

                    # 设置紫色填充色
                    c.setFillColorRGB(0.8, 0.2, 0.8)

                    # 左侧装饰条 - 无边框
                    c.rect(x, bar_y, bar_width, bar_height, fill=1, stroke=0)

                    # 右侧装饰条 - 无边框
                    c.rect(
                        x + self.card_width - bar_width,
                        bar_y,
                        bar_width,
                        bar_height,
                        fill=1,
                        stroke=0,
                    )

                    # 文字处理
                    text = texts[current_card]
                    c.setFillColorRGB(0, 0, 0)  # 黑色文字

                    # 计算文字可用空间
                    text_max_width = self.card_width - inner_margin
                    text_max_height = self.card_height

                    # 计算合适的字体大小并创建段落对象
                    font_size, paragraphs = self._calculate_font_size(
                        text, text_max_width, text_max_height
                    )

                    # 计算总高度
                    total_height = sum(
                        p.wrap(text_max_width, text_max_height)[1] for p in paragraphs
                    )

                    # 计算起始位置（从顶部开始）
                    text_x = x + (self.card_width - text_max_width) / 2
                    text_y = y + self.card_height - inner_margin / 4

                    # 绘制文字
                    c.saveState()
                    for p in paragraphs:
                        w, h = p.wrap(text_max_width, text_max_height)
                        p.drawOn(c, text_x, text_y - h)
                        text_y -= h  # 更新下一段文字的位置
                    c.restoreState()

                    current_card += 1

                if current_card >= total_cards:
                    break

            # 如果还有更多卡片要绘制，创建新页面
            if current_card < total_cards:
                c.showPage()

        c.save()

    def create_bilingual_cards(
        self,
        output_file,
        chinese_texts,
        english_texts,
        logo_path,
        logo2_path,
        main_logo_size=50 * mm,
        corner_logo_size=20 * mm,
    ):
        """生成中英文对照的卡片并按照正面-背面交替顺序合成PDF"""
        # 生成临时文件名
        temp_dir = os.path.dirname(output_file) or "."
        temp_fronts = os.path.join(temp_dir, "temp_fronts.pdf")
        temp_backs = os.path.join(temp_dir, "temp_backs.pdf")

        # 准备中英文组合的文本
        bilingual_texts = [
            f"{ch}\n{en}" for ch, en in zip(chinese_texts, english_texts)
        ]

        total_cards = len(bilingual_texts)

        # 生成卡片正面
        self.create_card_fronts(temp_fronts, bilingual_texts)

        # 生成卡片背面
        self.create_card_backs(
            temp_backs,
            logo_path,
            logo2_path,
            main_logo_size,
            corner_logo_size,
            total_cards=total_cards,  # 传递总卡片数量
        )

        # 使用PyPDF2合并PDF，按照正面-背面交替顺序
        merger = PdfMerger()

        # 打开临时PDF文件
        with open(temp_fronts, "rb") as fronts_file, open(
            temp_backs, "rb"
        ) as backs_file:
            fronts = PdfReader(fronts_file)
            backs = PdfReader(backs_file)

            # 计算总页数
            total_pages = len(fronts.pages)

            # 逐页添加正面和背面
            for page_num in range(total_pages):
                # 添加一页正面
                merger.append(pages=(page_num, page_num + 1), fileobj=fronts_file)
                # 添加对应的背面
                merger.append(pages=(page_num, page_num + 1), fileobj=backs_file)

            # 保存最终的PDF
            with open(output_file, "wb") as output:
                merger.write(output)

        # 清理临时文件
        try:
            os.remove(temp_fronts)
            os.remove(temp_backs)
        except:
            pass  # 忽略删除临时文件时的错误
