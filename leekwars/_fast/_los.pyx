# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True
"""Cython kernel for Map.verifyLoS line-of-sight check.

Mirrors the Python implementation in ``leekwars/maps/map.py:verifyLoS``
line-by-line, with typed locals so Cython lowers the inner loops to C.

The wrapper in map.py prepares ``ignored_ids`` (a Python set of ints)
and the Map's ``coord`` 2D list, then delegates the heavy walking
work here. We don't handle the FIRST_IN_LINE area-attack pre-pass --
the wrapper falls back to the pure-Python verifyLoS for those.
"""
from libc.math cimport ceil, floor


def verify_los_kernel(int sx, int sy, int ex, int ey,
                      object ignored_ids,
                      list coord,
                      int min_x, int min_y,
                      int width, int height,
                      object entity_by_cell,
                      int start_id, int end_id):
    """Returns True if line of sight from (sx, sy) to (ex, ey) is clear.

    ``ignored_ids`` -- set of cell ids whose blocking is ignored.
    ``coord``       -- map.coord (2D list of Cell or None).
    ``entity_by_cell`` -- map.entityByCell.
    ``start_id``, ``end_id`` -- shortcuts used by the available()-failed branch.
    """
    cdef int a = ey - sy
    cdef int b = ex - sx
    if a < 0:
        a = -a
    if b < 0:
        b = -b
    cdef int dx_step = -1 if sx > ex else 1
    cdef int dy_step = 1 if sy < ey else -1

    # Build path: pairs of (start_y_offset, span). Same arithmetic as
    # the reference Python version, including the +-eps edge cases.
    cdef list path = []
    cdef int i, h
    cdef double d, y_val, ceil_y, floor_y
    if b == 0:
        path.append(0)
        path.append(a + 1)
    else:
        d = a / (<double>b) / 2.0
        h = 0
        for i in range(b):
            y_val = 0.5 + (i * 2 + 1) * d
            ceil_y = ceil(y_val - 0.00001)
            path.append(h)
            path.append(<int>ceil_y - h)
            floor_y = floor(y_val + 0.00001)
            h = <int>floor_y
        path.append(h)
        path.append(a + 1 - h)

    # Walk the line. Outer loop: each pair p (x-step). Inner loop: span
    # cells in the dy direction starting at path[p].
    cdef int n_pairs = len(path) // 2
    cdef int p, j
    cdef int span_start, span_count
    cdef int cell_x, cell_y, ix, iy
    cdef object cell, blocker
    cdef int cell_id

    for p in range(n_pairs):
        span_start = path[2 * p]
        span_count = path[2 * p + 1]
        cell_x = sx + p * dx_step
        ix = cell_x - min_x
        for j in range(span_count):
            cell_y = sy + (span_start + j) * dy_step
            iy = cell_y - min_y
            if not (0 <= ix < width):
                return False
            if not (0 <= iy < height):
                return False
            cell = coord[ix][iy]
            if cell is None:
                return False
            if not cell.walkable:
                return False
            blocker = entity_by_cell.get(cell)
            if blocker is not None:
                cell_id = cell.id
                if cell_id == start_id:
                    continue
                if cell_id == end_id:
                    return True
                if cell_id not in ignored_ids:
                    return False
    return True
