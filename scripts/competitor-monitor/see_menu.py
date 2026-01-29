import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("scripts/competitor-monitor/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

IMG_PATH = "company/06-marketing/monitoring-data/debug_force/2_scrolled.png"

def main():
    print("Глаза ИИ смотрят на меню...")
    with open(IMG_PATH, "rb") as image_file:
        b64 = base64.b64encode(image_file.read()).decode('utf-8')

    prompt = """
    Посмотри на скриншот мобильного приложения Яндекс.Карты.
    Там есть горизонтальное меню с кнопками (под названием организации).
    Перечисли ВСЕ кнопки, которые ты видишь в этом меню, слева направо.
    Например: "Обзор, Отзывы, Фото..."
    """

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
    )
    print(res.choices[0].message.content)

if __name__ == "__main__":
    main()
