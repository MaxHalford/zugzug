# zugzug

This is a little framework to answer statistical questions related to [Hearthstone](https://playhearthstone.com). Things started when I wrote an analysis that gathered some interest [on reddit](https://www.reddit.com/r/CompetitiveHS/comments/g1tqj0/analyzing_the_time_it_takes_to_summon_zixor_prime/). I then looked into doing some more analysis but noticed that I was doing a lot of copy/pasting. I then decided to write some helpers to avoid repeating myself and make less mistakes.

Many Hearthstone questions can probably be answered with exact formulas. However, that may involve brain power that you might want to invest elsewhere. An alternative solution is to approach the exact answer by running multiple simulations and aggregating the results. Essentially, `zugzug` is a tool that helps you perform so-called [Monte Carlo experiments](https://www.wikiwand.com/en/Monte_Carlo_method). The user provides a simulation function, which takes various parameters as inputs and outputs a number. Then, the user calls `zugzug`'s `run` function and specifies a grid of parameters. The results are then aggregated and displayed in a table.

Various utilities such as cards, conditions, and game mechanisms are implemented in `zugzug` to help out writing simulation functions. These utilities are implemented on an as-needed basis. Therefore, not all of them are available. However, new features and specific requests are more than welcome to be discussed. Likewise, the API is highly succeptible to change.

## Installation

```sh
pip install git+https://github.com/MaxHalford/zugzug
```

## Examples

**What is the probability of having a 1 mana card at the first turn?**

We first import `zugzug`.

```py
>>> import zugzug as zz

```

Reproducibility can be enforced by fixing the global random number generator.

```py
>>> import random
>>> random.seed(42)

```

For this analysis, we're not interested in any card in particular. Instead, we are interested by the mana cost of each cost. We can thus define two kinds of cards, one that costs 1 mana and 1 that costs 2 mana.

```py
>>> one_mana_card = zz.cards.Card(name='1 Mana Card', mana=1)
>>> two_mana_card = zz.cards.Card(name='2 Mana Card', mana=2)

```

Let us now define a simulation function. One parameter will determine one many 1 mana cards are in the deck, whilst the other will indicate if we're looking for 1 mana cards during the mulligan phase or not. The details of the simulation are influenced by these two parameters. We'll output a boolean value which tells whether or not a 1 mana card is in hand.

```py
>>> def sim(n_ones, mulligan):
...
...     # Create a deck with 1 and 2 mana cards
...     deck = [one_mana_card] * n_ones + [two_mana_card] * (30 - n_ones)
...
...     # Indicate that we want to fish for 1 mana cards during the mulligan phase
...     wishlist = [one_mana_card] * 3 if mulligan else []
...     game = zz.Game(deck, wishlist=wishlist)
...
...     # Go to the first turn
...     game.next_turn()
...
...     return one_mana_card in game.hand

```

We may now call the `run` function by providing it with the simulation function. We'll also choose how many repetitions we want to do and a set of values for each parameter. The rest is taken care by `zugzug`.

```py
>>> results = zz.run(sim, n=1000, n_ones=range(1, 7), mulligan=[False, True])
>>> print(results)
╒══════════╤════════════╤═══════════╤════════╤══════════╕
│   n_ones │ mulligan   │    median │   mean │    stdev │
╞══════════╪════════════╪═══════════╪════════╪══════════╡
│        1 │ False      │ 0.0733945 │  0.128 │ 0.334257 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        1 │ True       │ 0.15445   │  0.236 │ 0.424835 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        2 │ False      │ 0.171141  │  0.255 │ 0.436079 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        2 │ True       │ 0.33612   │  0.402 │ 0.490547 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        3 │ False      │ 0.293651  │  0.37  │ 0.483046 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        3 │ True       │ 0.595841  │  0.553 │ 0.497432 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        4 │ False      │ 0.402527  │  0.446 │ 0.497324 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        4 │ True       │ 0.760355  │  0.676 │ 0.468234 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        5 │ False      │ 0.589253  │  0.549 │ 0.497842 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        5 │ True       │ 0.826146  │  0.742 │ 0.437753 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        6 │ False      │ 0.702552  │  0.627 │ 0.483844 │
├──────────┼────────────┼───────────┼────────┼──────────┤
│        6 │ True       │ 0.87578   │  0.801 │ 0.399448 │
╘══════════╧════════════╧═══════════╧════════╧══════════╛

```

**How much mana does [Frizz Kindleroost](https://hearthstone.gamepedia.com/Frizz_Kindleroost) save?**

Summoning Frizz Kindleroot reduces the mana cost of each dragon in the deck by 2. To measure how much mana this saves on average, we can run a simulation where the turns go by as long as Frizz is not in hand. We can do this by calling `game.play_until` with the `zz.conditions.Playable(frizz)` condition.

```py
>>> import random
>>> import zugzug as zz

>>> random.seed(42)

>>> dragon = zz.cards.Minion(name='Dragon', mana=None, race=zz.races.DRAGON)
>>> frizz = zz.cards.FrizzKindleroost()

>>> def sim(mulligan, n_dragons):
...
...     deck = [frizz] + [dragon] * n_dragons
...     deck = deck + [zz.cards.Wisp()] * (30 - len(deck))
...     game = zz.Game(deck, wishlist=[frizz] if mulligan else [])
...
...     game.play_until(zz.conditions.Playable(frizz))
...
...     return sum(2 for card in game.deck if card == dragon)

>>> results = zz.run(sim, n=1000, mulligan=[False, True], n_dragons=[2, 4, 6, 8, 10, 12])
>>> print(results)
╒════════════╤═════════════╤══════════╤════════╤═════════╕
│ mulligan   │   n_dragons │   median │   mean │   stdev │
╞════════════╪═════════════╪══════════╪════════╪═════════╡
│ False      │           2 │  1.93236 │  1.898 │ 1.5761  │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ False      │           4 │  3.90851 │  3.7   │ 2.6178  │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ False      │           6 │  5.98276 │  5.728 │ 3.76034 │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ False      │           8 │  8.03237 │  7.678 │ 4.73653 │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ False      │          10 │ 10.1261  │  9.72  │ 5.68805 │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ False      │          12 │ 12.0412  │ 11.724 │ 6.57381 │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ True       │           2 │  2.02603 │  2.038 │ 1.59408 │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ True       │           4 │  4.07219 │  3.948 │ 2.79376 │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ True       │           6 │  6.28    │  6.12  │ 3.74802 │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ True       │           8 │  9.52564 │  8.224 │ 4.74514 │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ True       │          10 │ 11.5612  │ 10.298 │ 5.81214 │
├────────────┼─────────────┼──────────┼────────┼─────────┤
│ True       │          12 │ 13.8684  │ 12.224 │ 6.94997 │
╘════════════╧═════════════╧══════════╧════════╧═════════╛

```

**How long does it take to get [Zixor Prime](https://hearthstone.gamepedia.com/Zixor_Prime) in hand?**

This was the first analysis I did. You can see the code I used in [this gist](https://gist.github.com/MaxHalford/0bf06078d2dd6ef3609f4e3cca5bc41c). Using `zugzug` reduces the amount of necessary of code and helps a bit with readability. It also helped me gain trust in my analysis by delegating the game mechanics to `zugzug`.

This simulation is a bit more verbose than the previous ones because their are two first phases involved. First of all we need to wait that Zixor is in hand. Then, once Zixor's deathrattle has triggered, we have to wait to draw Zixor Prime. The goal of this analysis is to study the impact of draw cards such as [Diving Gryphon](https://www.hearthpwn.com/cards/151350-diving-gryphon), [Scavenger's Ingenuity](https://www.hearthpwn.com/cards/210658-scavengers-ingenuity), and [Tracking](https://hearthstone.gamepedia.com/Tracking).

```py
>>> import random
>>> import zugzug as zz

>>> random.seed(42)

>>> zixor = zz.cards.Zixor()
>>> zixor_prime = zz.cards.ZixorPrime()
>>> gryphon = zz.cards.DivingGryphon()
>>> si = zz.cards.ScavengersIngenuity()
>>> tracking = zz.cards.Tracking(zixor_prime, zixor, si, gryphon)
>>> tracking.wishlist.append(tracking)
>>> wisp = zz.cards.Wisp()

>>> playlist = [si, gryphon, tracking]
>>> wishlist = [zixor, si, gryphon, tracking]

>>> def sim(n_gryphons, n_si, n_tracking):
...
...     deck = (
...         [zixor] +
...         [gryphon] * n_gryphons +
...         [si] * n_si +
...         [tracking] * n_tracking +
...         [wisp] * (30 - 1 - n_gryphons - n_si - n_tracking)
...     )
...     game = zz.Game(deck, wishlist=wishlist, playlist=playlist)
...
...     # Play until Zixor is playable
...     game.play_until(zz.conditions.Playable(zixor))
...
...     # Assume it takes 0 to 2 turns to get Zixor killed
...     for _ in range(random.randint(0, 2)):
...         game.next_turn()
...
...     # Insert Zixor Prime into the deck once Zixor's deathrattle triggers
...     game.play_card(zixor)
...
...     # Wait until Zixor Prime is playable
...     game.play_until(zz.conditions.Playable(zixor_prime))
...
...     return game.turn

>>> results = zz.run(
...     sim, n=1000,
...     n_gryphons=[0, 1, 2],
...     n_si=[0, 1, 2],
...     n_tracking=[0, 1, 2]
... )
>>> print(results)
╒══════════════╤════════╤══════════════╤══════════╤════════╤═════════╕
│   n_gryphons │   n_si │   n_tracking │   median │   mean │   stdev │
╞══════════════╪════════╪══════════════╪══════════╪════════╪═════════╡
│            0 │      0 │            0 │ 22.7881  │ 21     │ 6.45024 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            0 │      0 │            1 │ 19.7245  │ 18.687 │ 5.65376 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            0 │      0 │            2 │ 17.959   │ 16.835 │ 4.97056 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            0 │      1 │            0 │ 16.3727  │ 16.652 │ 6.19462 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            0 │      1 │            1 │ 15.2869  │ 15.328 │ 5.3125  │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            0 │      1 │            2 │ 13.6     │ 13.836 │ 4.43517 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            0 │      2 │            0 │ 11.4167  │ 12.864 │ 4.98481 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            0 │      2 │            1 │ 10.7182  │ 12.204 │ 4.35814 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            0 │      2 │            2 │  9.76364 │ 11.118 │ 3.61623 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            1 │      0 │            0 │ 16.5435  │ 16.481 │ 6.1929  │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            1 │      0 │            1 │ 15.1866  │ 15.239 │ 5.34588 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            1 │      0 │            2 │ 13.0821  │ 13.556 │ 4.74694 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            1 │      1 │            0 │ 11.4     │ 13.165 │ 5.41434 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            1 │      1 │            1 │ 10.7222  │ 12.243 │ 4.57109 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            1 │      1 │            2 │  9.48864 │ 11.186 │ 3.80866 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            1 │      2 │            0 │  8.91096 │ 10.991 │ 4.01036 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            1 │      2 │            1 │  8.47466 │ 10.254 │ 3.19683 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            1 │      2 │            2 │  8.35616 │  9.604 │ 2.60845 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            2 │      0 │            0 │ 11.8519  │ 13.515 │ 5.63556 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            2 │      0 │            1 │ 11.1833  │ 12.664 │ 4.79897 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            2 │      0 │            2 │  9.51818 │ 11.342 │ 3.88692 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            2 │      1 │            0 │  9.30172 │ 11.208 │ 4.12065 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            2 │      1 │            1 │  8.75954 │ 10.536 │ 3.56559 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            2 │      1 │            2 │  8.47466 │  9.96  │ 2.95112 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            2 │      2 │            0 │  8.4311  │  9.948 │ 3.02795 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            2 │      2 │            1 │  8.33056 │  9.391 │ 2.44256 │
├──────────────┼────────┼──────────────┼──────────┼────────┼─────────┤
│            2 │      2 │            2 │  8.28616 │  9.138 │ 2.1353  │
╘══════════════╧════════╧══════════════╧══════════╧════════╧═════════╛

```

**What is the likelihood of having [Scalerider](https://hearthstone.gamepedia.com/Scalerider) in hand without a dragon?**

To do.

## Development

I don't expect anyone else to use this code but you never know. Here are the steps you'll want to follow:

```sh
$ python3 -m venv .
$ source ./bin/activate
$ pip install -e ".[dev]"
$ python3 setup.py develop
```

You can run tests with `pytest` and `mypy`.

## License

Licensed under the [WTFPL](http://www.wtfpl.net/).
