from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def translate_to_english(text: str) -> str:
    """
    Traduit du texte en anglais via OpenAI (GPT-4o-mini).
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a translator that only translates to English. No explanation. Return only the translated text."},
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()
