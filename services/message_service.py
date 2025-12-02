from repository import message_repo


def send(sender_id: int, receiver_id: int, subject: str, body: str):
    return message_repo.send_message(sender_id, receiver_id, subject, body)


def inbox(user_id: int):
    return message_repo.list_inbox(user_id)


def outbox(user_id: int):
    return message_repo.list_outbox(user_id)
