import os
import base64
import glob
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("scripts/competitor-monitor/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = "company/06-marketing/monitoring-data/screenshots"

def analyze_any_prices(image_path):
    print(f"Анализируем скриншот: {os.path.basename(image_path)}")
    
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = """
    Посмотри на этот скриншот (это вкладка 'Товары и услуги' или прайс-лист шиномонтажа).
    Перечисли списком ВСЕ услуги и цены, которые ты видишь.
    Пиши в формате: "Услуга - Цена".
    Если цен нет, так и напиши: "Цен не обнаружено".
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
            max_tokens=500,
        )
        print("\n--- Ответ GPT ---")
        print(response.choices[0].message.content)
        print("-----------------")
    except Exception as e:
        print(f"Ошибка: {e}")

def main():
    # Ищем скриншоты за последнюю дату
    if not os.path.exists(DATA_DIR): return
    dates = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    latest_date = dates[-1]
    
    # Берем конкретного конкурента №1 (Mobile)
    target = glob.glob(f"{DATA_DIR}/{latest_date}/1._*_mobile.png")
    
    if target:
        analyze_any_prices(target[0])
    else:
        print("Скриншот не найден.")

if __name__ == "__main__":
    main()
