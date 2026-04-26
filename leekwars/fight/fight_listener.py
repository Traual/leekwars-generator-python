from abc import ABC, abstractmethod


class FightListener(ABC):

    @abstractmethod
    def newTurn(self, fight) -> None:
        ...
