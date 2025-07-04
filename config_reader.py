# import configparser
# import logging
# import os
# from pathlib import Path
# from typing import Optional, Dict, Any

# from exceptions import ConfigException
# from utility import Singleton

# logger = logging.getLogger(__name__)

# POWER_DICT = {
#     60: 'power_60kw',
#     120: 'power_120kw',
#     180: 'power_180kw',
#     240: 'power_240kw'
# }

# class ConfigManager(metaclass=Singleton):
#     """Configuration manager with improved validation and flexibility."""
    
#     def __init__(self):
#         self._config = configparser.ConfigParser()
#         self._power: Optional[str] = None
#         self._load_config()
        
#     def _load_config(self) -> None:
#         """Load configuration from various possible locations."""
#         config_paths = [
#             '/home/FastCharger_Zeon/bin/config.ini',
#             '/home/Standard_Dec15/bin/config.ini',
#             os.path.join(os.getcwd(), 'config.ini'),
#             os.path.expanduser('~/.config/fastcharger/config.ini')
#         ]
        
#         for path in config_paths:
#             if os.path.exists(path):
#                 logger.info(f"Loading configuration from {path}")
#                 self._config.read(path)
#                 return
                
#         raise ConfigException("No valid configuration file found")
    
#     def validate_config(self) -> None:
#         """Validate the configuration file structure and values."""
#         if not self._config.has_section('total_power'):
#             raise ConfigException("Missing 'total_power' section in config")
            
#         if not self._config.has_option('total_power', 'TOTAL_POWER'):
#             raise ConfigException("Missing 'TOTAL_POWER' setting in config")
            
#         try:
#             power = int(self._config.get('total_power', 'TOTAL_POWER'))
#             if power not in POWER_DICT:
#                 raise ConfigException(f"Invalid power value: {power}. Must be one of {list(POWER_DICT.keys())}")
#         except ValueError:
#             raise ConfigException("TOTAL_POWER must be an integer")
    
#     def set_power(self, power: str) -> None:
#         """Set the power configuration after validation."""
#         power_int = int(power)
#         if power_int not in POWER_DICT:
#             raise ConfigException(f"Invalid power setting: {power}")
#         self._power = POWER_DICT[power_int]
#         logger.debug(f"Power set to {self._power}")
    
#     def get_power_config(self, config_param: str) -> str:
#         """Get power-specific configuration parameter."""
#         if self._power is None:
#             raise ConfigException('Power setting not initialized')
#         try:
#             result = self._config.get(self._power, config_param)
#             return result
#         except configparser.NoOptionError as e:
#             logger.error(f'Unable to get config parameter {config_param} for {self._power}')
#             raise ConfigException(f'Missing configuration: {e}')
    
#     def get_total_power(self) -> str:
#         """Get the total power setting after validation."""
#         self.validate_config()
#         return self._config.get('total_power', 'TOTAL_POWER')
    
#     def get_all_power_settings(self) -> Dict[str, Any]:
#         """Get all power-related settings for the current configuration."""
#         if self._power is None:
#             raise ConfigException('Power setting not initialized')
        
#         try:
#             return dict(self._config.items(self._power))
#         except configparser.NoSectionError:
#             raise ConfigException(f'No configuration section found for {self._power}')
        

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
        # self._config.read('/home/FastCharger_Zeon/bin/config.ini')
        self._config.read('/home/Standard_Dec15/config.ini')
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