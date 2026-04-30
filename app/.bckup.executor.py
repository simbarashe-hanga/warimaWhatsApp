from app.ledger import (
    record_contribution,
    get_balance,
    get_group_balance,
)


def handle_intent(intent_data, context, sender, db, user):
    intent = intent_data.get("intent")
    amount = intent_data.get("amount")

    if intent == "contribute":
        if not amount:
            return (
                "How much would you like to contribute?",
                {"awaiting_amount": True}
            )

        # 1. Save to Database
        record_contribution(db, user, amount, user.group_id)

        return (
            f"You contibuted R{amount}",
            {} # clear context
        )

    if intent == "balance":
        user_balance = get_balance(db, sender)

        if user.group_id:
            group_balance = get_group_balance(db, user.group_id)
        else:
            group_balance = 0.0

        return (
            f"Your balance: R{user_balance:.2f}\n"
            f"Group pool: R{group_balance:.2f}",
            context
        )

    if intent == "payout":
        return ("Payout not ready yet", {})

    return ("Hi Send 'Contribute' to get started.", {})
