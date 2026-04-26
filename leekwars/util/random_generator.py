from abc import ABC, abstractmethod


class RandomGenerator(ABC):
    @abstractmethod
    def seed(self, seed: int) -> None:
        ...

    @abstractmethod
    def get_int(self, min_v: int, max_v: int) -> int:
        ...

    @abstractmethod
    def get_long(self, min_v: int, max_v: int) -> int:
        ...

    @abstractmethod
    def get_double(self) -> float:
        ...
