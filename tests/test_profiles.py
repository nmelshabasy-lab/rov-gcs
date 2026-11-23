import json

from gcs.input.profiles import ProfileManager


def make(tmp_path):
    p = tmp_path / "p.json"
    p.write_text(json.dumps({
        "controller_profiles": {"Pad X": "x"},
        "profiles": {"default": {"axes": {}}, "x": {"axes": {"0": "yaw"}}},
    }))
    return ProfileManager(str(p))


def test_auto_select_by_controller(tmp_path):
    name, prof = make(tmp_path).for_controller("Pad X")
    assert name == "x" and prof["axes"]["0"] == "yaw"


def test_unknown_controller_uses_default(tmp_path):
    name, _ = make(tmp_path).for_controller("Mystery")
    assert name == "default"


def test_save_and_reload(tmp_path):
    pm = make(tmp_path)
    pm.set_profile("new", {"axes": {"1": "surge"}})
    pm.save()
    assert "new" in ProfileManager(pm.path).names()
