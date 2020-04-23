import collections

import zugzug as zz


def test_mulligan():

    game = zz.Game(deck=[])
    game.hand = [zz.cards.Wisp, zz.cards.Wisp, zz.cards.ScavengersIngenuity]
    game.deck = [zz.cards.ScavengersIngenuity, zz.cards.Zixor, zz.cards.Wisp]

    game.mulligan(wishlist=[zz.cards.ScavengersIngenuity, zz.cards.Zixor])

    expected = [zz.cards.ScavengersIngenuity, zz.cards.Zixor, zz.cards.ScavengersIngenuity]
    assert collections.Counter(game.hand) == collections.Counter(expected)
