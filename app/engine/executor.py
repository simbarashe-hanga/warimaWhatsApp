from app.services.transaction_service import create_or_get_transaction

def handle_intent(intent_data, context, user_id, db):
    intent = intent_data.get("intent")

    context = context or {}

    response = "Sorry, I don't understand."
    new_context = context
    next_action = None

    if intent == "greeting":
        response = "Hey! Type 'contribute' or 'agent' to get started."

    elif intent == "start_contribution":
        response = "How much would you like to contribute?"
        new_context = {"flow": "contribution", "step": "awaiting_amount"}

    elif intent == "agent":
        response= "You are chatting with the Warima A.I Agent"
        new_context = {"flow": "agent_flow", "step": "chatting"}

    elif intent == "provide_amount":
        amount = intent_data.get("amount")
        response = f"Confirm R{amount}? Reply 1 to confirm, 2 to cancel."
        new_context = {
            "flow": "contribution",
            "step": "awaiting_confirmation",
            "amount": amount
        }

    elif intent == "confirm":
        amount = context.get("amount")

        if not amount:
            response = "No amount found. Do you want to chat with 'agent' or 'contribute'."
        else:
            txn = create_or_get_transaction(db, user_id, amount)
            response = f"Contribution of R{amount} received. Transaction ID: {txn.id}"

        new_context = None

    elif intent == "cancel":
        response = "Cancelled. Type 'contribute' to start again."
        new_context = None

    return response, new_context, next_action
