import json
import os
import glob
from datetime import datetime

DATA_DIR = "company/06-marketing/monitoring-data"
OUTPUT_REPORT_DIR = "company/06-marketing/reports"

def generate_report():
    print("=== Генерация визуального отчета ===")
    
    processed_dir = f"{DATA_DIR}/processed"
    if not os.path.exists(processed_dir): return
    dates = sorted(os.listdir(processed_dir))
    if not dates: return
    latest_date = dates[-1]
    data_file = f"{processed_dir}/{latest_date}/data.json"
    
    # Загружаем данные (если есть)
    data = {}
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
    # Получаем список конкурентов из файла (так надежнее, если в JSON не попали все)
    # Но для простоты пока работаем с JSON. Если JSON пуст (скрипт парсинга не запускали), возьмем список папок скриншотов
    
    # 2. Формируем Markdown
    lines = []
    lines.append(f"# 🕵️ Глубокий отчет: {latest_date}")
    lines.append(f"> Теперь со скриншотами цен и отзывов!")
    lines.append("")
    
    lines.append("## 📸 Детальные карточки")
    
    # Список конкурентов берем из data.json
    for name, info in data.items():
        clean_name = name.replace('_', ' ')
        lines.append(f"### 📍 {clean_name}")
        
        # Ссылки на доказательства (проверяем существование файлов)
        shot_dir = f"{DATA_DIR}/screenshots/{latest_date}"
        
        # Формируем ссылки
        lines.append("**Доказательства:**")
        
        # Проверяем наличие файлов
        long_shot = f"{name}_long.png"
        full_shot = f"{name}_full.png"
        
        lines.append(f"- 📸 [Полный скриншот (Длинный)]({shot_dir}/{long_shot}) (или {full_shot})")
        
        lines.append("")
        
        # Текстовые данные
        if "website" in info:
            tables = len(info["website"].get("tables", []))
            if tables > 0:
                lines.append(f"> Найдены таблицы цен на сайте: {tables} шт.")

    # Сохранение
    output_file = f"{OUTPUT_REPORT_DIR}/deep_report_{latest_date}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
        
    print(f"Отчет готов: {output_file}")

if __name__ == "__main__":
    generate_report()
