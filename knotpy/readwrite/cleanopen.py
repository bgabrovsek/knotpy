import gzip
import bz2
from os.path import splitext
from pathlib import Path
from collections import defaultdict


# To handle new extensions, define data function accepting data `path` and `mode`.
# Then add the extension to _dispatch_dict.
fopeners = {
    ".gz": gzip.open,
    ".gzip": gzip.open,
    ".bz2": bz2.BZ2File,
}
_dispatch_dict = defaultdict(lambda: open, **fopeners)  # type: ignore


def prepend_to_extension(path, decoration=None):
    name, ext = splitext(path)
    if decoration is not None:
        path = name + "-" + str(decoration) + ext
    return path


def clean_open_file(path, mode="r"):
    """Ensure clean opening of files."""
    f = open(path, mode)
    return f


def clean_close_file(f):
    f.close()


