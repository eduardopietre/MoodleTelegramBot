import json
from MoodleTelegramBot.bot import MoodleBot
from MoodleTelegramBot.botconfig import BotConfig


def un_cypher_if_exists():
    try:
        from private import un_cypher
        return un_cypher
    except ImportError:
        return lambda x: x


def get_config(filename: str = "config.json") -> BotConfig:
    with open(filename, "r") as file:
        json_content = json.loads(file.read())
        un_cypher = un_cypher_if_exists()
        return BotConfig.from_dict(json_content, un_cypher)


if __name__ == '__main__':
    config = get_config()
    bot = MoodleBot(config)
    bot.run()
