import re

def detect_intent(text: str, context: dict):
    text = text.lower()

    # 1. If waiting for amount
    if context.get("awaiting_amount"):
        return {
            "intent": "contribute",
            "amount": extract_amount(text),
            "from_context": True
        }

    # 2. Normal detection
    if "pay" in text or "contribute" in text:
        return {"intent": "contribute", "amount": extract_amount(text)}

    if "balance" in text:
        return {"intent": "balance", "amount": None}

    if "payout" in text:
        return {"intent": "payout", "amount": None}

    return {"intent": "general", "amount": None}


def extract_amount(text: str):
    match = re.search(r"\d+(\.\d+)?", text)
    return float(match.group()) if match else None
