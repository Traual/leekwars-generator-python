import re


_swear_words = set()
_replacements = ['*', '&', '@', '#', '!']


def set_swear_words(swear_words):
    global _swear_words
    _swear_words = swear_words


def get_replacement(fight, l: int) -> str:
    sb = []
    for i in range(l):
        sb.append(_replacements[fight.get_state().get_random().get_int(0, len(_replacements) - 1)])
    return ''.join(sb)


def check_string(fight, source: str) -> str:
    def replace(mr):
        word = mr.group()
        if word.lower() in _swear_words:
            return get_replacement(fight, len(word))
        else:
            return word
    return re.sub(r'\w+', replace, source, flags=re.UNICODE)
