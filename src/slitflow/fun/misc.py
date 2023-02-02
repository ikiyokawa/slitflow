def reduce_list(names):
    """Return string if len(list) == 1 to avoid pandas warning.

    df.groupby(["a"]) returns warning. To avoid this, input should be
    df.groupby("a"). This function can be used as follows:

    .. code-block:: python

        from fun.misc import reduce_list as rl
        df.groupby(rl(["a"]))

    Args:
        names (list): List of string.

    Returns:
        list or str: String if len(list) == 1
    """
    if len(names) == 1:
        return names[0]
    else:
        return names
