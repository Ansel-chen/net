from repository import subscription_repo


def follow(follower_id: int, author_id: int) -> None:
    subscription_repo.follow(follower_id, author_id)


def unfollow(follower_id: int, author_id: int) -> None:
    subscription_repo.unfollow(follower_id, author_id)


def feed(user_id: int, limit: int = 20):
    return subscription_repo.list_feed(user_id, limit)
