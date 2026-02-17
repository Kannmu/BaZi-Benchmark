from bazibench.core import constants


def test_constants_basic():
    assert len(constants.TIANGAN) == 10
    assert len(constants.DIZHI) == 12
    assert constants.WU_HU_DUN["甲"] == "丙"
    assert constants.WU_SHU_DUN["甲"] == "甲"


def test_rules_presence():
    assert ("子", "丑") in constants.LIU_HE
    assert ("子", "午") in constants.LIU_CHONG
    assert ("申", "子", "辰") in constants.SAN_HE
    assert ("寅", "巳", "申") in constants.XING
