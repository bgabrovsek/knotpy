import re
import string

__all__ = ["abcABC", 'multi_replace']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


abcABC = string.ascii_lowercase + string.ascii_uppercase  # this is already in from string import ascii_letters

# def multi_replace(s: str, replacements: dict) -> str:
#     """Performs multiple string replacements
#     :param s: input string
#     :param replacements: dictionary of string replacements
#     :return: string with replacements
#     """
#
#     rep = dict((re.escape(k), v) for k, v in replacements.items())
#     pattern = re.compile("|".join(rep.keys()))
#     return pattern.sub(lambda m: rep[re.escape(m.group(0))], s)


def multi_replace(text, *replacements):
    """Replace substrings with other strings, until there are no substrings left.
    :param text: input string
    :param replacements: list of tuples or dicts
    :return: replaced string

    Example:
    multi_replace("AAAABC", ("AA", "a"), "Bb", {"C": "c"})
    returns
    "abc"
    """
    for repl in replacements:
        if isinstance(repl, dict):
            for key, val in repl.items():
                while key in text:
                    text = text.replace(key, val)
        else:
            key, val = repl[0], repl[1]
            while key in text:
                text = text.replace(key, val)
    return text

#print(multi_replace("AAAABC", ("AA", "A"), "Bb", {"C": "c"}))


def nested_split(text: str, max_depth=None) -> list:
    """ Splits a string into a list of lists.
    Example: "a,(b,c,(d,e))" -> ['a', ['b', 'c', ['d', 'e']]]
    :param text: string list
    :param max_depth:
    :return: list of lists
    """

    if max_depth is None:
        max_depth = 10000

    # clean up string
    text = text.strip()
    while "  " in text:
        text = text.replace("  ", " ")
    #text = multi_replace(text, {";": ",", "(": "[", ")": "]"})
    text = text.replace(";", ",")
    text = text.replace(", ", ",")
    text = text.replace(" ", ",")

    pattern = re.compile(r"(,|\[|\]|\(|\))")  # split by ",", "[", and "]", TODO: fix RE

    list_stack = [[]]  # if item  starts by [({, we add a sublist to the stack

    for item in pattern.split(text):
        if not len(item) or item == ",":
            continue
        if item == "[" or item == "(":
            list_stack[-1].append(list())
            list_stack.append(list_stack[-1][-1])
        elif item == "]" or item == ")":
            list_stack.pop()
        else:
            list_stack[-1].append(item)

    return list_stack[0]


def string_to_nested_tuple_with_prefixes(text: str, default_prefix=None):
    """Turns a string containing elements to a sequence of tuples
    E.g. X[1, 9, 2, 8], X[3, 10, 4, 11] -> (("X",(1,9,2,8),...)
    [[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]] -> ((default_prefix, (4,2,5,1)), ...)
    """
    text = multi_replace(
        text,{
            ")": "]",
            "(": "[",
            " ": "",
            ";": ","
        }
    )

    if (len(text) >= 1 and text[0] != "[") :#or (len(text) >= 2 and text[:2] != "[["):
        text = "[" + text + "]"

    print(text)
#
#
# string_to_nested_tuple_with_prefixes("X[1, 9, 2, 8], X[3, 10, 4, 11]")
# string_to_nested_tuple_with_prefixes("[[4,2,   5,1],  [8,6,1,5],[6,3,7,4],[2,7,3,8]]")
# string_to_nested_tuple_with_prefixes("(X[1, 9, 2, 8], X[3, 10, 4, 11])")
# string_to_nested_tuple_with_prefixes("[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]")
#
# exit()

def _test():
    print(nested_split("v    c  (8,   9,([9],0,1)) (8,9,0)"))


if __name__ == "__main__":
    _test()
