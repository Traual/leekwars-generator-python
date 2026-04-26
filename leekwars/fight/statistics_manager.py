from abc import abstractmethod

from ..statistics.statistics_manager import StatisticsManager as BaseStatisticsManager


class StatisticsManager(BaseStatisticsManager):
    """Fight-aware statistics manager interface."""

    @abstractmethod
    def setGeneratorFight(self, fight) -> None:
        ...
