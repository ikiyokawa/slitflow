import numpy as np


class Loop(object):
    """Super class for loop generators.

    """

    def __init__(self, items):
        self.set_items(items)
        self.i = -1

    def __iter__(self):
        while True:
            self.i += 1
            if self.i >= len(self.items):
                self.i = 0
            yield self.items[self.i]

    def set_items(self, items):
        self.items = items


class NumberLoop(Loop):
    """Integer of float loop generator for matplotlib figure.

    """

    def set_items(self, items):
        self.items = []
        if type(items) in (int, float):
            self.items = [items]
        elif type(items) in (list, tuple):
            self.items = items


class ColorLoop(Loop):
    """RGB color generator for matplotlib figure.

    Args:
        colors (str): Name for edge and face color list.

    Returns:
        list of list of list: Nested list containing [list of RGB values for
        edge, list of RGB values for face]. RGB values should be [R(0-255),
        G(0-255), B(0-255)].
    """

    palette = {
        "small_pastel_edge":
        ((50, 170, 160), (220, 170, 0), (122, 12, 112)),
        "small_pastel_face":
        ((115, 195, 185), (252, 216, 0), (199, 111, 171)),
        "scatter_face":
        ((211, 13, 13), (1, 1, 203), (41, 161, 154), (145, 81, 201),
         (167, 140, 73)),
        "umap_face":
        ((200, 200, 200), (150, 0, 150), (0, 150, 0)),
        "umap_inv_face":
        ((200, 200, 200), (0, 150, 0), (150, 0, 150))}

    def set_items(self, items):
        self.items = []
        if items is None:
            self.items = [None]
        elif isinstance(items, str):
            if items in self.palette.keys():
                for item in self.palette[items]:
                    self.items.append(tuple(np.array(item) / 255))
            elif items == "None":
                self.items = ["None"]
            else:
                raise Exception(
                    "Default color name and hex code is \
                        not available currently.")
        elif type(items) in (list, tuple):
            if type(items[0]) in (int, float):  # single color
                self.items = [tuple(np.array(items) / 255)]
            else:  # multi color
                for item in items:
                    if item is None:
                        self.items.append(item)
                    elif item == "None":
                        self.items.append(item)
                    else:
                        self.items.append(tuple(np.array(item) / 255))


class LineStyleLoop(Loop):
    """Line style string generator for matplotlib figure.

    Args:
        styles (str or list): Style string for line style.

    Returns:
        list: Line style string generator
    """

    style_dict = {
        "densely dotted": (0, (1, 1)),
        "densely dashed": (0, (5, 1)),
        "densely dashdotted": (0, (3, 1, 1, 1)),
        "densely dashdotdotted": (0, (3, 1, 1, 1, 1, 1))}

    palette = {
        "default": ["solid",
                    style_dict["densely dashed"],
                    style_dict["densely dotted"],
                    style_dict["densely dashdotted"],
                    style_dict["densely dashdotdotted"]],
        "with_model3": ["solid",
                        style_dict["densely dashed"],
                        style_dict["densely dotted"],
                        "None", "None", "None"]}

    def set_items(self, items):
        self.items = []
        if items is None:
            self.items = [None]
        elif isinstance(items, str):
            if items in self.palette.keys():
                self.items = self.palette[items]
            else:
                self.items = [items]
        elif type(items) in (list, tuple):
            self.items = items


class MarkerStyleLoop(Loop):
    """Marker style string generator for matplotlib figure.

    Args:
        styles (str or list): Style string for marker style.

    Returns:
        list: Marker style string generator
    """

    palette = {"default": ["o", "s", "^", "x", "v"],
               "with_model3": ["None", "None", "None", "o", "s", "^"]}

    def set_items(self, items):
        self.items = []
        if items is None:
            self.items = [None]
        elif isinstance(items, str):
            if items in self.palette.keys():
                self.items = self.palette[items]
            else:
                self.items = [items]
        elif type(items) in (list, tuple):
            self.items = items
