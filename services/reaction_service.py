from repository import reaction_repo


def toggle(post_id: int, user_id: int, reaction_type: str):
    return reaction_repo.toggle_reaction(post_id, user_id, reaction_type)


def user_flags(post_id: int, user_id: int) -> dict:
    flags = reaction_repo.get_user_reactions(post_id, user_id)
    return {
        "liked": "like" in flags,
        "favorited": "favorite" in flags,
    }
