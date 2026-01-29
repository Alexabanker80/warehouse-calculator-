import os
import asyncio
from playwright.async_api import async_playwright

# Shin-Pro (где точно есть цены)
TARGET_URL = "https://yandex.ru/maps/-/CLx-5RiW"
OUTPUT_DIR = "company/06-marketing/monitoring-data/debug_force"

async def main():
    print("=== Атака через JS Injection ===")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        iphone = p.devices['iPhone 14 Pro']
        context = await browser.new_context(**iphone, locale='ru-RU', timezone_id='Europe/Moscow')
        page = await context.new_page()
        
        print("1. Загрузка...")
        await page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        await page.screenshot(path=f"{OUTPUT_DIR}/1_loaded.png")
        
        print("2. Ищем скроллируемый контейнер меню...")
        
        # Магия JS: ищем все div-ы, у которых контент шире экрана (горизонтальный скролл)
        # и прокручиваем их вправо до упора
        await page.evaluate("""
            () => {
                const divs = document.querySelectorAll('div');
                divs.forEach(div => {
                    const style = window.getComputedStyle(div);
                    if (style.overflowX === 'scroll' || style.overflowX === 'auto') {
                        if (div.scrollWidth > div.clientWidth) {
                            console.log('Нашли скролл! Крутим!');
                            div.scrollLeft = 5000; // Крутим до упора
                        }
                    }
                });
            }
        """)
        
        print("   -> JS отработал. Ждем прорисовку...")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"{OUTPUT_DIR}/2_scrolled.png")
        
        print("3. Ищем кнопку 'Товары' / 'Цены'...")
        found = False
        target_btn = None
        
        for kw in ["Товары", "Цены", "Услуги", "Прайс"]:
            # Ищем кнопку
            locator = page.get_by_text(kw, exact=True).last # last часто надежнее, если есть скрытые
            if await locator.is_visible():
                print(f"!!! ЕСТЬ КОНТАКТ: Вижу кнопку '{kw}' !!!")
                target_btn = locator
                found = True
                break
        
        if found:
            await target_btn.click()
            print("4. Кликнули! Ждем загрузку списка...")
            await page.wait_for_timeout(3000)
            
            # Еще раз скроллим ВНИЗ сам список товаров
            await page.mouse.wheel(0, 1000)
            await page.wait_for_timeout(1000)
            
            await page.screenshot(path=f"{OUTPUT_DIR}/SUCCESS_PRICES.png", full_page=True)
            print("УСПЕХ! Скриншот списка цен сохранен.")
        else:
            print("Не помогло. Кнопка все равно не видна.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
