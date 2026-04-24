def extract_message(payload):
    try:
        entry = payload["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return None

        message = value["messages"][0]
        sender = message["from"]

        return message, sender

    except Exception:
        return None
