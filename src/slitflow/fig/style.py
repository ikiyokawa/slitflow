import numpy as np
import matplotlib as mpl
import matplotlib.font_manager as font_manager
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt

from .figure import Figure
from ..fun.palette import NumberLoop, ColorLoop, LineStyleLoop, MarkerStyleLoop
from .. import setreqs

CM = 1 / 2.54
FONT_SIZE = 6
LINE_SIZE = 0.5
FONT_FAMILY = "Arial"


class Basic(Figure):
    """Basic figure style for A4 paper size.

    This class is valid only if there is only one axes in Figure.
    This class is used to change matplotlib's figure format in a convenient
    way. The default setting is to create a quarter-width square graphic image
    on an A4 size document.

    Args:
        reqs[0] (Figure): Figure class object.
        param["size"] (list of float, optional): [width, height] of figure
            image (cm). Defaults to [4.5, 4.5].
        param["margin"] (list of float, optional): [left, bottom, right, top]
            of figure margin (cm). Defaults to [0.9, 0.6, 0.1, 0.4].
        param["limit"] (list of float, optional): [x_lower, x_upper,
            y_lower, y_upper] limits of figure. If x_lower = None, skip
            X limits.
        param["tick"] (list of list of float, optional): Tick position
            float lists for X and Y axes. :class:`numpy.ndarray` is available,
            e.g., [np.arange(0, 1, 0.1), [0, 1, 2]].
        param["tick_label"] (list of list of str, optional): Tick label for
            [x-axis, y-axis].
        param["format"] (list of str, optional): Strings for X and tick
            formats, e.g. ["%.0f","%.1f"].
        param["is_box"] (bool, optional): Draw box lined axis, if True.
        param["line_widths"] (float or list of float, optional): Line width.
            Defaults to 1.
        param["line_styles"] (str or list of str, optional): Line style.
        param["line_colors"] (list of RGB 0-255, optional): Line color. e.g.,
            [[0, 0, 255]] is blue. Palette name is also available.
        param["error_thicknesses"] (list of float, optional): Error bar line
            width. Defaults to 1.
        param["error_line_styles"] (list of str, optional): Error bar line
            style.
        param["error_cap_sizes"] (list of float, optional): Error bar
            cap line width.
        param["marker_styles"] (str or list of str, optional): Marker style.
        param["marker_colors"] (list of list of RGB 0-255, optional): Marker
            edge and face colors. e.g., [[[0,0,0]],[[100,100,100]]].
            List of palette_name is also available.
        param["marker_widths"] (float or list of float, optional): Marker
            widths.
        param["marker_sizes"] (float or list of float, optional): Marker sizes.
        param["bar_widths"] (float or list of float): Width of each bar.
        param["label"] (list of str, optional): [X label string, Y label
            string] for axes label texts.
        param["legend"] (list, optional): [list of label strings, handle
            indexes of artists to create a legend, keyword arguments for
            matplotlib legend]. If [None, None], then delete all legends. If
            handle indexes are None, e.g. [["Label1", "Label2"], None] then
            create legend for all artists. If only handle indexes are
            specified, e.g. [None, [0,1]], then create legend for selected
            artists with existing labels. Keyword arguments should be
            dictionary, e.g. {"loc": "center"}.
        param["log_scale"](list of bool): Change axes to the log scale. e.g.,
            [False, True] means that the only y-axis is the log scale.
        param["title"] (str, optional): String for the figure title.
        param["clim"] (list of float, optional): [vmin, vmax] of colormap
            limit.
        param["cmap"] (str, optional): Colormap name. See also
            `matplotlib.colormaps <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_.

    Returns:
        Figure: Styled Figure object
    """

    def save_data(self, data, path):
        """
        :func:`matplotlib.pyplot.clf` is removed to avoid deleting the final
        :class:`matplotlib.figure.Figure` object.
        """
        super(Figure, self).save_data(data, path)

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.delete_param("size")
        self.info.set_split_depth(self.reqs[0].info.split_depth())

        if "size" not in param:
            param["size"] = [4.5, 4.5]
        self.info.add_param(
            "size", param["size"], "list of cm",
            "[width, height] of figure size")
        if "margin" not in param:
            param["margin"] = [0.9, 0.6, 0.1, 0.4]
        self.info.add_param(
            "margin", param["margin"], "list of cm",
            "[left, bottom, right, top] of figure margin (cm)")
        if "limit" in param:
            self.info.add_param(
                "limit", param["limit"], "list of float",
                "[x_lower, x_upper, y_lower, y_upper] limits of figure")
        if "tick" in param:
            x_tick = param["tick"][0]
            if type(x_tick).__module__ == np.__name__:
                x_tick = x_tick.tolist()
            y_tick = param["tick"][1]
            if type(y_tick).__module__ == np.__name__:
                y_tick = y_tick.tolist()
            self.info.add_param(
                "tick", [x_tick, y_tick], "list of float", "[x, y] of tick")
        if "tick_label" in param:
            self.info.add_param(
                "tick_label", param["tick_label"], "list",
                "[x, y] of tick label")
        if "is_box" in param:
            self.info.add_param(
                "is_box", param["is_box"], "bool", "Whether to write box axis")
        if "label" in param:
            self.info.add_param(
                "label", param["label"], "list of str",
                "[x, y] of label string")
        if "format" in param:
            self.info.add_param(
                "format", param["format"], "list of str",
                "[x, y] of tick format string")
        if "line_widths" not in param:
            param["line_widths"] = 1
        self.info.add_param(
            "line_widths", param["line_widths"], "float or list of float",
            "Line widths")
        if "line_styles" in param:
            self.info.add_param(
                "line_styles", param["line_styles"], "list of str",
                "Line styles")
        if "line_colors" in param:
            self.info.add_param(
                "line_colors", param["line_colors"], "list of RGB 0-255",
                "Line colors")
        if "bar_widths" in param:
            self.info.add_param(
                "bar_widths", param["bar_widths"], "float or list of float",
                "Width of each bar")

        if "error_thicknesses" not in param:
            param["error_thicknesses"] = 1
        self.info.add_param(
            "error_thicknesses", param["error_thicknesses"], "list of float",
            "Error bar line widths")
        if "error_line_styles" in param:
            self.info.add_param(
                "error_line_styles", param["error_line_styles"], "list of str",
                "Error bar line styles")
        if "error_colors" in param:
            self.info.add_param(
                "error_colors", param["error_colors"],
                "list of RGB 0-255", "Error bar range line colors")
        if "error_cap_sizes" in param:
            self.info.add_param(
                "error_cap_sizes", param["error_cap_sizes"],
                "list of float", "Error bar cap sizes")

        if "marker_styles" in param:
            self.info.add_param(
                "marker_styles", param["marker_styles"], "list of str",
                "Marker styles")
        if "marker_sizes" in param:
            self.info.add_param(
                "marker_sizes", param["marker_sizes"], "list of float",
                "Marker size")
        if "marker_colors" in param:
            self.info.add_param(
                "marker_colors", param["marker_colors"], "list of list of\
                RGB 0-255", "Marker edge and face colors")
        if "marker_widths" in param:
            self.info.add_param(
                "marker_widths", param["marker_widths"], "list of float",
                "Marker line width")

        if "legend" in param:
            self.info.add_param(
                "legend", param["legend"], "list",
                "Legend [list of label string, indexes of artist handles,\
                    keyword arguments]")
        if "title" in param:
            self.info.add_param(
                "title", param["title"], "str", "Title of figure")
        if "log_scale" in param:
            self.info.add_param(
                "log_scale", param["log_scale"], "list of bool",
                "[x, y] of log scale")
        if "clim" in param:
            self.info.add_param(
                "clim", param["clim"], "list of int",
                "[vmin, vmax] of colormap")
        if "cmap" in param:
            self.info.add_param(
                "cmap", param["cmap"], "str", "Colormap name")

    @ staticmethod
    def process(reqs, param):
        """Basic figure style for A4 paper size.

        Args:
            reqs[0](matplotlib.figure.Figure): Figure object.
            param (dict): See class args description.

        Returns:
            matplotlib.figure.Figure: Styled Figure object
        """
        fig = reqs[0]
        fig = set_format(fig)
        fig = set_size(fig, param["size"], param["margin"])

        if "limit" in param:
            x_lim = [param["limit"][0], param["limit"][1]]
            y_lim = [param["limit"][2], param["limit"][3]]
            fig = set_lim(fig, x_lim, y_lim)
        if "tick" in param:
            fig = set_tick(fig, param["tick"][0], param["tick"][1])
        if "tick_label" in param:
            fig = set_ticklabel(
                fig, param["tick_label"][0], param["tick_label"][1])
        if "label" in param:
            fig = set_label(fig, param["label"][0], param["label"][1])
        if "format" in param:
            fig = set_tickformat(fig, param["format"][0], param["format"][1])

        if "line_widths" in param:
            fig = set_linewidth(fig, param["line_widths"])
        if "line_styles" in param:
            fig = set_linestyle(fig, param["line_styles"])
        if "line_colors" in param:
            fig = set_linecolor(fig, param["line_colors"])

        if "marker_styles" in param:
            fig = set_markerstyle(fig, param["marker_styles"])
        if "marker_sizes" in param:
            fig = set_markersize(fig, param["marker_sizes"])
        if "marker_colors" in param:
            fig = set_markercolor(fig, param["marker_colors"][0],
                                  param["marker_colors"][1])
        if "marker_widths" in param:
            fig = set_markerwidth(fig, param["marker_widths"])
        if "bar_widths" in param:
            fig = set_barwidth(fig, param["bar_widths"])

        if "error_thicknesses" in param:
            fig = set_errorthickness(fig, param["error_thicknesses"])
        if "error_line_styles" in param:
            fig = set_errorlinestyle(fig, param["error_line_styles"])
        if "error_colors" in param:
            fig = set_errorcolor(fig, param["error_colors"])
        if "error_cap_sizes" in param:
            fig = set_errorcapsize(fig, param["error_cap_sizes"])

        if "is_box" in param:
            fig = is_boxed(fig, param["is_box"])
        if "log_scale" in param:
            fig = is_log_scale(fig, param["log_scale"])
        if "title" in param:
            fig = set_title(fig, param["title"])

        if "legend" in param:
            fig = set_legend(fig, *param["legend"])

        if "clim" in param:
            fig = set_clim(fig, param["clim"][0], param["clim"][1])
        if "cmap" in param:
            fig = set_cmap(fig, param["cmap"])
        return fig


