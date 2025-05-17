import logging
from base_reader import BaseReader
from power_120kw.constant_manager_120kw import ConstantManager120KW
from utility import bytetobinary

#logger = logging.getLogger(__name__)


class DigitalInputReader(BaseReader):
    arbitration_id = 1282

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()

    def read_input_data(self):
        #logger.info('Reading digital input data for 120KW')
        self._global_data.set_data(bytetobinary(self.data)[0])
