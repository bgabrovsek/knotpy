from abc import ABC, abstractmethod

class ReidemeisterLocation(ABC):

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()

