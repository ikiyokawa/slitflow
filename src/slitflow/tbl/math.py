import numpy as np

from .table import Table
from .. import RANDOM_SEED
from ..fun.misc import reduce_list as rl
from .. import setreqs

np.random.seed(RANDOM_SEED)


class EvalOneCol(Table):
    """Apply :func:`eval` calculation to columns.

    Args:
        reqs[0] (Table): Table containing columns for calculation.
        param["calc_cols"] (list of str, optional): Column names to calculate.
            If not provided, all columns are calculated.
        param["split_depth"] (int): File split depth number.
        param["type"] (str, optional): Preset calculation type. Select
            from "log10", "standardize" or user defined. type is also used as
            new column name headers.
        param["eval"] (str, optional): Calculation eval string such as
            '__import__("numpy").log10(x)'. eval is needed if type is not
            defined. The input values should be x in eval string.

    Returns:
        Table: Calculated Table object
    """

    def set_info(self, param={}):
        """Modify column information and add params.
        """
        self.info.copy_req()
        if param["type"] == "log10":
            calc_name = "log10_"
            eval_str = '__import__("numpy").log10(x)'
        elif param["type"] == "standardize":
            calc_name = "std_"
            eval_str = "(x - x.mean()) / x.std()"
        else:
            calc_name = param["type"]
            eval_str = param["eval"]
        new_cols = []
        if "calc_cols" not in param:
            param["calc_cols"] = self.info.get_column_name("col")
        for calc_col in param["calc_cols"]:
            new_col = calc_name + calc_col
            new_cols.append(new_col)
            col_dict = self.info.get_column_dict(calc_col)
            self.info.add_column(
                col_dict["depth"], new_col, col_dict["type"],
                calc_name + "[" + col_dict["unit"] + "]",
                calc_name + " of " + col_dict["description"])
        self.info.delete_column(param["calc_cols"])
        self.info.add_param("calc_cols", param["calc_cols"],
                            "list of str", "Column names to calculate")
        self.info.add_param("new_cols", new_cols,
                            "list of str", "Generated column names")
        self.info.add_param("eval", eval_str,
                            "str", "Calculation eval string")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Apply :func:`eval` calculation to columns.

        If you want to calculate multiple columns in one Table object,
        , use :class:`EvalTwoCols` and select the same Table object for
        reqs[0] and reqs[1].

        Args:
            reqs[0] (pandas.DataFrame): Table containing columns for
                calculation.
            param["calc_cols"] (list of str): Column names to calculate.
            param["new_cols"] (list of str): Column names of calculated
                columns.
            param["eval"] (str): Calculation eval string such as
                '__import__("numpy").log10(x)'. The input values should be x
                in eval string.

        Returns:
            pandas.DataFrame: Table containing calculated columns
        """
        df = reqs[0].copy()
        for calc_col, new_col in zip(param["calc_cols"], param["new_cols"]):
            x = df[calc_col]
            df[new_col] = eval(param["eval"], {}, {"x": x})
            df = df.drop(calc_col, axis=1)
        return df


class EvalTwoCols(Table):
    """Apply :func:`eval` between two columns from different Tables.

    Args:
        reqs[0] (Table): Table containing a column for calculation as x.
        reqs[1] (Table): The second table containing a column for calculation
            as y.
        param["calc_cols"] (list of str): Column names of [x, y].
        param["eval"] (str): String of equation with column1=x and
            column2=y. Ex. "x*y".
        param["new_col_info"](tuple of str): Information of new
            columns. This should be ("name", "type", "unit", "description").
        param["keep_cols"] (list of bool or list of list of str): If True, keep
            all columns. If False, delete all columns except calc_cols.
            If list of str, keep columns in the list.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Calculated column data
    """

    def set_reqs(self, reqs, param):
        """Drop elements that exist only in one required data.
        """
        self.reqs = setreqs.allocate_data(reqs, param)

    def set_info(self, param={}):
        """Set new column information and add params."""
        if "keep_cols" not in param:
            param["keep_cols"] = [False, False]
        keep_cols_list = []
        for i, keep_cols in enumerate(param["keep_cols"]):
            if keep_cols is True:
                keep_cols = self.reqs[i].info.get_column_name("col")
            elif keep_cols is False:
                keep_cols = []
            keep_cols_list.append(keep_cols)
        self.info.add_param("keep_cols", keep_cols_list, "list of str",
                            "Keep columns in the list")
        self.info.copy_req(0)
        keeps = self.info.get_column_name("index") + keep_cols_list[0]
        self.info.delete_column(keeps=keeps)

        self.info.copy_req(1)
        self.info.delete_column(keeps=keeps + keep_cols_list[1])

        self.info.add_column(0, *param["new_col_info"])
        self.info.add_param("calc_cols", param["calc_cols"],
                            "list of str", "Column names of [x, y]")
        self.info.add_param(
            "eval", param["eval"], "str",
            "String of eval with column1=x and column2=y")
        self.info.add_param(
            "col_name", param["new_col_info"][0], "str",
            "Calculated column name")
        self.info.add_param(
            "index_cols", self.info.get_column_name("index"),
            "list of str", "Index column names")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Apply :func:`eval` between two columns from different Tables.

        Args:
            reqs[0] (pandas.DataFrame): Table containing a column for
                calculation as x.
            reqs[1] (pandas.DataFrame): The second table containing a column
                for calculation as y.
            param["calc_cols"] (list of str): Column names of [x, y].
            param["index_cols"] (list of str): Column names of index.
            param["eval"] (str): String of equation with column1=x and
                column2=y. Ex. "x*y".
            param["keep_cols"] (list of list of str): List of column names to
                keep.
            param["col_name"](str): Name string of calculated column.

        Returns:
            Table: Calculated column data
        """
        df1 = reqs[0].copy()
        df2 = reqs[1].copy()
        x = df1[param["calc_cols"][0]].values
        y = df2[param["calc_cols"][1]].values
        df = df1[param["index_cols"]]
        for keep_cols in param["keep_cols"]:
            for keep_col in keep_cols:
                df[keep_col] = df1[[keep_col]]
        df[param["col_name"]] = eval(param["eval"], {}, {"x": x, "y": y})
        return df


