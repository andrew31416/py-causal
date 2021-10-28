from typing import List


from itertools import product


def get_combinations(items: List):
    """
    Returns a list of all combinations of items in the supplied list.

    Keyword arguments
    -----------------
    items: List -- a list of items

    Returns
    -------
    List[List]
    """

    res = list(product(*[[[], [_n]] for _n in items]))

    def _parse(inputs):
        out = []
        for _x in inputs:
            out+=_x
        return out
    # convert to list of list
    res = list(map(_parse, res))

    # remove empty lists
    return [_x for _x in res if len(_x)>0]
