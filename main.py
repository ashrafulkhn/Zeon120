import logging
import sys
from config_reader import ConfigManager
from exceptions import ConfigException


# def setup_logger():
#     # Configure logging settings
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         filename='app.log',
#         filemode='w'
#     )


if __name__ == "__main__":
    # setup_logger()
    #logger = logging.getLogger(__name__)
    config_mgr = ConfigManager()
    try:
        total_power = config_mgr.get_total_power()
        config_mgr.set_power(total_power)
    except ConfigException as err:
        #logger.error(f'error found in app config: {err}')
        sys.exit(1)
    else:

        if int(total_power) == 120:
            from power_120kw.dynamicsharing import perform_action
 
        perform_action()
