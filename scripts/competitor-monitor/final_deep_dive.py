import os
import base64
import glob
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("scripts/competitor-monitor/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = "company/06-marketing/monitoring-data/screenshots"
REPORT_FILE = "company/06-marketing/reports/final_deep_dive_2026-01-29.md"

COMPETITORS = {
    "1._Шиномонтаж_(на_Вашутинском)": "1. Шиномонтаж (на Вашутинском)",
    "2._Конкурент_(Проверить_название_по_ссылке)": "2. Конкурент (Неизвестно)",
    "3._Конкурент_(Проверить_название_по_ссылке)": "3. Колпак",
    "4._Конкурент_(Проверить_название_по_ссылке)": "4. SoFyKaR",
    "5._Конкурент_(Проверить_название_по_ссылке)": "5. АвтоLife",
    "6._Конкурент_(Проверить_название_по_ссылке)": "6. Шик Блеск Авто",
    "7._Shin-Pro": "7. Shin-Pro",
    "Филиал:_Химки": "0. Наш Филиал (Химки)"
}

def analyze_image(image_path, prompt):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ],
                }
            ],
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка: {e}"

def main():
    if not os.path.exists(DATA_DIR): return
    dates = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    latest_date = dates[-1]
    
    print(f"=== Формирование Финального Досье за {latest_date} ===")
    
    report_content = []
    report_content.append(f"# 📂 Финальное досье конкурентов ({latest_date})")
    report_content.append("")
    
    # Сортируем ключи, чтобы идти по порядку 1..7
    sorted_keys = sorted(COMPETITORS.keys())
    
    for key in sorted_keys:
        human_name = COMPETITORS[key]
        print(f"Обработка: {human_name}...")
        
        report_content.append(f"## {human_name}")
        
        # 1. ОТЗЫВЫ (Ищем _reviews.png)
        reviews_shot = f"{DATA_DIR}/{latest_date}/{key}_reviews.png"
        reviews_text = "Скриншот отзывов не найден."
        
        if os.path.exists(reviews_shot):
            prompt = """
            Выпиши до 5 самых свежих НЕГАТИВНЫХ отзывов (1-3 звезды) с датами.
            Формат:
            - Дата: Текст (кратко)
            
            Если негативных нет, выпиши 3 последних любых.
            """
            reviews_text = analyze_image(reviews_shot, prompt)
        
        report_content.append("### 🤬 Отзывы (Негатив/Последние)")
        report_content.append(reviews_text)
        report_content.append("")
        
        # 2. ЦЕНЫ (Ищем _mobile_prices.png, если нет - _long.png)
        prices_shot = f"{DATA_DIR}/{latest_date}/{key}_mobile_prices.png"
        if not os.path.exists(prices_shot):
             prices_shot = f"{DATA_DIR}/{latest_date}/{key}_long.png"
             
        prices_text = "Скриншот цен не найден."
        
        if os.path.exists(prices_shot):
            prompt = """
            Выпиши ВСЕ услуги и цены, которые видишь на картинке.
            Формат:
            - Услуга: Цена
            
            Если цен нет (заглушка, капча, просто фото), напиши: "Цены скрыты/не найдены".
            """
            prices_text = analyze_image(prices_shot, prompt)
            
        report_content.append("### 💰 Товары и услуги")
        report_content.append(prices_text)
        report_content.append("---")
        report_content.append("")

    # Сохраняем
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_content))
        
    print(f"Досье готово: {REPORT_FILE}")

if __name__ == "__main__":
    main()
