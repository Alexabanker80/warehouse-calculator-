import os
import base64
import glob
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("scripts/competitor-monitor/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = "company/06-marketing/monitoring-data/screenshots"

def analyze_prices_for_all(image_path, competitor_name):
    print(f"\n🔍 Анализ: {competitor_name}")
    
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = """
    Ты смотришь на экран телефона с открытой страницей Шиномонтажа (вкладка Цены/Товары).
    
    Твоя задача: Найти и выписать цены на услуги.
    Формат ответа:
    1. Услуга: Цена
    2. Услуга: Цена
    
    Если видишь много цен, выбери 5-7 самых важных (Переобувка R16, R18, Хранение, Ремонт).
    Если цен НЕТ (только отзывы или фото), напиши: "Цены не найдены".
    """

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
            max_tokens=400,
        )
        print(f"📄 Отчет по ценам:\n{response.choices[0].message.content}")
    except Exception as e:
        print(f"Ошибка: {e}")

def main():
    if not os.path.exists(DATA_DIR): return
    dates = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    latest_date = dates[-1]
    
    # Ищем все мобильные скриншоты (где мы искали цены)
    screenshots = glob.glob(f"{DATA_DIR}/{latest_date}/*_mobile_*.png")
    
    if not screenshots:
        print("Скриншоты не найдены. Сначала запустите scraper.py")
        return

    print(f"Найдено {len(screenshots)} скриншотов. Начинаем анализ...")
    
    for shot in sorted(screenshots):
        name = os.path.basename(shot).replace('_mobile_prices.png', '').replace('_mobile_site.png', '')
        analyze_prices_for_all(shot, name)

if __name__ == "__main__":
    main()
