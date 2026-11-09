import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

async def ask_ai(question: str, system_prompt: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="deepseek/deepseek-r1:free", # Бесплатная модель
            messages=[
                {"role": "system", "content": system_prompt}, # Сюда придет промпт от Разработчика 2
                {"role": "user", "content": question}
            ],
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        return "Извини, у меня неполадки с сетью. Попробуй позже."