_STAT_COUNT = 18  # STAT_LIFE..STAT_RAM, with gaps at 7,8 (unused but harmless).


class Stats:
    """Stats container backed by a flat 18-int list.

    The Java code uses TreeMap<Integer, Integer> but the keys are a small
    closed enum (0..17) — a Python list is dramatically faster to lookup
    and easier on the GC. We expose the same `.stats` attribute (a dict
    interface) for the two effect callsites that iterate it, so external
    code is unaffected.
    """

    __slots__ = ("_a",)

    def __init__(self, other=None):
        if other is not None:
            self._a = list(other._a)
        else:
            self._a = [0] * _STAT_COUNT

    def getStat(self, stat: int) -> int:
        return self._a[stat]

    def addStats(self, to_add) -> None:
        a = self._a
        b = to_add._a
        for i in range(_STAT_COUNT):
            v = b[i]
            if v:
                a[i] += v

    def setStat(self, key: int, value: int) -> None:
        self._a[key] = value

    def clear(self) -> None:
        a = self._a
        for i in range(_STAT_COUNT):
            a[i] = 0

    def updateStat(self, id_: int, delta: int) -> None:
        self._a[id_] += delta

    # Compatibility shim: some Effect callsites iterate `effect.stats.stats.items()`.
    @property
    def stats(self):
        return _StatsItemsView(self._a)


class _StatsItemsView:
    """Adapter giving the previous dict-of-stats look (only `.items()` is used)."""
    __slots__ = ("_a",)

    def __init__(self, a):
        self._a = a

    def items(self):
        a = self._a
        return [(i, v) for i, v in enumerate(a) if v]
