user_memory = {}

processed_message = set()

def get_user_context(user_id: str):
    return user_memory.get(user_id, {})


def update_user_context(user_id: str, data: dict):
    if user_id not in user_memory:
        user_memory[user_id] = {}

    user_memory[user_id].update(data)


def clear_user_context(user_id: str):
    user_memory.pop(user_id, None)


def is_duplicate(message_id: str):
    if message_id in processed_messages:
        return True

    processed_messages.add(message_id)
    return False
