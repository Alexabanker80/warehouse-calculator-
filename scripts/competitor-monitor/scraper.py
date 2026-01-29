import os
import re
import random
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

COMPETITORS_FILE = "company/06-marketing/competitors-list.md"
OUTPUT_DIR = "company/06-marketing/monitoring-data"
SCREENSHOT_DIR = f"{OUTPUT_DIR}/screenshots"

async def read_competitors_list():
    links = []
    if not os.path.exists(COMPETITORS_FILE): return []
    with open(COMPETITORS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    current_competitor = "Unknown"
    for line in lines:
        line = line.strip()
        if line.startswith('## '): current_competitor = line.replace('## ', '').strip()
        elif line.startswith('### '): current_competitor = line.replace('### ', '').strip()
        if 'http' in line:
            url_match = re.search(r'(https?://[^\s\)]+)', line)
            if url_match:
                url = url_match.group(1)
                source_type = "yandex" if "yandex.ru/maps" in url else "website"
                links.append({"name": current_competitor, "url": url, "type": source_type})
    return links

async def scrape_url(context, link_data, date_str):
    page = await context.new_page()
    url = link_data['url']
    name = link_data['name'].replace(' ', '_').replace('/', '-')
    source_type = link_data['type']
    
    # Нам нужны только Яндекс.Карты для отзывов
    if source_type != "yandex":
        await page.close()
        return False
    
    print(f"Поиск отзывов: {name}")
    
    try:
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 4000))
        
        # Логика для мобильных Яндекс.Карт
        # Ищем вкладку "Отзывы"
        clicked = False
        try:
            # Пробуем разные селекторы
            # 1. Точное совпадение
            await page.get_by_text("Отзывы", exact=True).first.click(timeout=3000)
            clicked = True
        except:
            try:
                # 2. Поиск по части слова (иногда там "254 Отзыва")
                await page.locator("div", has_text=re.compile(r"Отзыв")).last.click(timeout=3000)
                clicked = True
            except:
                pass
        
        if clicked:
            print("  -> Вкладка 'Отзывы' нажата")
            await page.wait_for_timeout(2000)
        else:
            print("  -> Вкладка не нажата, скроллим главную...")

        # Скроллим вниз, чтобы прочитать побольше отзывов
        for _ in range(5):
            await page.mouse.wheel(0, 800)
            await page.wait_for_timeout(1000)
        
        # Делаем скриншот отзывов
        path = f"{SCREENSHOT_DIR}/{date_str}/{name}_reviews.png"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        await page.screenshot(path=path, full_page=True)
        
        return True
    except Exception as e:
        print(f"  - Ошибка: {str(e)}")
        return False
    finally:
        await page.close()

async def main():
    print("=== Запуск Охотника за Отзывами ===")
    date_str = datetime.now().strftime("%Y-%m-%d")
    links = await read_competitors_list()
    if not links: return
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        iphone = p.devices['iPhone 14 Pro']
        context = await browser.new_context(
            **iphone,
            locale='ru-RU',
            timezone_id='Europe/Moscow'
        )
        for link in links:
            await scrape_url(context, link, date_str)
        await browser.close()
    print(f"=== Готово. Скриншоты: {SCREENSHOT_DIR}/{date_str} ===")

if __name__ == "__main__":
    asyncio.run(main())
