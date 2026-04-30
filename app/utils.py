def extract_message(payload):
    try:
        message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]
        message_id = message["id"]

        return message, sender, message_id

    except Exception:
        return None
