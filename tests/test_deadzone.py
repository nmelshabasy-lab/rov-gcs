from gcs.input.deadzone import apply_deadzone


def test_inside_deadzone_is_zero():
    assert apply_deadzone(0.05, 0.1) == 0.0
    assert apply_deadzone(-0.09, 0.1) == 0.0


def test_full_deflection_reaches_one():
    assert apply_deadzone(1.0, 0.1) == 1.0
    assert apply_deadzone(-1.0, 0.1) == -1.0


def test_sign_preserved():
    assert apply_deadzone(0.5, 0.1) > 0
    assert apply_deadzone(-0.5, 0.1) < 0
