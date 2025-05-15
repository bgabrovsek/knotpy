import knotpy as kp

def test_settings_descriptor():

    old_arm = list(kp.settings.allowed_moves)
    kp.settings.allowed_moves = "r1,r2"
    assert set(kp.settings.allowed_moves) == {"R1", "R2"}

    kp.settings.allowed_moves = old_arm
    assert kp.settings.allowed_moves is not old_arm
    assert set(kp.settings.allowed_moves) == set(old_arm)

    kp.settings.trace_moves = True
    assert kp.settings.trace_moves == True
    kp.settings.trace_moves = False
    assert kp.settings.trace_moves == False


if __name__ == '__main__':
    test_settings_descriptor()