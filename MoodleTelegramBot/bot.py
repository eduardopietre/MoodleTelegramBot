import time
import threading
from typing import Optional

from telegram import Update
from telegram.ext import CallbackContext

from MoodleTelegramBot.TelegramBot import utils
from MoodleTelegramBot.TelegramBot.timer import RepeatedTimer
from MoodleTelegramBot.TelegramBot.basebot import BaseBot

from MoodleTelegramBot.MoodleBot import BotResult, run_scrapper
from MoodleTelegramBot.botconfig import BotConfig


def commands_helper_str():
    helps = [
        "/start  -  Autoriza o usuário.",
        "/check  -  Roda novamente a verificação.",
        "/echo - Retorna o resultado da última verificação.",
        "/next  -  Mostra quanto tempo falta para a próxima verificação.",
    ]

    return "\n".join(helps)



class MoodleBot(BaseBot):

    def __init__(self, config: BotConfig):
        super().__init__(
            config.telegram_bot_token,
            config.username_chat_id_cache,
            config.username_whitelist
        )

        self.scrapper_config = config
        self.check_delay = config.check_delay

        self.repeating_check: Optional[RepeatedTimer] = None
        self.previous_result: BotResult = BotResult.empty()
        self.is_scrapping = False

        self.scrapper_thread = None


    def alert_all_users(self, message):
        for username, chat_id in self.auth_manager.items():
            self.send_message_to_chat_id(chat_id, message)


    def on_callback_result(self, bot_result: Optional[BotResult]):
        self.is_scrapping = False
        self.previous_result = bot_result

        if self.previous_result.result and self.previous_result.new:
            self.alert_all_users(self.previous_result.message())


    def __internal_run_scrapper(self):
        run_scrapper(self.scrapper_config, self.on_callback_result)


    def run_scrapper(self):
        self.is_scrapping = True
        self.scrapper_thread = threading.Thread(target=self.__internal_run_scrapper)
        self.scrapper_thread.start()


    # Start commands handlers


    def cmd_start(self, update: Update, context: CallbackContext) -> None:
        # Send a message when the command /start is issued.

        user = update.effective_user
        is_auth = self.auth_manager.is_user_authorized(user)
        message = utils.greetings_for_user(user, is_auth)

        if is_auth:
            self.authenticate_user(user, update.effective_message.chat_id)

        update.message.reply_markdown_v2(message)


    def cmd_text(self, update: Update, context: CallbackContext) -> None:
        if not self.auth_manager.is_user_authorized(update.effective_user):
            return

        update.message.reply_text(f"Não há comandos com essas palavras.\n{commands_helper_str()}")


    def cmd_check(self, update: Update, context: CallbackContext) -> None:
        if not self.auth_manager.is_user_authorized(update.effective_user):
            return

        if self.is_scrapping:
            update.message.reply_text(f"Uma verificação já está em andamento, deseja forçar o cancelamento?\nUse /cancel")
        else:
            update.message.reply_text(f"Entendido. Iniciando verificação, por favor aguarde...")
            self.run_scrapper()


    def cmd_cancel(self, update: Update, context: CallbackContext) -> None:
        if not self.auth_manager.is_user_authorized(update.effective_user):
            return

        if self.is_scrapping:
            self.is_scrapping = False
            update.message.reply_text(f"Tentativa de cancelar recebida.")
        else:
            update.message.reply_text(f"Não há verificação a ser cancelada.")


    def cmd_echo(self, update: Update, context: CallbackContext) -> None:
        if not self.auth_manager.is_user_authorized(update.effective_user):
            return

        if self.previous_result.result or self.previous_result.is_empty():
            update.message.reply_text(self.previous_result.message())
        elif self.previous_result.error:
            update.message.reply_text(str(self.previous_result.error))
        else:
            update.message.reply_text("Não encontramos o último resultado.")


    def cmd_next(self, update: Update, context: CallbackContext) -> None:
        if not self.auth_manager.is_user_authorized(update.effective_user):
            return

        if self.repeating_check:
            next_time = self.repeating_check.next_call
            now = time.time()

            interval = next_time - now
            hours = int(interval / (60 * 60))
            minutes = int((interval % (60 * 60)) / 60)
            seconds = round(interval % 60)

            update.message.reply_text(f"Verificação em {hours} hora(s), {minutes} minuto(s) e {seconds} segundo(s).")

        else:
            update.message.reply_text("Não encontramos a verificação recorrente.")


    # End command handlers


    def run(self) -> None:
        # Set it up to check every X seconds
        self.repeating_check = RepeatedTimer(self.check_delay, self.run_scrapper)

        handlers = [
            ("start", self.cmd_start),

            ("check", self.cmd_check),
            ("c", self.cmd_check),

            ("echo", self.cmd_echo),
            ("e", self.cmd_echo),

            ("next", self.cmd_next),
            ("n", self.cmd_next),

            ("cancel", self.cmd_cancel)
        ]

        self.base_run(handlers, self.cmd_text)
