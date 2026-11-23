"""Dead-zone for analogue axes."""


def apply_deadzone(value, deadzone=0.1):
    """Return 0 inside the dead-zone; outside, rescale so output still reaches +/-1."""
    if abs(value) < deadzone:
        return 0.0
    sign = 1.0 if value > 0 else -1.0
    scaled = (abs(value) - deadzone) / (1.0 - deadzone)
    return sign * min(scaled, 1.0)
