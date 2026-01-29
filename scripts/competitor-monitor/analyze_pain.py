import os
import base64
import glob
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("scripts/competitor-monitor/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = "company/06-marketing/monitoring-data/screenshots"
REPORT_FILE = "company/06-marketing/reports/pain_report_2026-01-29.md"

def analyze_pain(image_path, competitor_name):
    print(f"Анализ болей: {competitor_name}")
    
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = """
    Проанализируй эти отзывы о шиномонтаже.
    Твоя задача - выявить СЛАБЫЕ МЕСТА и БОЛИ клиентов.
    
    Напиши кратко:
    1. На что жалуются чаще всего? (очереди, цена, грубость, сломали что-то)
    2. Если есть вопиющий случай (скандал) - упомяни его.
    3. Если жалоб нет и все хвалят - так и напиши: "Сильные стороны: ..."
    
    Не пересказывай отзывы, дай аналитический вывод.
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
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка анализа: {e}"

def main():
    if not os.path.exists(DATA_DIR): return
    dates = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
    latest_date = dates[-1]
    
    screenshots = glob.glob(f"{DATA_DIR}/{latest_date}/*_reviews.png")
    
    report_lines = []
    report_lines.append(f"# 😡 Карта болей конкурентов ({latest_date})")
    report_lines.append("> Анализ негативных отзывов и слабых мест")
    report_lines.append("")
    
    for shot in sorted(screenshots):
        name = os.path.basename(shot).replace('_reviews.png', '')
        clean_name = name.replace('_', ' ')
        
        analysis = analyze_pain(shot, name)
        
        report_lines.append(f"## {clean_name}")
        report_lines.append(analysis)
        report_lines.append(f"🔗 [Скриншот отзывов](../monitoring-data/screenshots/{latest_date}/{os.path.basename(shot)})")
        report_lines.append("---")
        
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    print(f"\nГотово! Отчет сохранен: {REPORT_FILE}")

if __name__ == "__main__":
    main()
