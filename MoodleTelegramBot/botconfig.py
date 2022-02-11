from dataclasses import dataclass
from MoodleTelegramBot.MoodleBot.data import CourseConfig


@dataclass
class BotConfig:
    telegram_bot_token: str
    notify: [str]
    database: str
    login_user: str
    login_pass: str
    base_url: str
    username_whitelist: [str]
    check_delay: int
    username_chat_id_cache: str
    courses: [CourseConfig]

    @staticmethod
    def from_dict(d: dict, un_cypher):
        return BotConfig(
            telegram_bot_token=d["telegram_bot_token"],
            notify=d["notify"],
            database=d["database"],
            base_url=d["base_url"],
            username_whitelist=d["username_whitelist"],
            check_delay=d["check_delay"],
            username_chat_id_cache=d["username_chat_id_cache"],
            login_user=un_cypher(d["login"]),
            login_pass=un_cypher(d["password"]),
            courses=[
                CourseConfig(
                    id=sub_d["id"],
                    name=sub_d["name"],
                    parser=sub_d["parser"]
                ) for sub_d in d["courses"]
            ]
        )

