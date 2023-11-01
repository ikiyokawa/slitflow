import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def natural_sort(list_to_sort):
    return sorted(list_to_sort, key=natural_keys)


def ordered_union(lists):
    result = []
    for lst in lists:
        for item in lst:
            if item not in result:
                result.append(item)
    return result


def ordered_intersection(lists):
    result = lists[0]
    for lst in lists[1:]:
        result = [item for item in result if item in lst]
    return result
