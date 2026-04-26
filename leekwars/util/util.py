import hashlib
import os


BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
END_COLOR = "\033[0m"


_primes = None


def is_prime(value: int) -> bool:
    global _primes
    if _primes is None:
        _primes = set([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691])
    return value in _primes


def get_hexa_color(color: int) -> str:
    retour = format(color & 0xFFFFFF, 'x')
    while len(retour) < 6:
        retour = "0" + retour
    return retour


def json_array_to_string_array(array):
    return [str(v) for v in array]


def save(data, file: str):
    try:
        with open(file, 'w', encoding='utf-8') as out:
            out.write(str(data))
    except Exception as e:
        import traceback
        traceback.print_exc()


def read_json_array(file: str):
    if not os.path.exists(file):
        return None
    try:
        with open(file, 'rb') as reader:
            data = reader.read()
        from .json_util import parse_array
        return parse_array(data.decode('utf-8'))
    except Exception:
        import traceback
        traceback.print_exc()
    return None


def sha1(data: str) -> str:
    try:
        m = hashlib.sha1()
        m.update(data.encode('utf-8'))
        return m.hexdigest()
    except Exception:
        return ""


def read_file(filepath: str) -> str:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError:
        import traceback
        traceback.print_exc()
        return ""


def write_file(data: str, file: str):
    try:
        with open(file, 'w', encoding='utf-8') as out:
            out.write(data)
    except Exception as e:
        print(e)
