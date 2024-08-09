


# Example usage:
mls = MultiLevelSet()
mls[0] = "a"
mls[1] = "b"
mls[1] = "a"  # This should be ignored
mls[2] = "c"
mls[2] = "w"
mls[2] = "b"  # This should be ignored
print(mls)