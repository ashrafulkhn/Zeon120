# config_reader.py - Handles reading and managing application configuration from INI files.
# Provides ConfigManager for accessing power module settings and total power.

import configparser
import logging
from exceptions import ConfigException
from utility import Singleton

# POWER_DICT maps power values to their corresponding module names.
POWER_DICT = {
    60: 'power_60kw',
    120: 'power_120kw',
    180: 'power_180kw',
    240: 'power_240kw'
}


class ConfigManager(metaclass=Singleton):
    def __init__(self):
        """Initialize the ConfigManager, setting up the config parser and reading the INI file."""
        # Create a configparser object
        self._config = configparser.ConfigParser()
        # Read the configuration from the INI file
        self._config.read('/home/FastCharger_Zeon/bin/config.ini')
        self._power = None

    def set_power(self, power):
        """Set the current power module based on the provided power value."""
        self._power = POWER_DICT.get(int(power))

    def get_power_config(self, config_param):
        """
        Access values from sections and keys for the selected power module.

        Raises ConfigException if the desired power is not set or if the config option is missing.
        """
        if self._power is None:
            raise ConfigException('Desired power is not part of app config')
        try:
            result = self._config.get(self._power, config_param)
            return result
        except configparser.NoOptionError:
            # Raise exception if config option is missing
            raise ConfigException('Unable to get PECC config for desired power')

    def get_total_power(self):
        """
        Retrieve the total power value from the config file.

        Raises ConfigException if total power is missing from the config.
        """
        total_power_key = 'total_power'
        try:
            result = self._config.get(total_power_key, 'TOTAL_POWER')
            return result
        except configparser.NoOptionError:
            # Raise exception if total power is missing
            raise ConfigException('Unable to get total power from config')
