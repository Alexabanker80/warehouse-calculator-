import os
import base64
import glob
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("scripts/competitor-monitor/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = "company/06-marketing/monitoring-data/screenshots"

def get_name_from_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = """
    Посмотри на этот скриншот Яндекс.Карт.
    Напиши ТОЧНОЕ название организации из заголовка карточки.
    Верни только название, ничего лишнего.
    Если названия не видно, напиши "Unknown".
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
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    if not os.path.exists(DATA_DIR): return
    dates = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    latest_date = dates[-1]
    
    # Сначала ищем по reviews
    # Если Unknown, ищем по mobile.png
    
    all_files = glob.glob(f"{DATA_DIR}/{latest_date}/*.png")
    # Группируем файлы по ключу конкурента
    groups = {}
    for f in all_files:
        name = os.path.basename(f)
        key = None
        if "_reviews.png" in name: key = name.replace('_reviews.png', '')
        elif "_mobile.png" in name: key = name.replace('_mobile.png', '')
        
        if key:
            if key not in groups: groups[key] = []
            groups[key].append(f)
    
    mapping = {}
    
    for key in sorted(groups.keys()):
        files = groups[key]
        real_name = "Unknown"
        
        # Приоритет: mobile.png (там шапка), потом reviews
        target_file = None
        for f in files: 
            if "_mobile.png" in f: target_file = f
        
        if not target_file and files: target_file = files[0]
        
        if target_file:
            real_name = get_name_from_image(target_file)
            
        print(f"[{key}] -> {real_name}")
        mapping[key] = real_name
        
    # Выводим итоговый список для замены
    print("\n--- COPY THIS TO UPDATE LIST ---")
    for k, v in mapping.items():
        print(f"{k}|{v}")

if __name__ == "__main__":
    main()
