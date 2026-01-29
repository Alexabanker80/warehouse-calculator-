import os
import asyncio
import random
from playwright.async_api import async_playwright

TARGET_URL = "https://yandex.ru/maps/-/CLx-5RiW" # Shin-Pro
OUTPUT_DIR = "company/06-marketing/monitoring-data/debug_shinpro_v2"

async def main():
    print("=== Отладка v2 (Умный свайп) ===")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        iphone = p.devices['iPhone 14 Pro']
        context = await browser.new_context(**iphone, locale='ru-RU', timezone_id='Europe/Moscow')
        page = await context.new_page()
        
        await page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        await page.screenshot(path=f"{OUTPUT_DIR}/1_start.png")

        # Ищем любой видимый элемент меню (например, "Обзор" или "Отзывы")
        # Чтобы понять, на какой высоте делать свайп
        anchor = page.get_by_text("Отзывы").first
        
        y_coord = 250 # Дефолт
        
        if await anchor.is_visible():
            box = await anchor.bounding_box()
            if box:
                y_coord = box['y'] + box['height'] / 2
                print(f"-> Нашли якорь 'Отзывы' на высоте {y_coord}")
        else:
            print("-> Якорь не найден, используем дефолт 250")
            
        # Теперь ищем Цены
        target_found = False
        keywords = ["Товары", "Цены", "Услуги", "Прайс"]
        
        for attempt in range(10): # Больше попыток
            # 1. Проверка видимости
            for kw in keywords:
                btn = page.get_by_text(kw, exact=True).first
                if await btn.is_visible():
                    print(f"!!! НАШЛИ КНОПКУ: {kw}")
                    await btn.click()
                    target_found = True
                    break
            
            if target_found: break
            
            print(f"   (Свайп {attempt+1}) Тянем меню влево на высоте {y_coord}...")
            
            # Свайп
            await page.mouse.move(350, y_coord)
            await page.mouse.down()
            await page.mouse.move(50, y_coord, steps=15) # Медленный свайп
            await page.mouse.up()
            await page.wait_for_timeout(800)
            
            await page.screenshot(path=f"{OUTPUT_DIR}/swipe_{attempt}.png")
            
        if target_found:
            await page.wait_for_timeout(3000)
            await page.screenshot(path=f"{OUTPUT_DIR}/SUCCESS_prices.png", full_page=True)
            print("УСПЕХ! Скриншот цен сделан.")
        else:
            print("ПРОВАЛ. Кнопка не найдена.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
