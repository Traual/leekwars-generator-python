from .util.util import BLUE, GREEN, YELLOW, RED, END_COLOR


_enabled = False


def enable(enable_: bool) -> None:
    global _enabled
    _enabled = enable_


def i(tag: str, s: str) -> None:
    if _enabled:
        print("[" + BLUE + tag + END_COLOR + "] " + s)


def s(tag: str, msg: str) -> None:
    if _enabled:
        print("[" + GREEN + tag + END_COLOR + "] " + msg)


def w(tag: str, s: str) -> None:
    if _enabled:
        print("[" + YELLOW + tag + END_COLOR + "] " + s)


def e(tag: str, s: str) -> None:
    if _enabled:
        print("[" + RED + tag + END_COLOR + "] " + s)


def start(tag: str, s: str) -> None:
    if _enabled:
        print("[" + BLUE + tag + END_COLOR + "] " + s, end='')


def end(s: str = None) -> None:
    if _enabled:
        if s is None:
            print()
        else:
            print(s)
