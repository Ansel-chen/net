from repository import reaction_repo


def toggle(post_id: int, user_id: int, reaction_type: str):
    return reaction_repo.toggle_reaction(post_id, user_id, reaction_type)
