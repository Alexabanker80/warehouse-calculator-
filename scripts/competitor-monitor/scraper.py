import os
import re
import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

COMPETITORS_FILE = "company/06-marketing/competitors-list.md"
OUTPUT_DIR = "company/06-marketing/monitoring-data"
SCREENSHOT_DIR = f"{OUTPUT_DIR}/screenshots"
RAW_DATA_DIR = f"{OUTPUT_DIR}/raw_html"

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
    
    print(f"Обработка: {name} ({source_type})")
    
    try:
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000) # Ждем прогрузки
        
        # Делаем ДЛИННЫЙ скриншот
        # Для этого нужно прокрутить страницу
        # В Яндексе скролл работает хитро, нужно крутить конкретный контейнер
        # Но мы попробуем общий скролл + увеличение вьюпорта
        
        if source_type == "yandex":
            # Имитация скролла пользователя
            for _ in range(5):
                await page.mouse.wheel(0, 500)
                await page.wait_for_timeout(500)
            
            # Делаем высокий скриншот
            # Увеличиваем высоту окна браузера виртуально, чтобы влезло больше
            await page.set_viewport_size({"width": 1280, "height": 2500})
            await page.wait_for_timeout(1000)
            
            path = f"{SCREENSHOT_DIR}/{date_str}/{name}_long.png"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            await page.screenshot(path=path, full_page=False) # full_page в Яндексе может сломаться из-за карт, лучше фиксированная высота
            
        else:
            # Обычный сайт - full page
            path = f"{SCREENSHOT_DIR}/{date_str}/{name}_full.png"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                await page.screenshot(path=path, full_page=True)
            except:
                # Если страница бесконечная, делаем обычный
                await page.screenshot(path=path, full_page=False)
                
            # HTML
            content = await page.content()
            html_path = f"{RAW_DATA_DIR}/{date_str}/{name}_site.html"
            os.makedirs(os.path.dirname(html_path), exist_ok=True)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return True
    except Exception as e:
        print(f"  - Ошибка {name}: {str(e)}")
        return False
    finally:
        await page.close()

async def main():
    print("=== Запуск Long-Screenshot мониторинга ===")
    date_str = datetime.now().strftime("%Y-%m-%d")
    links = await read_competitors_list()
    if not links: return
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        for link in links:
            await scrape_url(context, link, date_str)
        await browser.close()
    print(f"=== Готово. Длинные скриншоты в {SCREENSHOT_DIR}/{date_str} ===")

if __name__ == "__main__":
    asyncio.run(main())
