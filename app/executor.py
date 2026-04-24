from app.ledger import (
    record_contribution,
    get_balance,
    get_group_balance,
    get_or_create_user
)


def handle_intent(intent_data, context, sender, db):
    intent = intent_data.get("intent")
    amount = intent_data.get("amount")

    if intent == "contribute":
        if not amount:
            return (
                "How much would you like to contribute?",
                {"awaiting_amount": True}
            )

        # 1. Save to Database
        record_contribution(db, sender, amount)

        return (
            f"You contibuted R{amount}",
            {} # clear context
        )

    if intent == "balance":
        user = get_or_create_user(db, sender)

        user_balance = get_balance(db, sender)
        group_balance = get_group_balance(user.group_id)

        return (
            f"Your balance: R{user_balance:.2f}\n"
            f"Group pool: R{group_balance:.2f}"
        ), context


    if intent == "payout":
        return ("Payout not ready yet", {})

    return ("Hi Send 'Contribute' to get started.", {})
