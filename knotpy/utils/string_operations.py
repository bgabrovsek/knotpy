import re


__all__ = ['multi_replace']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def multi_replace(s: str, replacements: dict) -> str:
    """Performs multiple string replacements
    :param s: input string
    :param replacements: dictionary of string replacements
    :return: string with replacements
    """

    rep = dict((re.escape(k), v) for k, v in replacements.items())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], s)