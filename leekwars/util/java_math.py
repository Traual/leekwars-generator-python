"""Helpers reproducing Java numeric semantics that differ from Python.

Used pervasively in the engine because behaviour parity with the Java
generator is a hard requirement for deep-learning training.
"""

import math


def java_round(d: float) -> int:
    """Java's ``Math.round(double)``.

    Returns ``floor(d + 0.5)`` — rounds half **up** (toward +inf).
    Python's built-in ``round()`` uses banker's rounding (half-to-even),
    which produces different results on ``.5`` boundaries.
    """
    return int(math.floor(d + 0.5))


def java_div(a: int, b: int) -> int:
    """Java integer division: truncates toward zero (Python ``//`` rounds toward -inf)."""
    q, r = divmod(a, b)
    if r != 0 and (a < 0) != (b < 0):
        q += 1
    return q


def java_mod(a: int, b: int) -> int:
    """Java integer modulo: result has the dividend's sign (Python ``%`` differs)."""
    return a - java_div(a, b) * b


def java_long(n: int) -> int:
    """Wrap an unbounded Python int to signed 64-bit, matching Java ``long`` overflow."""
    return ((n + (1 << 63)) & ((1 << 64) - 1)) - (1 << 63)
