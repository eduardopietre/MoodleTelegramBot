from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional


@dataclass
class PluginResult:
    plugin_name: str
    display_name: str
    new: bool
    message: Optional[str]
    error: Optional[Exception]
    date: datetime

    def is_empty(self):
        return (not self.message) and (self.error is None) and (not self.new)

    def strftime(self):
        local_date = self.date.astimezone(tz=timezone(-timedelta(hours=3)))
        return local_date.strftime("%d/%m/%Y %H:%M:%S")

    def get_message(self):
        if self.is_empty():
            return f"[{self.strftime()}]\nÚltimo resultado não encontrou novas alterações."

        return f"{self.display_name} alterações encontradas em [{self.strftime()}]:\n{self.message}"

    @staticmethod
    def empty():
        return PluginResult("-", "-", False, None, None, datetime.now())


class BasePlugin(ABC):

    def __init__(self, init_dictionary: dict):
        self.plugin_name = self.__class__.__name__
        self.init_dictionary = init_dictionary
        self.display_name = self.init_dictionary["display_name"]

    @abstractmethod
    def run_scrapper(self, callback):
        pass
