def extract_message(payload: dict):
    try:
        entry = payload.get("entry", [])
        if not entry:
            return None

        changes = entry[0].get("changes", [])
        if not changes:
            return None

        value = changes[0].get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return None

        msg = messages[0]

        return {
            "id": msg.get("id"),
            "user_id": msg.get("from"),
            "text": msg.get("text", {}).get("body", "").strip().lower()
        }

    except Exception as e:
        print("extract_message error:", e)
        return None
