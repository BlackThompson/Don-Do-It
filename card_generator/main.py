from src.card_generator import CardGenerator
from src.wordlist import actions_list, actions_list_english

# from PyPDF2.generic import mm


def main():
    # 创建卡片生成器实例
    generator = CardGenerator(rows=3, cols=3)

    # 生成中英文对照的卡片
    generator.create_bilingual_cards(
        output_file="bilingual_cards.pdf",
        chinese_texts=actions_list,
        english_texts=actions_list_english,
        logo_path="Echo_Logo.png",  # 角落Logo
        logo2_path="Echo_Logo_2.png",  # 中心Logo
        main_logo_size=200,
        corner_logo_size=60,
    )


if __name__ == "__main__":
    main()
