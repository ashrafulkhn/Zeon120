from abc import ABC, abstractmethod


class BaseReader(ABC):

    @abstractmethod
    def read_input_data(self):
        pass