class Centering(Table):
    """Shift column values using center values.


    Args:
        reqs[0] (Table): Table to shift column values.
        param["calc_cols"] (list of str): Coordinate column names to shift.
        param["group_depth"] (int): Data split depth.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Table containing shifted columns
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.add_param(
            "calc_cols", param["calc_cols"], "str", "Column names of [x, y]")
        self.info.set_group_depth(param["group_depth"])
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Shift column values using center values.

        Args:
            reqs[0] (pandas.DataFrame): Table to shift column values.
            param["calc_cols"] (list of str): Coordinate column names to shift.
            param["index_cols"] (list of str): Column names for index.

        Returns:
            pandas.DataFrame: Table containing shifted columns

        """
        df = reqs[0].copy()
        if len(param["index_cols"]) > 0:
            grouped = df.groupby(rl(param["index_cols"]), group_keys=False)
            df_new = grouped.apply(lambda x: centering_by_edge(
                x, param["calc_cols"]))
        else:
            df_new = centering_by_edge(df, param["calc_cols"])
        return df_new


def centering_by_edge(df, calc_cols):
    """Shift column value by center position.

    Args:
        df (pandas.DataFrame): Table containing columns to shift.
        calc_cols (list of str): Column names to shift values.

    Returns:
        pandas.DataFrame: Table containing shifted columns
    """
    for calc_col in calc_cols:
        x = df[calc_col].values
        xc = (np.max(x) + np.min(x)) / 2
        df[calc_col] = x - xc
    return df


class AddGauss(Table):
    """Add Gaussian random values to Table.

    Args:
        reqs[0] (Table): Table to add Gauss value.
        param["name"] (str): Column name of Gauss value.
        param["unit"] (str): Column unit of Gauss value.
        param["description"] (str): Column description of Gauss value.
        param["sigmas"] (float): Standard deviation of Gauss values.
        param["baselines"] (float): Baseline value of Gauss values.
        param["ratio"] (float): Ratio of Gauss fraction.
        param["seed"] (int, optional): Random seed.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Table with Gauss values
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.add_column(0, param["name"], "float64", param["unit"],
                             param["description"])
        self.info.add_param("name", param["name"], "str",
                            "Column name of Gauss values")
        self.info.add_param("sigmas", param["sigmas"], "a.u.",
                            "Standard deviation of Gauss values")
        self.info.add_param("baselines", param["baselines"], "a.u.",
                            "Baseline value of background")
        self.info.add_param("ratio", param["ratio"], "float",
                            "Ratio value of each Gauss component")
        if "seed" in param:
            self.info.add_param("seed", param["seed"], "int", "Random seed")
            np.random.seed(param["seed"])
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Add Gaussian random values to table.

        Args:
            reqs[0] (numpy.ndarray): Table to add Gauss value.
            param["name"] (str): Column name of Gauss value.
            param["sigmas"] (float): Standard deviation of Gauss values.
            param["baselines"] (float): Baseline value of Gauss values.
            param["ratio"] (float): Ratio of Gauss fraction.

        Returns:
            numpy.ndarray: Table with Gauss values
        """
        df = reqs[0].copy()
        counts = np.round(np.array(param["ratio"]) * len(df)).astype(np.int32)
        rnds = np.empty(0)
        for baseline, sigma, count in zip(param["baselines"], param["sigmas"],
                                          counts):
            rnds = np.concatenate((rnds, np.random.normal(
                loc=baseline, scale=sigma, size=count)))
        df[param["name"]] = rnds
        return df
