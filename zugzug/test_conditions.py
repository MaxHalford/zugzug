import zugzug as zz


def test_conjunction():

    c = zz.conditions.InHand(1) & zz.conditions.InHand(2)
    assert isinstance(c, zz.conditions.Conjunction)
