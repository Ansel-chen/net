from repository import comment_repo


def add_comment(post_id: int, user_id: int, body: str, parent_id: int | None):
    return comment_repo.create_comment(post_id, user_id, body, parent_id)


def list_comments(post_id: int):
    return comment_repo.list_by_post(post_id)
