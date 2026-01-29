import os
import json
import base64
import glob
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем ключ из .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = "company/06-marketing/monitoring-data"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_screenshot_with_gpt(image_path, competitor_name):
    print(f"  > Отправляем в GPT: {competitor_name} ({os.path.basename(image_path)})")
    
    base64_image = encode_image(image_path)
    
    prompt = """
    Ты - аналитик данных. Твоя задача - найти цены на услуги шиномонтажа на этом скриншоте.
    
    Меня интересуют ТОЛЬКО три позиции:
    1. Комплексная переобувка (шиномонтаж) 4 колес радиуса R16 (Легковые).
    2. Комплексная переобувка (шиномонтаж) 4 колес радиуса R18 (Легковые/Кроссоверы).
    3. Сезонное хранение шин/колес (цена за комплект на сезон/полгода).
    
    Если точной цены нет, но есть диапазон (2000-3000), пиши среднее.
    Если услуги нет на картинке, пиши null.
    
    Верни ответ строго в формате JSON, без лишних слов:
    {
        "R16": 1234,
        "R18": 5678,
        "Storage": 900
    }
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Актуальная модель
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        
        content = response.choices[0].message.content
        # Очищаем от md-тегов если есть
        content = content.replace('```json', '').replace('```', '').strip()
        
        return json.loads(content)
        
    except Exception as e:
        print(f"  ! Ошибка GPT: {e}")
        return None

def main():
    print("=== Запуск GPT-4 Vision Analysis ===")
    
    processed_dir = f"{DATA_DIR}/processed"
    screenshot_root = f"{DATA_DIR}/screenshots"

    # Берем последнюю дату
    if not os.path.exists(screenshot_root): return
    dates = sorted([d for d in os.listdir(screenshot_root) if os.path.isdir(os.path.join(screenshot_root, d))])
    if not dates: return
    latest_date = dates[-1]
    
    print(f"Дата анализа: {latest_date}")
    
    # Загружаем текущие данные
    data_file = f"{processed_dir}/{latest_date}/data.json"
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
    else:
        full_data = {}

    # Ищем все скриншоты
    screenshots = glob.glob(f"{screenshot_root}/{latest_date}/*.png")
    
    # Собираем уникальные имена конкурентов
    competitors = set()
    for s in screenshots:
        name = os.path.basename(s).split('_long.png')[0].split('_3_prices.png')[0].split('_site.png')[0]
        # Отсекаем суффиксы более аккуратно
        if "_long" in os.path.basename(s): competitors.add(os.path.basename(s).replace('_long.png', ''))
        
    for name in competitors:
        # Приоритет: 1. long (там больше всего инфы), 2. prices
        long_shot = f"{screenshot_root}/{latest_date}/{name}_long.png"
        price_shot = f"{screenshot_root}/{latest_date}/{name}_3_prices.png"
        
        target_shot = None
        if os.path.exists(long_shot): target_shot = long_shot
        elif os.path.exists(price_shot): target_shot = price_shot
        
        if not target_shot: continue
        
        result = analyze_screenshot_with_gpt(target_shot, name)
        
        if result:
            print(f"  + Результат {name}: {result}")
            if name not in full_data: full_data[name] = {}
            
            # Сохраняем как 'gpt_prices'
            full_data[name]['gpt_prices'] = result

    # Сохраняем обновленный JSON
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)
        
    print(f"Готово! Данные сохранены в {data_file}")

if __name__ == "__main__":
    main()
