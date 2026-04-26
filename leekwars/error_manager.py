from abc import ABC, abstractmethod


class ErrorManager(ABC):
    @abstractmethod
    def exception(self, e: BaseException, fight_id: int, farmer: int = None, file=None) -> None:
        ...
