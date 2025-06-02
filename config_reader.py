import configparser
import logging
from exceptions import ConfigException
from utility import Singleton

#logger = logging.getLogger(__name__)

POWER_DICT = {
    60: 'power_60kw',
    120: 'power_120kw',
    180: 'power_180kw',
    240: 'power_240kw'
}

class ConfigManager(metaclass=Singleton):
    def __init__(self):
        # Create a configparser object
        self._config = configparser.ConfigParser()
        # Read the configuration from the INI file
        self._config.read('/home/FastCharger_Zeon/bin/config.ini')
        #self._config.read('/home/Standard_Dec15/bin/config.ini')
        self._power = None

    def set_power(self, power):
        self._power = POWER_DICT.get(int(power))

    def get_power_config(self, config_param):
        # Access values from sections and keys
        if self._power is None:
            raise ConfigException('Desired power is not part of app config')
        try:
            result = self._config.get(self._power, config_param)
            return result
        except configparser.NoOptionError:
            #logger.error('Unable to get PECC config for desired power')
            raise ConfigException('Unable to get PECC config for desired power')

    def get_total_power(self):
        total_power_key = 'total_power'
        try:
            result = self._config.get(total_power_key, 'TOTAL_POWER')
            return result
        except configparser.NoOptionError:
            #logger.error('Unable to get total power from config')
            raise ConfigException('Unable to get total power from config')
