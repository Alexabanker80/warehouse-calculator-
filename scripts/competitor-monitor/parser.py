import os
import json
import glob
import re
from bs4 import BeautifulSoup
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    pytesseract = None

# Конфигурация
DATA_DIR = "company/06-marketing/monitoring-data"

def preprocess_image(img):
    """Подготовка изображения для лучшего OCR."""
    # 1. В оттенки серого
    img = img.convert('L')
    
    # 2. Увеличиваем контрастность
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    
    # 3. Бинаризация (черно-белое)
    # Это помогает убрать серый фон Яндекса
    thresh = 200
    fn = lambda x: 255 if x > thresh else 0
    img = img.point(fn, mode='1')
    
    return img

def extract_prices_from_image(image_path):
    """Умный поиск цен с предобработкой."""
    if not pytesseract: return {}
    
    try:
        original_img = Image.open(image_path)
        
        # Делаем предобработку
        processed_img = preprocess_image(original_img)
        
        # Распознаем текст с настройкой --psm 6 (предполагаем блок текста)
        # rus+eng - чтобы читать и "R16" и "Цена"
        text = pytesseract.image_to_string(processed_img, lang='rus+eng', config='--psm 6')
        
        found_prices = {}
        
        # Разбиваем на строки и анализируем каждую
        lines = text.split('\n')
        for line in lines:
            line_clean = line.lower().strip()
            if not line_clean: continue
            
            # Ищем цену в строке (число от 1000 до 99000)
            # Часто цена бывает в конце строки: "Шиномонтаж R16 ... 3000"
            price_match = re.findall(r'\b(\d{3,5})\b', line)
            
            if not price_match: continue
            
            # Берем последнее число в строке как наиболее вероятную цену
            price = price_match[-1]
            
            # Логика определения услуги
            if '16' in line_clean and ('r16' in line_clean or 'радиус' in line_clean or 'комплекс' in line_clean):
                # Избегаем записи самого радиуса "16" как цены
                if price != '16': 
                    found_prices['R16'] = price
                    
            elif '18' in line_clean and ('r18' in line_clean or 'радиус' in line_clean or 'комплекс' in line_clean):
                 if price != '18':
                    found_prices['R18'] = price
                    
            elif 'хранен' in line_clean or 'сезон' in line_clean:
                found_prices['Storage'] = price

        return found_prices
        
    except Exception as e:
        print(f"Ошибка OCR {image_path}: {e}")
        return {}

def parse_yandex_maps(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return {}

def parse_website(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "footer"]): script.extract()
    text = soup.get_text(separator=' ', strip=True)
    tables = []
    for table in soup.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            cols = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if cols: rows.append(cols)
        if rows: tables.append(rows)
    return {"text_preview": text[:2000], "tables": tables}

def main():
    print("=== Запуск OCR v2 (Улучшенный) ===")
    
    processed_dir = f"{DATA_DIR}/processed"
    raw_root = f"{DATA_DIR}/raw_html"
    screenshot_root = f"{DATA_DIR}/screenshots"

    if not os.path.exists(raw_root): return
    dates = sorted([d for d in os.listdir(raw_root) if os.path.isdir(os.path.join(raw_root, d))])
    if not dates: return
    latest_date = dates[-1]
    
    results = {}
    
    # Скриншоты
    screenshot_files = glob.glob(f"{screenshot_root}/{latest_date}/*.png")
    print(f"Обрабатываем {len(screenshot_files)} изображений с фильтрами...")
    
    for shot_path in screenshot_files:
        filename = os.path.basename(shot_path)
        
        # Определяем ключ
        key = None
        if "_long" in filename: key = filename.replace('_long.png', '')
        elif "_3_prices" in filename: key = filename.replace('_3_prices.png', '')
        
        if not key: continue
            
        prices = extract_prices_from_image(shot_path)
        if prices:
            if key not in results: results[key] = {}
            if 'ocr_prices' not in results[key]: results[key]['ocr_prices'] = {}
            results[key]['ocr_prices'].update(prices)
            print(f"  + {key}: {prices}")

    # Сохраняем (дополняем существующий JSON если есть, или создаем новый)
    output_dir = f"{processed_dir}/{latest_date}"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/data.json"
    
    # Читаем старый json чтобы не потерять данные с сайтов
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            # Мержим
            for k, v in results.items():
                if k not in old_data: old_data[k] = {}
                old_data[k].update(v)
            results = old_data
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Готово: {output_file}")

if __name__ == "__main__":
    main()
