from abc import *


class ServiceOverlayBase(metaclass=ABCMeta):
    def __init__(self):
        pass

    def __del__(self):
        pass

    @abstractmethod
    def file_check(self, files):
        pass

    @abstractmethod
    def convert(self, logs):
        pass
