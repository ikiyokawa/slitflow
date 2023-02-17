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

    Args:
        numbers (int or float or list): Numbers for style loop.

    Yields:
        int or float: The next number in the range of numbers
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
        colors (str or list): Name for edge or face color list.
            If list of int, this always returns a list which is
            it divided by 255.

            If list of list of int, this returns a list which is
            a element of it divided by 255 in order.

            If list of str, this returns a list which is a element of
            a palette registered in this class divided by 255 in order.

            TODO: Future plan
            (If list of (palette, list of int), where type(palette) belong to
            above three, this creates a new palette by patch-working palettes
            in the list, and returns a list according to the palette.
            e.g, [([0,0,0], [1,2]), ([[1,1,1], [2,2,2]], 4)] let create
            a new palette [[1,1,1], [0,0,0], [0,0,0], [2,2,2]].)

    Yields:
        list of float: The next RGB values. RGB values should be [R(0-1),
        G(0-1), B(0-1)]
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

    Yields:
        str: The next style string
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

    Yields:
        str: The next marker style string
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
