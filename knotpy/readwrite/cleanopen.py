import gzip
import bz2
from os.path import splitext
from pathlib import Path
from collections import defaultdict


# To handle new extensions, define a function accepting a `path` and `mode`.
# Then add the extension to _dispatch_dict.
fopeners = {
    ".gz": gzip.open,
    ".gzip": gzip.open,
    ".bz2": bz2.BZ2File,
}
_dispatch_dict = defaultdict(lambda: open, **fopeners)  # type: ignore


def clean_open_file(path, mode="r", decorator=None):
    """Ensure clean opening of files."""

    name, ext = splitext(path)
    if decorator is not None:
        path = name + "-" + str(decorator) + ext

    f = open(path, mode)
    return f, path

def clean_close_file(f):
    f.close()


