import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def natural_sort(list_to_sort):
    return sorted(list_to_sort, key=natural_keys)
