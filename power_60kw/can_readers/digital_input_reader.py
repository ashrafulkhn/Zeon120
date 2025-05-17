import logging
from base_reader import BaseReader
from power_60kw.constant_manager_60kw import ConstantManager60KW
from utility import bytetobinary

#logger = logging.getLogger(__name__)


class DigitalInputReader(BaseReader):
    arbitration_id = 1282

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager60KW()

    def read_input_data(self):
        #logger.info('Reading digital input data for 60KW')
        self._global_data.set_data(bytetobinary(self.data)[0])
