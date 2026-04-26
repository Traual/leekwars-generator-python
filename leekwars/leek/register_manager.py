from abc import ABC, abstractmethod


class RegisterManager(ABC):

    @abstractmethod
    def getRegisters(self, leek: int) -> str:
        ...

    @abstractmethod
    def saveRegisters(self, leek: int, registers: str, is_new: bool) -> None:
        ...
