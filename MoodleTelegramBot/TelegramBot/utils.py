from typing import Optional
from telegram import Update, User


def username_from_update(update: Update) -> Optional[str]:
    effective_user = update.effective_user
    return username_from_user(effective_user)


def username_from_user(user: User) -> Optional[str]:
    return user.username if user else None


def greetings_for_user(user: User, is_auth: bool) -> str:
    username = username_from_user(user)
    append = " " if is_auth else " não "

    return fr"Olá {user.mention_markdown_v2()}\! Seu usuário é '{username}'\. E você{append}está autenticado\."
