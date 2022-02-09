import json
from private import BOT_TOKEN, un_cypher
from MoodleTelegramBot.bot import MoodleBot
from MoodleTelegramBot.MoodleBot.scrapperconfig import ScrapperConfig


def get_username_whitelist(filename: str = "username_whitelist.txt") -> set[str]:
    usernames = set()

    with open(filename, "r") as file:
        for line in file:
            user = line.strip()
            if user:
                usernames.add(user)

    return usernames


def get_configs(filename: str = "configs.json") -> [ScrapperConfig]:
    with open(filename, "r") as file:
        dicts = json.loads(file.read())
        return [ScrapperConfig.from_dict(d, un_cypher) for d in dicts]


if __name__ == '__main__':
    username_whitelist = get_username_whitelist()
    config = get_configs()[0]

    # In seconds, 2hrs
    check_delay = 60 * 60 * 2

    bot = MoodleBot(
        token=BOT_TOKEN,
        database_file="mgb_database.json",
        whitelisted_users=username_whitelist,
        scrapper_config=config,
        check_delay=check_delay
    )

    bot.run()
