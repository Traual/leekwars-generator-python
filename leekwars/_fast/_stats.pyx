# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True
"""Cython cdef class for Stats — backed by a fixed-size C int array.

The pure-Python Stats stored an 18-element list. Every clone of an
Entity allocates two new Stats. Cythonising this as a cdef class with a
``int _a[18]`` member turns those allocations into single struct writes
and makes ``getStat`` / ``setStat`` direct memory accesses.

Backward compat: same method names (``getStat``, ``setStat``, ``addStats``,
``clear``, ``updateStat``), plus the ``.stats`` property returning a
view with ``.items()`` for the few effect callsites that iterate it.
"""


cdef int _STAT_COUNT = 18


cdef class Stats:
    cdef int[18] _a

    def __cinit__(self, Stats other=None):
        cdef int i
        if other is None:
            for i in range(18):
                self._a[i] = 0
        else:
            for i in range(18):
                self._a[i] = other._a[i]

    cpdef int getStat(self, int stat):
        return self._a[stat]

    cpdef setStat(self, int key, int value):
        self._a[key] = value

    cpdef updateStat(self, int id_, int delta):
        self._a[id_] += delta

    cpdef clear(self):
        cdef int i
        for i in range(18):
            self._a[i] = 0

    cpdef addStats(self, Stats to_add):
        cdef int i, v
        for i in range(18):
            v = to_add._a[i]
            if v:
                self._a[i] += v

    @property
    def stats(self):
        return _StatsItemsView.create(self)


cdef class _StatsItemsView:
    cdef Stats _stats

    @staticmethod
    cdef _StatsItemsView create(Stats s):
        cdef _StatsItemsView v = _StatsItemsView.__new__(_StatsItemsView)
        v._stats = s
        return v

    def items(self):
        cdef int i, v
        out = []
        for i in range(18):
            v = self._stats._a[i]
            if v:
                out.append((i, v))
        return out