class ParamTable(Basic):
    """Set figure style from the parameter table.

    The parameter dictionary of :class:`Basic` is replaced as :class:`Table`
    to set different style values for split figures.

    Args:
        reqs[0] (Figure): Figure class object.
        reqs[1] (Table): Parameter table object. For required columns, please
            see :class:`Basic`.
        param (dict): Parameters for :class:`Basic` is available to set
            common style for all figures.

    Returns:
        Figure: Styled Figure object
    """

    def set_reqs(self, reqs=None, param=None):
        """Drop elements that exist only in one required data.
        """
        self.reqs = setreqs.and_2reqs(reqs)

    @ staticmethod
    def process(reqs, param):
        """Basic figure style for A4 paper size.

        Args:
            reqs[0](matplotlib.figure.Figure): Figure object.
            param (dict): See class args description of :class:`Basic`.

        Returns:
            matplotlib.figure.Figure: Styled Figure object
        """
        fig = Basic.process(reqs, param)
        df = reqs[1].copy()
        col_names = list(df.columns)

        if "limit" in col_names:
            limit = eval(df["limit"].values[0])
            x_lim = [limit[0], limit[1]]
            y_lim = [limit[2], limit[3]]
            fig = set_lim(fig, x_lim, y_lim)
        if "tick" in col_names:
            tick = eval(df["tick"].values[0])
            fig = set_tick(fig, tick[0], tick[1])
        if "tick_label" in col_names:
            tick_label = eval(df["tick_label"].values[0])
            fig = set_ticklabel(
                fig, tick_label[0], tick_label[1])
        if "label" in col_names:
            label = eval(df["label"].values[0])
            fig = set_label(fig, label[0], label[1])
        if "format" in col_names:
            format = eval(df["format"].values[0])
            fig = set_tickformat(fig, format[0], format[1])

        if "line_widths" in col_names:
            line_widths = eval(df["line_widths"].values[0])
            fig = set_linewidth(fig, line_widths)
        if "line_styles" in col_names:
            line_styles = df["line_styles"].values[0]
            fig = set_linestyle(fig, line_styles)
        if "line_colors" in col_names:
            line_colors = eval(df["line_colors"].values[0])
            fig = set_linecolor(fig, line_colors)

        if "marker_styles" in col_names:
            marker_styles = df["marker_styles"].values[0]
            fig = set_markerstyle(fig, marker_styles)
        if "marker_sizes" in col_names:
            marker_sizes = eval(df["marker_sizes"].values[0])
            fig = set_markersize(fig, marker_sizes)
        if "marker_colors" in col_names:
            marker_colors = eval(df["marker_colors"].values[0])
            fig = set_markercolor(fig, marker_colors[0], marker_colors[1])
        if "marker_widths" in col_names:
            marker_widths = eval(df["marker_widths"].values[0])
            fig = set_markerwidth(fig, marker_widths)
        if "bar_widths" in col_names:
            bar_widths = eval(df["bar_widths"].values[0])
            fig = set_barwidth(fig, bar_widths)

        if "error_thicknesses" in col_names:
            error_thicknesses = eval(df["error_thicknesses"].values[0])
            fig = set_errorthickness(fig, error_thicknesses)
        if "error_line_styles" in col_names:
            error_line_styles = df["error_line_styles"].values[0]
            fig = set_errorlinestyle(fig, error_line_styles)
        if "error_colors" in col_names:
            error_colors = eval(df["error_colors"].values[0])
            fig = set_errorcolor(fig, error_colors)
        if "error_cap_sizes" in col_names:
            error_cap_sizes = eval(df["error_cap_sizes"].values[0])
            fig = set_errorcapsize(fig, error_cap_sizes)

        if "is_box" in col_names:
            is_box = eval(df["is_box"].values[0])
            fig = is_boxed(fig, is_box)
        if "log_scale" in col_names:
            log_scale = eval(df["log_scale"].values[0])
            fig = is_log_scale(fig, log_scale)
        if "title" in col_names:
            title = df["title"].values[0]
            fig = set_title(fig, title)

        if "legend" in col_names:
            legend = eval(df["legend"].values[0])
            fig = set_legend(fig, *legend)

        if "clim" in col_names:
            clim = eval(df["clim"].values[0])
            fig = set_clim(fig, clim[0], clim[1])
        if "cmap" in col_names:
            cmap = df["cmap"].values[0]
            fig = set_cmap(fig, cmap)
        return fig


