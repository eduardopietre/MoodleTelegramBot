from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PluginResult:
    new: bool
    plugin_name: str
    messages: [str]


class BasePlugin(ABC):

    def __init__(self, init_dictionary: dict):
        self.init_dictionary = init_dictionary

    @abstractmethod
    def run_scrapper(self) -> PluginResult:
        pass