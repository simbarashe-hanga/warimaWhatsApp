from app.models.conversation import ConversationMessage

#Save message
def save_message(
    db,
    user_id,
    role,
    content
):
    msg = ConversationMessage(
        user_id=user_id,
        role=role,
        content=content
    )

    db.add(msg)
    db.commit()

#Load recent history
def get_recent_messages(
    db,
    user_id,
    limit=10
):
    messages = (
        db.query(ConversationMessage)
        .filter_by(user_id=user_id)
        .order_by(
            ConversationMessage.id.desc()
        )
        .limit(limit)
        .all()
    )

    messages.reverse()

    return [
        {
            "role":m.role,
            "content":m.content
        }
        for m in messages
    ]
