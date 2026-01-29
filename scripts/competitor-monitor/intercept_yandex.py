import asyncio
import json
import os
from playwright.async_api import async_playwright

# Цель: Shin-Pro (там точно есть цены)
TARGET_URL = "https://yandex.ru/maps/-/CLx-5RiW"
OUTPUT_FILE = "company/06-marketing/monitoring-data/yandex_intercept.json"

async def apply_stealth(page):
    """Маскировка под человека."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
    """)

async def main():
    print("=== Операция 'Перехват' (No-Deps) ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale='ru-RU',
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await apply_stealth(page)
        
        captured_data = []

        async def handle_response(response):
            try:
                # Фильтруем только JSON
                ct = response.headers.get("content-type", "")
                if "application/json" in ct or "text/javascript" in ct:
                    url = response.url
                    if "maps" in url or "biz" in url or "1.x" in url:
                        try:
                            body = await response.json()
                            text = json.dumps(body, ensure_ascii=False)
                            # Ищем цены
                            if "price" in text or "goods" in text:
                                print(f"!!! ПОЙМАЛИ ПАКЕТ: {len(text)} байт")
                                captured_data.append(body)
                        except:
                            pass
            except:
                pass

        page.on("response", handle_response)
        
        print("1. Заходим на страницу...")
        try:
            await page.goto(TARGET_URL, timeout=60000, wait_until="networkidle")
        except:
            print("   (Таймаут, но продолжаем)")
        
        print("2. Провоцируем сервер...")
        # Скролл вниз
        await page.mouse.wheel(0, 2000)
        await page.wait_for_timeout(3000)
        
        # Попытка клика
        try:
            await page.get_by_text("Товары и услуги").click(timeout=5000)
            print("   -> Кликнули 'Товары'")
            await page.wait_for_timeout(3000)
        except:
            print("   -> Клик не удался")
            # Сделаем скриншот для отладки
            await page.screenshot(path="company/06-marketing/monitoring-data/debug_intercept.png")

        print(f"3. Сохраняем {len(captured_data)} пакетов...")
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(captured_data, f, ensure_ascii=False, indent=2)
            
        await browser.close()
        print(f"Готово: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
