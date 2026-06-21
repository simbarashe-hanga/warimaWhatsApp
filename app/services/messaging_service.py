import httpx
import os


async def send_message(user_id: str, text: str):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_ID")

    if not token or not phone_id:
        raise Exception("Missing WhatsApp env vars")

    url = f"https://graph.facebook.com/v25.0/{phone_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": user_id,
        "type": "text",
        "text": {"body": text}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    # Debug log
    print("PAYLOAD SENT:", payload)
    print("RESPONSE:", response.json())
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    return response.json()
