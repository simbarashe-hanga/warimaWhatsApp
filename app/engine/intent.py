def detect_intent(text: str, context: dict):
    text = text.lower().strip()

    if text in ["hi", "hello", "hey"]:
        return {"intent": "greeting"}

    if "contribute" in text:
        return {"intent": "start_contribution"}

    if "agent" in text:
        return {"intent": "agent"}

    if text == "1":
        return {"intent": "confirm"}

    if text == "2":
        return {"intent": "cancel"}
    
    if text.isdigit():
        return {"intent": "provide_amount", "amount": int(text)}

    return {"intent": "unknown"}
