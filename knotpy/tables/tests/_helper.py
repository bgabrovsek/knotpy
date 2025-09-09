import os, uuid

_REMOVE_FILES_AFTER_TEST = True

_unique = uuid.uuid4().hex[:8]

def _safe_delete_file(filename):
    try:
        assert os.path.isfile(filename), f"{filename} was not created"
    finally:
        if _REMOVE_FILES_AFTER_TEST:
            if os.path.exists(filename):
                os.remove(filename)


