from repository import post_repo, subscription_repo
from services import reaction_service


def _normalize_post(record: dict | None) -> dict | None:
    if not record:
        return None
    record["like_count"] = int(record.get("like_count") or 0)
    record["favorite_count"] = int(record.get("favorite_count") or 0)
    return record


def create_post(author_id: int, title: str, body: str, tags: str | None) -> int:
    return post_repo.create_post(author_id, title, body, tags)


def list_posts(limit: int = 20, offset: int = 0):
    return [_normalize_post(item) for item in post_repo.list_posts(limit, offset)]


def list_by_author(author_id: int, limit: int = 20):
    return [_normalize_post(item) for item in post_repo.list_by_author(author_id, limit)]


def get_post(post_id: int, user_id: int | None = None):
    post = _normalize_post(post_repo.get_post(post_id))
    if not post:
        return None
    if user_id:
        flags = reaction_service.user_flags(post_id, user_id)
        post.update(flags)
    else:
        post.update({"liked": False, "favorited": False})
    return post


def update_post(post_id: int, author_id: int, title: str, body: str, tags: str | None) -> bool:
    return post_repo.update_post(post_id, author_id, title, body, tags)


def delete_post(post_id: int, author_id: int) -> bool:
    return post_repo.delete_post(post_id, author_id)


def feed_for_user(user_id: int, limit: int = 20):
    return [_normalize_post(item) for item in subscription_repo.list_feed(user_id, limit)]


def search_posts(keyword: str | None, tag: str | None, limit: int = 20, offset: int = 0):
    return [_normalize_post(item) for item in post_repo.search_posts(keyword, tag, limit, offset)]


def list_categories(limit: int = 10):
    return post_repo.list_categories(limit)


def list_reacted_posts(user_id: int, reaction_type: str, limit: int = 20):
    return [_normalize_post(item) for item in post_repo.list_reacted_by_user(user_id, reaction_type, limit)]


def get_post_stats():
    data = post_repo.get_post_stats()
    return {
        "total_posts": int(data.get("total_posts") or 0),
        "latest_created_at": data.get("latest_created_at"),
    }
