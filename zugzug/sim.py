import itertools
import numbers
import random
import statistics
import tabulate
import typing

import tqdm  # type: ignore


__all__ = ['run']


PARAM = typing.Tuple[str, typing.Any]   # e.g ('n_gryphons', 2)
PARAMS = typing.Tuple[PARAM, ...]  # e.g. (('n_gryphons', 2), ('n_tracking', 1))
STATS = typing.Dict[PARAMS, typing.Dict[str, numbers.Number]]


def run(simulate: typing.Callable[..., numbers.Number], n=10_000, verbose = False, **params) -> str:
    """Runs a simulation function many and aggregates the results.

    Parameters:
        simulate: A user-defined function which outputs a number.
        n: The number of times to repeat the simulation.
        verbose: Whether or not to display progress.

    Returns:
        A table which summarizes the results from the simulation runs.

    """

    stats: STATS = {}

    for combo in tqdm.tqdm(list(expand_params(params)), position=0, disable=not verbose):
        results = [simulate(**dict(combo)) for _ in range(n)]
        stats[combo] = {
            'median': statistics.median_grouped(results),  # type: ignore
            'mean': statistics.mean(results),  # type: ignore
            'stdev': statistics.stdev(results)  # type: ignore
        }

    return fmt_stats(stats, tablefmt='fancy_grid')


def expand_params(params: typing.Dict[str, typing.List[typing.Any]]) -> typing.Iterator[PARAMS]:
    return itertools.product(*[[(p, v) for v in values] for p, values in params.items()])


def fmt_stats(stats: STATS, **kwargs) -> str:

    table = []

    for param in stats:
        row = [p[1] for p in param]
        row.extend(stats[param].values())
        table.append(row)

    param_names = [p[0] for p in list(stats.keys())[0]]
    stat_names = list(list(stats.values())[0].keys())
    headers = param_names + stat_names

    return tabulate.tabulate(table, headers=headers, **kwargs)
