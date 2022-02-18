from datetime import datetime

from MoodleTelegramBot.Plugins.BasePlugin import BasePlugin, PluginResult
from .data import CourseConfig
from .scrapper import MoodleScraper
from .logger import LOGGER


class MoodleBot(BasePlugin):


    def __init__(self, init_dictionary: dict):
        super(MoodleBot, self).__init__(init_dictionary)
        self.base_url = self.init_dictionary["base_url"]
        self.database = self.init_dictionary["database"]
        self.username = self.init_dictionary["username"]
        self.password = self.init_dictionary["password"]
        self.courses = [
            CourseConfig(d["id"], d["name"], d["parser"])
            for d in self.init_dictionary["courses"]
        ]


    def run_scrapper(self, callback):
        result = self.__run_scrapper()
        callback(result)


    def __run_scrapper(self):
        try:
            scraper = MoodleScraper(
                url=self.base_url,
                database_file=self.database,
                username=self.username,
                password=self.password
            )

            log = scraper.scraper(self.courses)

            return PluginResult(
                plugin_name="MoodleBot",
                new=True,
                message=log,
                error=None,
                date=datetime.now()
            )

        except Exception as error:
            LOGGER.error(f"Exception at run_scrapper: {error}")
            return PluginResult(
                plugin_name="MoodleBot",
                new=False,
                message=None,
                error=error,
                date=datetime.now()
            )
