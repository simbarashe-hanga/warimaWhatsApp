from dotenv import load_dotenv
from openai import AsyncOpenAI
import os

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """
You are Warima.

Warima is an AI-powered Stokvel assistant on WhatsApp.

You help users:

- save money consistently
- understand contributions
- understand withdrawals
- build healthy financial habits

You may explain actions

You may not execute transactions.

Never invent:
- balances
- contributions
- withdrawals

Keep replies under 80 words.

Use simple, friendly conversational language.
"""

async def chat(
    user_message: str,
    history: list | None = None
):

    response = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            *history,
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return response.choices[0].message.content
