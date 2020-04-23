import random
import typing

import zugzug as zz


class Game:

    def __init__(self, deck: typing.List[zz.cards.Card], wishlist=None, playlist=None):
        self.deck = deck
        self.wishlist = wishlist or []
        self.playlist = playlist or []

        self.health = 30
        self.hand: typing.List[zz.cards.Card] = []
        self.turn = 0
        self.max_mana = 0
        self.mana = 0

        # Shuffle the deck
        random.shuffle(self.deck)

        # Draw the first set of cards
        self.draw(n=3)

        # Apply mulligan if a wishlist is given
        if wishlist:
            self.mulligan(wishlist)

    def draw(self, n=1):
        self.hand.extend(self.deck[:n])
        del self.deck[:n]

    def mulligan(self, wishlist: typing.List[zz.cards.Card]):
        """

        References:
            1. [Mulligan article on Hearhstone Wiki](https://hearthstone.gamepedia.com/Mulligan)

        """

        # Determine which cards in hand can be kept and which can be discarded
        keep = []
        for card in wishlist:
            try:
                i = self.hand.index(card)
            except ValueError:
                continue
            keep.append(self.hand.pop(i))


        discard = self.hand
        self.hand = keep

        # No mulligan is necessary if the wishlist is satisfied
        if not discard:
            return

        # Draw new cards
        self.draw(n=len(discard))

        # Add the discarded cards to the deck and shuffle it
        self.deck.extend(discard)
        random.shuffle(self.deck)

    def next_turn(self):
        self.turn += 1
        self.max_mana = min(self.max_mana + 1, 10)
        self.mana = self.max_mana
        self.draw()

    def play_card(self, card: zz.cards.Card):
        self.hand.remove(card)
        self.mana -= card.mana
        card(self)

    def play_until(self, condition: zz.Condition):

        self.next_turn()

        if condition(self):
            return

        for card in self.playlist:

            if card in self.hand and self.mana >= card.mana:
                self.play_card(card)

                if condition(self):
                    return

        # Recurse
        self.play_until(condition)
