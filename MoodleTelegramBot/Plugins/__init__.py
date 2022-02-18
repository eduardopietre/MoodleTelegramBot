import importlib
import logging
from MoodleTelegramBot.Plugins.BasePlugin import BasePlugin


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


LOGGER = logging.getLogger(__name__)


def load_plugins(plugins_dict: dict) -> [BasePlugin]:
    plugins_instance = []

    for plugin_name, plugin_config in plugins_dict.items():
        try:
            module = importlib.import_module(plugin_name)
            base_class = getattr(module, plugin_name)
            instance = base_class(plugin_config)
            plugins_instance.append(instance)

        except ModuleNotFoundError as error:
            LOGGER.error("At Plugins load_plugins, ModuleNotFoundError: ", error)

        except AttributeError as error:
            LOGGER.error("At Plugins load_plugins, AttributeError: ", error)

    return plugins_instance

