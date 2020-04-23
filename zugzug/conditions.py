from __future__ import annotations

import abc
import collections

import zugzug as zz


__all__ = [
    'InHand',
    'EnoughMana',
    'Playable'
]


class Condition(abc.ABC):

    @abc.abstractmethod
    def __call__(self, game: zz.Game) -> bool:
        """Look at the current game state and check if a condition is verified or not."""

    def __and__(self, other: Condition) -> Condition:
        return Conjunction(self, other)

    def __or__(self, other: Condition) -> Condition:
        return Disjunction(self, other)

    def __invert__(self) -> Condition:
        return Negation(self)


class Conjunction(Condition):

    def __init__(self, a: Condition, b: Condition):
        self.a = a
        self.b = b

    def __call__(self, game: zz.Game) -> bool:
        return self.a(game) and self.b(game)


class Disjunction(Condition):

    def __init__(self, a: Condition, b: Condition):
        self.a = a
        self.b = b

    def __call__(self, game: zz.Game) -> bool:
        return self.a(game) or self.b(game)


class Negation(Condition):

    def __init__(self, c: Condition):
        self.c = c

    def __call__(self, game: zz.Game) -> bool:
        return not self.c(game)


class InHand(Condition):

    def __init__(self, card: zz.cards.Card):
        self.card = card

    def __call__(self, game: zz.Game) -> bool:
        return self.card in game.hand


class EnoughMana(Condition):

    def __init__(self, card: zz.cards.Card):
        self.card = card

    def __call__(self, game: zz.Game) -> bool:
        return game.mana >= self.card.mana


class Playable(Conjunction):

    def __init__(self, card):
        super().__init__(InHand(card), EnoughMana(card))
