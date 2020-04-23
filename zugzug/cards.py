from __future__ import annotations

import random
import typing

import zugzug as zz


__all__ = ['Minion', 'Spell']


class Card:

    def __init__(self, name: str, mana: int, race: str = None, abilities: typing.List[str] = None):
        self.name = name
        self.mana = mana
        self.race = race
        self.abilities = abilities or []

    def __call__(self, game: zz.Game):
        """Does something when the card is used."""
        pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self):
        return self.name


class Minion(Card):

    def __init__(self, name, mana, race=None, abilities=None):
        super().__init__(name=name, mana=mana)
        self.race = race
        self.abilities = abilities or []


class AngryChicken(Minion):

    def __init__(self):
        super().__init__(name='Angry Chicken', mana=2)


class DivingGryphon(Minion):

    def __init__(self):
        super().__init__(name='Diving Gryphon', mana=4, race=zz.races.BEAST,
                         abilities=[zz.abilities.RUSH])

    def __call__(self, game):
        rushers = [
            i for i, card in enumerate(game.deck)
            if isinstance(card, Minion) and zz.abilities.RUSH in card.abilities
        ]
        if rushers:
            i = random.choice(rushers)
            game.hand.append(game.deck.pop(i))


class FrizzKindleroost(Minion):

    def __init__(self):
        super().__init__(name='Frizz Kindleroost', mana=4)


class Scalerider(Minion):

    def __init__(self):
        super().__init__(name='Scalerider', mana=3)


class Wisp(Minion):

    def __init__(self):
        super().__init__(name='Wisp', mana=0)


class Zixor(Minion):

    def __init__(self):
        super().__init__(name='Zixor, Apex Predator', mana=3, race=zz.races.BEAST,
                         abilities=[zz.abilities.RUSH])

    def __call__(self, game):
        i = random.randint(0, len(game.deck))
        game.deck.insert(i, ZixorPrime())


class ZixorPrime(Minion):

    def __init__(self):
        super().__init__(name='Zixor Prime', mana=8, race=zz.races.BEAST,
                         abilities=[zz.abilities.RUSH])


class Spell(Card):
    pass


class ScavengersIngenuity(Spell):

    def __init__(self):
        self.name = "Scavenger's Ingenuity"
        self.mana = 2

    def __call__(self, game):
        beasts = [
            i for i, card in enumerate(game.deck)
            if isinstance(card, Minion) and card.race == zz.races.BEAST
        ]
        if beasts:
            i = random.choice(beasts)
            game.hand.append(game.deck.pop(i))


class Tracking(Spell):

    def __init__(self, *wishlist: typing.List[zz.cards.Card]):
        self.name = 'Tracking'
        self.mana = 1
        self.wishlist = list(wishlist)

    def __call__(self, game):
        next_3, game.deck = game.deck[:3], game.deck[3:]

        if not next_3:
            return

        for card in self.wishlist:
            if card in next_3:
                game.hand.append(card)
                return

        # If no tracked card was in the wish list then we pick one at random
        game.hand.append(random.choice(next_3))
