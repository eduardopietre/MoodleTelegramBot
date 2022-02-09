from typing import Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from .scrapper import MoodleScraper
from .logger import LOGGER
from .scrapperconfig import ScrapperConfig


@dataclass
class BotResult:
    result: Optional[str]
    error: Optional[Exception]
    new: bool
    date: datetime

    def is_empty(self):
        return self.result == "" and self.error is None and not self.new

    def strftime(self):
        local_date = self.date.astimezone(tz=timezone(-timedelta(hours=3)))
        return local_date.strftime("%d/%m/%Y %H:%M:%S")

    def message(self):
        if self.is_empty():
            return f"[{self.strftime()}]\nÚltimo resultado não encontrou novas alterações."

        return f"As seguintes alterações no Moodle foram encontradas em [{self.strftime()}]:\n{self.result}"

    @staticmethod
    def empty():
        return BotResult(None, None, False, datetime.now())



def run_scrapper(scrapper_config: ScrapperConfig, callback):
    def __run_scrapper():
        try:
            scraper = MoodleScraper(
                url=scrapper_config.base_url,
                database_file=scrapper_config.database,
                username=scrapper_config.login_user,
                password=scrapper_config.login_pass
            )

            log = scraper.scraper(scrapper_config.courses)

            return BotResult(log, None, scraper.found, datetime.now())

        except Exception as error:
            LOGGER.error(f"Exception at run_scrapper: {error}")
            return BotResult(None, error, False, datetime.now())


    result = __run_scrapper()
    callback(result)
