from repository import post_repo, subscription_repo


def create_post(author_id: int, title: str, body: str, tags: str | None) -> int:
    return post_repo.create_post(author_id, title, body, tags)


def list_posts(limit: int = 20, offset: int = 0):
    return post_repo.list_posts(limit, offset)


def list_by_author(author_id: int, limit: int = 20):
    return post_repo.list_by_author(author_id, limit)


def get_post(post_id: int):
    return post_repo.get_post(post_id)


def update_post(post_id: int, author_id: int, title: str, body: str, tags: str | None) -> bool:
    return post_repo.update_post(post_id, author_id, title, body, tags)


def delete_post(post_id: int, author_id: int) -> bool:
    return post_repo.delete_post(post_id, author_id)


def feed_for_user(user_id: int, limit: int = 20):
    return subscription_repo.list_feed(user_id, limit)


def search_posts(keyword: str | None, tag: str | None, limit: int = 20, offset: int = 0):
    return post_repo.search_posts(keyword, tag, limit, offset)


def list_categories(limit: int = 10):
    return post_repo.list_categories(limit)
