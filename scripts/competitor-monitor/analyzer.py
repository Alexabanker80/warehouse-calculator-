import json
import os
import glob
from datetime import datetime

DATA_DIR = "company/06-marketing/monitoring-data"
OUTPUT_REPORT_DIR = "company/06-marketing/reports"

def generate_price_report():
    print("=== Генерация Ценового Отчета ===")
    
    processed_dir = f"{DATA_DIR}/processed"
    if not os.path.exists(processed_dir): return
    dates = sorted(os.listdir(processed_dir))
    if not dates: return
    latest_date = dates[-1]
    data_file = f"{processed_dir}/{latest_date}/data.json"
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    lines = []
    lines.append(f"# 💰 Мониторинг цен конкурентов: {latest_date}")
    lines.append("> Цены извлечены автоматически (OCR) со скриншотов. Возможны неточности.")
    lines.append("")
    
    # ТАБЛИЦА ЦЕН
    lines.append("## Сравнение ключевых позиций")
    lines.append("| Конкурент | R16 (Комплекс) | R18 (Комплекс) | Хранение (Сезон) |")
    lines.append("| :--- | :---: | :---: | :---: |")
    
    for name, info in data.items():
        clean_name = name.replace('_', ' ')
        
        # Пытаемся найти цены (приоритет GPT, потом OCR)
        prices = info.get("gpt_prices") or info.get("ocr_prices", {})
        
        p_r16 = prices.get("R16")
        p_r18 = prices.get("R18")
        p_storage = prices.get("Storage")
        
        # Форматирование (None -> —)
        def fmt(val):
            if val is None or val == "null" or val == "": return "—"
            return f"**{val}**"
            
        p_r16 = fmt(p_r16)
        p_r18 = fmt(p_r18)
        p_storage = fmt(p_storage)
        
        lines.append(f"| {clean_name} | {p_r16} | {p_r18} | {p_storage} |")
        
    lines.append("")
    lines.append("---")
    
    # ДЕТАЛИЗАЦИЯ
    lines.append("## Источники данных")
    shot_dir = f"../monitoring-data/screenshots/{latest_date}"
    
    for name, info in data.items():
        ocr = info.get("ocr_prices", {})
        if ocr:
            lines.append(f"### {name.replace('_', ' ')}")
            lines.append(f"Робот распознал: {ocr}")
            lines.append(f"🔗 [Проверить на скриншоте]({shot_dir}/{name}_long.png)")
            lines.append("")

    # Сохранение
    output_file = f"{OUTPUT_REPORT_DIR}/price_report_{latest_date}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
        
    print(f"Ценовой отчет готов: {output_file}")

if __name__ == "__main__":
    generate_price_report()
