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
    plugins: dict

    @staticmethod
    def from_dict(d: dict, un_cypher):

        def _plugin_un_cypher(orig_plugin_dict):
            plugin_dict = {}

            for k, v in orig_plugin_dict.items():
                # Use recursion when encountering a dict
                if type(v) == dict:
                    v = _plugin_un_cypher(v)

                # If key ends with _cypher then un_cypher it
                if k.endswith("__cypher"):
                    plugin_dict[k.replace("__cypher", "")] = un_cypher(v)
                else:
                    plugin_dict[k] = v

            return plugin_dict


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
            ],
            plugins=_plugin_un_cypher(d["plugins"])
        )

