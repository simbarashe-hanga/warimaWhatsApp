user_memory = {}

def get_user_context(user_id: str):
    return user_memory.get(user_id, {})


def update_user_context(user_id: str, data: dict):
    if user_id not in user_memory:
        user_memory[user_id] = {}

    user_memory[user_id].update(data)


def clear_user_context(user_id: str):
    user_memory.pop(user_id, None)
