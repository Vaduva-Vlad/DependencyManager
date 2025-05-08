from abc import abstractmethod
from abc import ABC

class Command(ABC):
    def __init__(self, module):
        self.module=module

    @abstractmethod
    def run(self, args):
        pass