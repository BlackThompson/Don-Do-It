# 不要做挑战卡片生成器 Don't Do It Card Generator 🎴

一个用于生成双面打印卡片的 Python 工具，支持中英文对照显示。
A Python tool for generating double-sided cards with bilingual (Chinese-English) support.

## ✨ 功能特点 Features

- 🌐 支持中英文对照显示 Bilingual display support
- 📝 自动调整字体大小以适应卡片 Auto font size adjustment
- 🔤 支持粗体字体 Bold font support
- 📋 智能的英文文本换行 Smart English text wrapping
- 🎨 支持自定义 Logo 和装饰元素 Customizable logos and decorative elements
- ✂️ 自动生成切割线和出血标记 Automatic cutting lines and bleed marks
- 📄 优化的双面打印布局 Optimized double-sided printing layout
- 📦 支持批量生成多张卡片 Batch card generation support

## 📋 安装要求 Requirements

- 🐍 Python 3.6+
- 📦 依赖包 Dependencies:
  - reportlab
  - Pillow
  - PyPDF2

## 🚀 安装步骤 Installation

1. 克隆仓库 Clone repository:
```bash
git clone [repository-url]
cd card-generator
```

2. 安装依赖 Install dependencies:
```bash
pip install -r requirements.txt
```

## 💡 使用方法 Usage

1. 准备必要的文件 Prepare required files:
   - `Echo_Logo.png`: 用于卡片角落的 Logo (Corner logo)
   - `Echo_Logo_2.png`: 用于卡片中心的 Logo (Center logo)
   - 中英文对照文本列表 (Bilingual text list)

2. 运行程序 Run the program:
```bash
python main.py
```

3. 输出文件 Output:
   - 生成 `bilingual_cards.pdf` 文件 (Generates `bilingual_cards.pdf`)
   - PDF 文件中的页面按照正面-背面交替排列 (Pages alternate between front and back)

## ⚙️ 自定义配置 Customization

### 🎨 字体设置 Font Settings
默认使用微软雅黑字体 (Default: Microsoft YaHei):
- 普通字体 Regular: `C:/Windows/Fonts/msyh.ttc`
- 粗体字体 Bold: `C:/Windows/Fonts/msyhbd.ttc`

### 📐 卡片布局 Card Layout
- 默认每页 3x3 布局 (Default: 3x3 layout per page)
- 支持自定义行数和列数 (Customizable rows and columns)

### 🖼️ Logo 设置 Logo Settings
- 中心 Logo 大小 Center logo size: 默认 50mm (Default: 50mm)
- 角落 Logo 大小 Corner logo size: 默认 20mm (Default: 20mm)

## 🖨️ 打印说明 Printing Instructions

1. 使用双面打印机 Use double-sided printer
2. 选择"翻转长边"或"翻转短边" Select "Flip on long edge" or "Flip on short edge"
3. 确保纸张方向正确 Ensure correct paper orientation (A4)
4. 建议使用较厚的纸张 Recommended paper weight: 200g+

## ⚠️ 注意事项 Notes

- 确保所有图片文件存在且格式正确 Ensure all image files exist and are in correct format
- 中英文文本长度会影响字体大小自动调整 Text length affects automatic font size adjustment
- 建议在打印前先打印测试页确认效果 Test print recommended before batch printing

## 📁 文件结构 File Structure

```
card_generator/
├── src/
│   ├── __init__.py
│   ├── card_generator.py
│   ├── card_styles.py
│   └── wordlist.py
├── main.py
├── requirements.txt
└── README.md
```


---

Made with ❤️ by Black