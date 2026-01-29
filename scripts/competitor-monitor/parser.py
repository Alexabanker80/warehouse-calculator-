import os
import json
import glob
from bs4 import BeautifulSoup
from datetime import datetime

# Конфигурация
DATA_DIR = "company/06-marketing/monitoring-data"

def parse_yandex_maps(html_content):
    """Извлекает данные из карточки Яндекс.Карт."""
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {
        "rating": None,
        "reviews_count": None,
        "last_reviews": [],
        "prices": []
    }
    
    # 1. Рейтинг и количество отзывов
    # Классы Яндекса часто меняются (обфусцированы), поэтому ищем по смыслу или aria-label
    # Это эвристический поиск
    
    # Поиск рейтинга (обычно это число 4.x в крупном блоке)
    # Попробуем найти блок с рейтингом по тексту
    rating_elem = soup.find('span', class_=lambda x: x and 'business-rating-badge-view__rating-text' in x)
    if rating_elem:
        data["rating"] = rating_elem.get_text(strip=True)
        
    reviews_count_elem = soup.find('div', class_=lambda x: x and 'business-header-rating-view__text' in x)
    if reviews_count_elem:
        data["reviews_count"] = reviews_count_elem.get_text(strip=True)

    # 2. Отзывы
    # Ищем контейнеры отзывов
    reviews = soup.find_all('div', class_=lambda x: x and 'business-review-view__info' in x)
    for review in reviews[:5]: # Берем первые 5
        text_elem = review.find('span', class_=lambda x: x and 'business-review-view__body-text' in x)
        date_elem = review.find('span', class_=lambda x: x and 'business-review-view__date' in x)
        stars_elem = review.find('div', class_=lambda x: x and 'business-rating-badge-view__stars' in x) # Сложно вытащить кол-во звезд из CSS, но попробуем
        
        if text_elem:
            data["last_reviews"].append({
                "text": text_elem.get_text(strip=True),
                "date": date_elem.get_text(strip=True) if date_elem else "Неизвестно"
            })
            
    # 3. Цены (раздел Товары и услуги)
    # Это сложнее, так как они в другой вкладке, но иногда они есть в сниппете
    # Пока пропустим глубокий парсинг цен с Яндекса, так как мы не кликали на вкладку "Цены"
    
    return data

def parse_website(html_content):
    """Извлекает основной текст и цены с сайта."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Удаляем мусор
    for script in soup(["script", "style", "nav", "footer"]):
        script.extract()
        
    # Получаем текст
    text = soup.get_text(separator=' ', strip=True)
    
    # Пробуем найти таблицы (часто цены там)
    tables = []
    for table in soup.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            cols = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if cols:
                rows.append(cols)
        if rows:
            tables.append(rows)
            
    return {
        "text_preview": text[:2000], # Первые 2000 символов для анализа
        "tables": tables
    }

def main():
    print("=== Запуск парсинга данных ===")
    
    # Ищем внутри raw_html
    raw_root = os.path.join(DATA_DIR, "raw_html")
    if not os.path.exists(raw_root):
        print(f"Папка {raw_root} не найдена")
        return

    dates = sorted([d for d in os.listdir(raw_root) if os.path.isdir(os.path.join(raw_root, d))])
    if not dates:
        print("Нет данных для обработки")
        return
        
    latest_date = dates[-1]
    print(f"Обрабатываем дату: {latest_date}")
    
    raw_files = glob.glob(f"{raw_root}/{latest_date}/*.html")
    results = {}
    
    for file_path in raw_files:
        filename = os.path.basename(file_path)
        name = filename.replace('.html', '')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "_yandex" in name:
            parsed = parse_yandex_maps(content)
            key = name.replace('_yandex', '')
            if key not in results: results[key] = {}
            results[key]['yandex'] = parsed
        else:
            parsed = parse_website(content)
            key = name.replace('_website', '')
            if key not in results: results[key] = {}
            results[key]['website'] = parsed
            
    # Сохраняем результат
    # Создаем папку если нет
    output_dir = f"{DATA_DIR}/processed/{latest_date}"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Обработка завершена. Результат: {output_file}")
    
    # Вывод краткой статистики
    for name, data in results.items():
        print(f"\n--- {name} ---")
        if 'yandex' in data:
            y = data['yandex']
            print(f"Yandex: Рейтинг {y.get('rating')}, Отзывов {y.get('reviews_count')}")
            if y.get('last_reviews'):
                print(f"  Последний отзыв: {y['last_reviews'][0]['text'][:50]}...")
        if 'website' in data:
            print(f"Сайт: Найдено таблиц с ценами: {len(data['website']['tables'])}")

if __name__ == "__main__":
    main()
