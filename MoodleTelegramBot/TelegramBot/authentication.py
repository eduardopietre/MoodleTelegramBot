import os
import json
from typing import Optional

from telegram import User

from . import utils


class AuthManager:

    def __init__(self, database_file: str, whitelisted_users: set[str]):
        self.database_file = database_file
        self.whitelisted_users = whitelisted_users

        self.username_chat_id_pair = self.load_database()


    def is_user_authorized(self, user: Optional[User]) -> bool:
        if user is None:
            return False
        username = utils.username_from_user(user)
        return self.is_username_authorized(username)


    def is_username_authorized(self, username: Optional[str]) -> bool:
        # Just to be safe, explicit refuse None
        if username is None:
            return False
        return username in self.whitelisted_users


    def set_user_chat_id(self, username: str, chat_id: int) -> None:
        if username in self.username_chat_id_pair or self.is_username_authorized(username):
            self.username_chat_id_pair[username] = chat_id
            self.save_database()
        else:
            # TODO: log not authorized users trying to access.
            pass


    def chat_id_for_username(self, username: str) -> Optional[int]:
        if username in self.username_chat_id_pair:
            return int(self.username_chat_id_pair[username])
        return None


    def load_database(self) -> dict[str, int]:
        if os.path.isfile(self.database_file):
            with open(self.database_file, "r") as file:
                data = json.loads(file.read())

                # Removes not auth users.
                data = {
                    username: chat_id for username, chat_id in data.items()
                    if self.is_username_authorized(username)
                }

                return data
        else:
            return dict()


    def save_database(self) -> None:
        with open(self.database_file, "w") as file:
            json.dump(self.username_chat_id_pair, file, indent=4)


    def items(self):
        return self.username_chat_id_pair.items()
