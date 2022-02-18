from typing import Any

from telegram import User, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from .authentication import AuthManager
from .logger import LOGGER



class BaseBot:

    def __init__(self, token: str, database_file: str, whitelisted_users: set[str]):
        self.token = token
        self.auth_manager = AuthManager(database_file, whitelisted_users)

        # Create the Updater and pass it your bot's token.
        self.updater = Updater(self.token)


    def authenticate_user(self, user: User, chat_id: int):
        username = user.username

        if username is None:  # Security checks
            return

        self.auth_manager.set_user_chat_id(username, chat_id)


    def is_user_authenticate(self, user: User):
        self.auth_manager.is_user_authorized(user)


    def reply_update(self, update: Update, message: str) -> None:
        max_len = 4000  # 4096 in reality, but use 4000
        if len(message) > max_len:
            for i in range(0, len(message), max_len):
                update.message.reply_text(message[i:i + max_len])
        else:
            update.message.reply_text(message)


    def send_message_to_chat_id(self, chat_id: int, message: str) -> None:
        max_len = 4000  # 4096 in reality, but use 4000
        if len(message) > max_len:
            for i in range(0, len(message), max_len):
                self.updater.bot.send_message(chat_id, message[i:i + max_len])
        else:
            self.updater.bot.send_message(chat_id, message)


    def send_message_to_username(self, username: str, message: str) -> None:
        chat_id = self.auth_manager.chat_id_for_username(username)
        if chat_id:
            self.updater.bot.send_message(chat_id, message)
        else:
            LOGGER.warning(f"ChatId for username {username} not found.")


    def base_run(self, handlers: [(str, Any)], text_handler: Any) -> None:
        # Register handlers
        dispatcher = self.updater.dispatcher

        for command, func_handler in handlers:
            dispatcher.add_handler(CommandHandler(command, func_handler))


        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
