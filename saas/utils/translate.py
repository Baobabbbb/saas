from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def translate_text(text: str) -> str:
    """
    Traduit du texte en anglais via OpenAI (GPT-4o-mini) - version asynchrone.
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a translator that only translates to English. No explanation. Return only the translated text."},
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()
