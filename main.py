# main.py - Entry point for Zeon120 application
# Handles configuration, selects the correct power module, and starts the main action.

import logging
import sys
from config_reader import ConfigManager
from exceptions import ConfigException


# Uncomment and use setup_logger() to enable file logging
# def setup_logger():
#     # Configure logging settings
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         filename='app.log',
#         filemode='w'
#     )


if __name__ == "__main__":
    # Initialize configuration manager
    # setup_logger()
    #logger = logging.getLogger(__name__)
    config_mgr = ConfigManager()
    try:
        # Read total power from configuration
        total_power = config_mgr.get_total_power()
        # Set the power in the configuration manager
        config_mgr.set_power(total_power)
    except ConfigException as err:
        # Exit if configuration is invalid
        #logger.error(f'error found in app config: {err}')
        sys.exit(1)
    else:
        # Dynamically import and run the correct power module based on total_power
        if int(total_power) == 120:
            from power_120kw.dynamicsharing import perform_action
        perform_action()