class ColorBar(Figure):
    """Create color bar figure from mappable figure object.

    Args:
        reqs[0] (Figure): Figure containing mappable object.
        param["size"] (list of float, optional): [width, height] of figure
            image (cm). Defaults to [4.5, 0.9].
        param["margin"] (list, optional): [Left, bottom, right, top] of
            figure margin (cm). Defaults to [0.2, 0.7, 0.2, 0.05].
        param["is_vertical"] (bool, optional): Whether colorbar orientation is
            vertical. Defaults to False.
        param["label"] (str, optional): Colorbar label string.
        param["tick"] (list of float, optional): List of colorbar tick values.
        param["format"] (str, optional): Tick value format string. e.g. "%.0f".

    Returns:
        Figure: Styled colorbar Figure object
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.set_split_depth(self.reqs[0].info.split_depth())
        if "size" not in param:
            param["size"] = [4.5, 0.9]
        self.info.add_param(
            "size", param["size"], "list of cm",
            "[width, height] of figure size")
        if "margin" not in param:
            param["margin"] = [0.2, 0.7, 0.2, 0.05]
        self.info.add_param(
            "margin", param["margin"], "list of cm",
            "[left, bottom, right, top] of figure margin (cm)")
        if "is_vertical" not in param:
            param["is_vertical"] = False
        self.info.add_param(
            "is_vertical", param["is_vertical"], "bool",
            "Whether colorbar orientation is vertical")
        if "label" in self.info.get_param_names():
            param["label"] = self.info.get_param_value("label")
        elif "label" not in param:
            param["label"] = None
        self.info.add_param(
            "label", param["label"], "str", "Colorbar label string")
        if "tick" not in param:
            param["tick"] = None
        self.info.add_param(
            "tick", param["tick"], "list", "List of colorbar tick values")
        if "format" not in param:
            param["format"] = None
        self.info.add_param(
            "format", param["format"], "str", "Tick format string")

    @ staticmethod
    def process(reqs, param):
        """Create color bar figure from mappable figure object.

        Args:
            reqs[0](matplotlib.figure.Figure): Figure containing mappable.
            param (dict): See the class args description.

        Returns:
            matplotlib.figure.Figure: Styled Figure object
        """
        fig = reqs[0]
        ax = fig.axes[0]
        if ("is_vertical", True) in param.items():
            orientation = "vertical"
        else:
            orientation = "horizontal"
        if len(ax.images) > 0:
            cb = fig.colorbar(ax.images[0], ax=ax, orientation=orientation)
        else:
            cb = fig.colorbar(
                ax.collections[0], ax=ax, orientation=orientation)
        ax.set_visible(False)
        fig = set_format(fig, axes_no=1)
        size = param["size"]
        mrgn = param["margin"]
        fig = set_size(fig, size, mrgn, axes_no=1)
        cax = fig.axes[1]

        width = size[0] - mrgn[0] - mrgn[2]
        height = size[1] - mrgn[1] - mrgn[3]
        cax.set_box_aspect(height / width)
        cb.outline.set_linewidth(0.5)
        if param["is_vertical"]:
            fig = set_label(fig, None, param["label"], axes_no=1)
            fig = set_tick(fig, None, param["tick"], axes_no=1)
            fig = set_tickformat(fig, None, param["format"], axes_no=1)

            ytick_off = mpl.transforms.ScaledTranslation(
                -0.08, 0, fig.dpi_scale_trans)
            for label in cax.yaxis.get_majorticklabels():
                label.set_transform(label.get_transform() + ytick_off)

            ylabel_off = mpl.transforms.ScaledTranslation(
                -0.05, 0, fig.dpi_scale_trans)
            cax.yaxis.label.set_transform(
                cax.yaxis.label.get_transform() + ylabel_off)
        else:
            fig = set_label(fig, param["label"], None, axes_no=1)
            fig = set_tick(fig, param["tick"], None, axes_no=1)
            fig = set_tickformat(fig, param["format"], None, axes_no=1)

        return fig


font_dict = {"family": FONT_FAMILY, "size": FONT_SIZE}
font = font_manager.FontProperties(
    family=FONT_FAMILY, style="normal", size=FONT_SIZE)


def set_format(fig, axes_no=0):
    """Initiate figure format.
    """
    ax = fig.axes[axes_no]
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_linewidth(0.5)

    for artist in ([ax.xaxis.label, ax.yaxis.label]
                   + ax.get_xticklabels() + ax.get_yticklabels()):
        artist.set_fontsize(FONT_SIZE)
        artist.set_fontfamily(FONT_FAMILY)
    ax.tick_params(direction="out", length=1.5, width=0.5)

    # minor adjustment of tick and label positions
    xtick_off = mpl.transforms.ScaledTranslation(0, 0.03, fig.dpi_scale_trans)
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + xtick_off)
    ytick_off = mpl.transforms.ScaledTranslation(0.04, 0, fig.dpi_scale_trans)
    for label in ax.yaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + ytick_off)

    xlabel_off = mpl.transforms.ScaledTranslation(
        0, 0.025, fig.dpi_scale_trans)
    ax.xaxis.label.set_transform(
        ax.xaxis.label.get_transform() + xlabel_off)
    ylabel_off = mpl.transforms.ScaledTranslation(
        0.025, 0, fig.dpi_scale_trans)
    ax.yaxis.label.set_transform(
        ax.yaxis.label.get_transform() + ylabel_off)
    return fig


def set_size(fig, size, margin, axes_no=0):
    """Set figure size based on centimeter scale.
    """
    fig.set_size_inches(size[0] * CM, size[1] * CM)
    left = margin[0] / size[0]
    bottom = margin[1] / size[1]
    width = (size[0] - margin[0] - margin[2]) / size[0]
    height = (size[1] - margin[1] - margin[3]) / size[1]
    fig.axes[axes_no].set_position([left, bottom, width, height])
    return fig


def set_legend(fig, labels=None, handle_indexes=None, kwargs={}, axes_no=0):
    """Set figure legend.

    Args:
        fig (matplotlib.figure.Figure): Figure object.
        labels (list of str): List of label strings for each artists such as
            Line2D.
        handle_indexes (list of int): Index number list of artists to be
            included to the legend.
        kwargs (dict): Keyword arguments for :func:`matplotlib.pyplot.legend`.

    Returns:
        matplotlib.figure.Figure: Figure object with legend

    .. caution::

        All artists to be candidates for the legend should have labels during
        their creation.

    """
    ax = fig.axes[axes_no]
    handles, labels_ = ax.get_legend_handles_labels()

    if "frameon" not in kwargs:
        kwargs["frameon"] = False

    if (labels is None) and (handle_indexes is None):
        # delete all legends
        ax.legend_ = None
        return fig
    elif (labels is not None) and (handle_indexes is None):
        # create a new legend for all artists
        if type(labels) is str:
            labels = [labels]
        ax.legend(labels=labels, prop=font, **kwargs)
        return fig
    elif (labels is not None) and (handle_indexes is not None):
        # add a legend for selected artists
        if len(labels) != len(handle_indexes):
            raise Exception("Label and handle_nos should be the same counts.")
        leg = ax.legend(labels=labels,
                        handles=[handles[i] for i in handle_indexes],
                        prop=font, **kwargs)
        ax.add_artist(leg)
        return fig
    elif (labels is None) and (handle_indexes is not None):
        # add a legend for selected artists with the same labels
        leg = ax.legend(labels=[labels_[i] for i in handle_indexes],
                        handles=[handles[i] for i in handle_indexes],
                        prop=font, **kwargs)
        ax.add_artist(leg)
        return fig


def set_title(fig, title, axes_no=0):
    """Set title.
    """
    fig.axes[axes_no].set_title(title, fontdict=font_dict)
    return fig


def set_lim(fig, x_lim=None, y_lim=None, axes_no=0):
    """Set limit without changing tick and format.
    """
    ax = fig.axes[axes_no]
    if x_lim is not None:
        ax.set_xlim(x_lim)
        ticks_loc = ax.get_xticks().tolist()
        ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(ticks_loc))
    if y_lim is not None:
        ax.set_ylim(y_lim)
        ticks_loc = ax.get_yticks().tolist()
        ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(ticks_loc))
    return fig


def set_tickformat(fig, x_format, y_format, axes_no=0):
    """Set tick format without changing the style.
    """
    ax = fig.axes[axes_no]
    if x_format is not None:
        ax.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter(x_format))
    if y_format is not None:
        ax.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter(y_format))
    return fig


def set_tick(fig, x_tick=None, y_tick=None, axes_no=0):
    """Set ticks without changing limits.
    """

    ax = fig.axes[axes_no]
    x_lim = ax.get_xlim()
    y_lim = ax.get_ylim()
    if x_tick is not None:
        ax.set_xticks(x_tick)
    if y_tick is not None:
        ax.set_yticks(y_tick)
    fig = set_lim(fig, x_lim=x_lim, y_lim=y_lim, axes_no=axes_no)
    return fig


def set_label(fig, x_label, y_label, axes_no=0):
    """Set axis labels without changing its font.
    """
    ax = fig.axes[axes_no]
    ax.xaxis.set_label_text(x_label, font_dict)
    ax.yaxis.set_label_text(y_label, font_dict)
    return fig


def set_ticklabel(fig, x_label, y_label, axes_no=0):
    """Set tick labels without changing its font.
    """
    ax = fig.axes[axes_no]
    if x_label is not None:
        ax.set_xticklabels(x_label, fontdict=font_dict)
    if y_label is not None:
        ax.set_yticklabels(y_label, fontdict=font_dict)
    return fig


def set_linewidth(fig, line_widths, axes_no=0):
    """Set widths of lines.

    Args:
        fig (matplotlib.figure.Figure): Figure containing line artists.
        line_widths (float or list of float): Resizes line widths. All lines
            are resized according to the same value if set as a float.

    Returns:
        matplotlib.figure.Figure: Restyled Figure object
    """
    # for line style
    lines = [line for line in fig.axes[axes_no].get_children()
             if isinstance(line, mpl.lines.Line2D)
             and (line.get_label() != "_nolegend_")]
    for line, width in zip(lines, NumberLoop(line_widths)):
        line.set_linewidth(width)

    # for error bar line
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, width in zip(ctns, NumberLoop(line_widths)):
        ctn.lines[0].set_linewidth(width)

    return fig


def set_linestyle(fig, line_styles, axes_no=0):
    """Change line styles in bulk or individually.
    """
    # for line style
    gen = LineStyleLoop(line_styles)
    lines = [line for line in fig.axes[axes_no].get_children()
             if isinstance(line, mpl.lines.Line2D)
             and (line.get_label() != "_nolegend_")]
    for line, style in zip(lines, gen):
        line.set_linestyle(style)

    # for error bar line
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, style in zip(ctns, gen):
        ctn.lines[0].set_linestyle(style)

    return fig


def set_linecolor(fig, line_colors, axes_no=0):
    """Set colors of all line artists.

    Args:
        fig (matplotlib.figure.Figure): Figure object.
        line_colors (list of list): [RGB values,...]. RGB values should be
            [R(0-255), G(0-255), B(0-255)].

    Returns:
        matplotlib.figure.Figure: Restyled Figure object
    """
    gen = ColorLoop(line_colors)
    # for line style
    lines = [line for line in fig.axes[axes_no].get_children()
             if isinstance(line, mpl.lines.Line2D)
             and (line.get_label() != "_nolegend_")]
    for line, color in zip(lines, gen):
        edge_color = line.get_markeredgecolor()
        face_color = line.get_markerfacecolor()
        line.set_color(color)
        line.set_markeredgecolor(edge_color)
        line.set_markerfacecolor(face_color)

    # for error bar line
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, color in zip(ctns, gen):
        edge_color = ctn.lines[0].get_markeredgecolor()
        face_color = ctn.lines[0].get_markerfacecolor()
        ctn.lines[0].set_color(color)
        ctn.lines[0].set_markeredgecolor(edge_color)
        ctn.lines[0].set_markerfacecolor(face_color)
    return fig


def set_markerstyle(fig, marker_styles, axes_no=0):
    """Change line styles in bulk or individually.

    .. caution::

        Scatter plots can not change marker style.

    """
    gen = MarkerStyleLoop(marker_styles)
    # for line style
    lines = [line for line in fig.axes[axes_no].get_children()
             if isinstance(line, mpl.lines.Line2D)
             and (line.get_label() != "_nolegend_")]
    for line, style in zip(lines, gen):
        line.set_marker(style)

    # for error bar line
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, style in zip(ctns, gen):
        ctn.lines[0].set_marker(style)

    return fig


def set_markersize(fig, marker_sizes, axes_no=0):
    """Set marker sizes of all artists.
    """
    gen = NumberLoop(marker_sizes)
    # for line markers
    lines = [line for line in fig.axes[axes_no].get_children()
             if isinstance(line, mpl.lines.Line2D)
             and (line.get_label() != "_nolegend_")]
    for line, size in zip(lines, gen):
        line.set_markersize(size)

    # for scatter markers
    paths = [path for path in fig.axes[axes_no].get_children()
             if isinstance(path, mpl.collections.PathCollection)
             and (path.get_label() != "_nolegend_")]
    for path, size in zip(paths, gen):
        path.set_sizes([size])

    # for error bar line
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, size in zip(ctns, gen):
        ctn.lines[0].set_markersize(size)
    return fig


def set_markerwidth(fig, marker_widths, axes_no=0):
    """Set marker widths of all artists.
    """
    # for line style
    lines = [line for line in fig.axes[axes_no].get_children()
             if isinstance(line, mpl.lines.Line2D)
             and (line.get_label() != "_nolegend_")]
    for line, width in zip(lines, NumberLoop(marker_widths)):
        line.set_markeredgewidth(width)

    # for scatter markers
    paths = [path for path in fig.axes[axes_no].get_children()
             if isinstance(path, mpl.collections.PathCollection)
             and (path.get_label() != "_nolegend_")]
    for path, width in zip(paths, NumberLoop(marker_widths)):
        path.set_linewidth(width)

    # for bar plot
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.BarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, width in zip(ctns, NumberLoop(marker_widths)):
        for rect in ctn.patches:
            rect.set_linewidth(width)

    # for errorbar line markers
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, width in zip(ctns, NumberLoop(marker_widths)):
        ctn.lines[0].set_markeredgewidth(width)

    return fig


def set_barwidth(fig, bar_widths, axes_no=0):
    """Set bar widths.
    """
    # for bar plot
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.BarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, width in zip(ctns, NumberLoop(bar_widths)):
        for rect in ctn.patches:
            xc = rect.get_x() + rect.get_width() / 2
            rect.set_width(width)
            rect.set_x(xc - width / 2)
    return fig


def set_markercolor(fig, edge_colors, face_colors, axes_no=0):
    """Set edge and face colors of all artists.
    """
    # for line markers
    gen_edge = ColorLoop(edge_colors)
    gen_face = ColorLoop(face_colors)
    lines = [line for line in fig.axes[axes_no].get_children()
             if isinstance(line, mpl.lines.Line2D)
             and (line.get_label() != "_nolegend_")]
    for line, color in zip(lines, gen_edge):
        line.set_markeredgecolor(color)
    for line, color in zip(lines, gen_face):
        line.set_markerfacecolor(color)

    # for scatter markers
    paths = [path for path in fig.axes[axes_no].get_children()
             if isinstance(path, mpl.collections.PathCollection)
             and (path.get_label() != "_nolegend_")]
    for path, color in zip(paths, gen_edge):
        path.set_edgecolor(color)
    for path, color in zip(paths, gen_face):
        if color is None:
            pass  # PathCollection.set_facecolor does not work properly
        else:
            path.set_facecolor(color)

    # for bar plot
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.BarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, color in zip(ctns, gen_edge):
        for rect in ctn.patches:
            rect.set_edgecolor(color)
    for ctn, color in zip(ctns, gen_face):
        for rect in ctn.patches:
            if color is None:
                pass  # Rectangle.set_facecolor does not work properly
            else:
                rect.set_facecolor(color)

    # for errorbar line
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, color in zip(ctns, gen_edge):
        ctn.lines[0].set_markeredgecolor(color)
    for ctn, color in zip(ctns, gen_face):
        ctn.lines[0].set_markerfacecolor(color)

    return fig


def set_errorthickness(fig, error_thicknesses, axes_no=0):
    """Set widths of lines.

    Args:
        fig (matplotlib.figure.Figure): Figure containing line artists.
        line_widths (float or list of float): Resizes line widths. All lines
            are resized according to the same value if set as a float.

    Returns:
        matplotlib.figure.Figure: Restyled Figure object
    """
    # for line with error
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, thick in zip(ctns, NumberLoop(error_thicknesses)):
        for line in ctn.lines[1]:
            line.set_markeredgewidth(thick)
        for lcoll in ctn.lines[2]:
            lcoll.set_linewidth(thick)

    # for bar with error
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.BarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, thick in zip(ctns, NumberLoop(error_thicknesses)):
        if ctn.errorbar is not None:
            for line in ctn.errorbar.lines[1]:
                line.set_markeredgewidth(thick)
            for lcoll in ctn.errorbar.lines[2]:
                lcoll.set_linewidth(thick)

    return fig


def set_errorlinestyle(fig, error_line_styles, axes_no=0):
    """Change error line styles in bulk or individually.
    """
    # for line with error
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, style in zip(ctns, LineStyleLoop(error_line_styles)):
        for lcoll in ctn.lines[2]:
            lcoll.set_linestyle(style)

    # for bar with error
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.BarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, style in zip(ctns, LineStyleLoop(error_line_styles)):
        if ctn.errorbar is not None:
            for lcoll in ctn.errorbar.lines[2]:
                lcoll.set_linestyle(style)
    return fig


def set_errorcolor(fig, error_colors, axes_no=0):
    """Set colors of all line artists.

    Args:
        fig (matplotlib.figure.Figure): Figure object.
        line_colors (list of list): [RGB values,...]. RGB values should be
            [R(0-255), G(0-255), B(0-255)].

    Returns:
        matplotlib.figure.Figure: Restyled Figure object
    """
    # for line with error
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, color in zip(ctns, ColorLoop(error_colors)):
        for line in ctn.lines[1]:
            line.set_markeredgecolor(color)
        for lcoll in ctn.lines[2]:
            lcoll.set_color(color)

    # for bar with error
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.BarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, color in zip(ctns, ColorLoop(error_colors)):
        if ctn.errorbar is not None:
            for line in ctn.errorbar.lines[1]:
                line.set_markeredgecolor(color)
            for lcoll in ctn.errorbar.lines[2]:
                lcoll.set_color(color)
    return fig


def set_errorcapsize(fig, error_cap_sizes, axes_no=0):
    """Set marker sizes of all artists.
    """
    # for line with error
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.ErrorbarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, size in zip(ctns, NumberLoop(error_cap_sizes)):
        for line in ctn.lines[1]:
            line.set_markersize(size)

    # for bar with error
    ctns = [ctn for ctn in fig.axes[axes_no].containers
            if isinstance(ctn, mpl.container.BarContainer)
            and (ctn.get_label() != "_nolegend_")]
    for ctn, size in zip(ctns, NumberLoop(error_cap_sizes)):
        if ctn.errorbar is not None:
            for line in ctn.errorbar.lines[1]:
                line.set_markersize(size)
    return fig


def is_boxed(fig, bool=True, axes_no=0):
    """Show a rectangle-shaped box if True. Delete axes lines if False.
    """
    ax = fig.axes[axes_no]
    if bool is None:
        return fig
    elif bool:
        ax.spines["right"].set_visible(True)
        ax.spines["left"].set_visible(True)
        ax.spines["top"].set_visible(True)
        ax.spines["bottom"].set_visible(True)
        ax.spines["right"].set_linewidth(LINE_SIZE)
        ax.spines["left"].set_linewidth(LINE_SIZE)
        ax.spines["top"].set_linewidth(LINE_SIZE)
        ax.spines["bottom"].set_linewidth(LINE_SIZE)
    else:
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
    return fig


def is_log_scale(fig, bools, axes_no=0):
    """Change X and Y axes to the log scale.

    Args:
        fig (matplotlib.figure.Figure): Figure object.
        bools (list or bool):  Change axes to the log scale. e.g.,
            [False, True] means that the only y-axis is the log scale.

    Returns:
        matplotlib.figure.Figure: Restyled Figure object
    """
    ax = fig.axes[axes_no]
    if bools[0]:
        ax.set_xscale("log")
    if bools[1]:
        ax.set_yscale("log")
    return fig


def set_cmap(fig, cmap, axes_no=0):
    """Set cmaps of all artists.
    """
    for artist in fig.axes[axes_no].get_children():
        if type(artist) in [mpl.collections.PathCollection,
                            mpl.collections.PatchCollection,
                            mpl.image.AxesImage]:
            artist.set_cmap(cmap)
    return fig


def set_clim(fig, vmin, vmax, axes_no=0):
    """Set clim of all artists.
    """
    for artist in fig.axes[axes_no].get_children():
        if type(artist) in [mpl.collections.PathCollection,
                            mpl.collections.PatchCollection,
                            mpl.image.AxesImage]:
            artist.set_clim(vmin, vmax)
    return fig
