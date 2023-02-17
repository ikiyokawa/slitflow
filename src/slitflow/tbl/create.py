import pandas as pd
import itertools

from ..tbl.table import Table


class Index(Table):
    """Create nested index Table.

    This class can be used for the initial step of simulations.

    Args:
        reqs[] (None): Input Data is not required.
        param["index_counts"] (list of int): Total counts of each column.
        param["split_depth"] (int): File split depth number.
        param["index_value"] (int, optional): Set a single value to the first
            index column if you want to fix it.
        param["type"] (str, optional): Parameter initiation type. If you do
            not use ``type``, you must set ``calc_cols`` as a list of column
            names.

                * "image" : Add ``img_no`` index.
                * "trajectory" : Add ``img_no`` and ``trj_no`` index.
                * "movie" : Add ``img_no`` and ``frm_no`` index.

        param["param"] (list of list, optional): Additional parameters.
            The list should be [[name, value, unit, description],...].

    Returns:
        Table: Index Table of iterated numbers

    Examples:
        Create a nested trajectory index list.

        .. code-block:: python

            D = sf.data.tbl.create.Index()
            D.run([],{"type":"trajectory", "index_counts":[2,3],
                      "split_depth":0})
            print(D.data[0])
            #   img_no trj_no
            # 0      1      1
            # 1      1      2
            # 2      1      3
            # 3      2      1
            # 4      2      2
            # 5      2      3

    """

    def set_info(self, param):
        """Set columns and params.
        """

        if ("type", "trajectory") in param.items():
            self.info.add_column(
                1, "img_no", "int32", "num", "Image number")
            self.info.add_column(
                2, "trj_no", "int32", "num", "Trajectory number")
            self.info.add_param(
                "calc_cols", ["img_no", "trj_no"], "list of str",
                "Index calc column names")
        elif ("type", "image") in param.items():
            self.info.add_column(
                1, "img_no", "int32", "num", "Image number")
            self.info.add_param(
                "calc_cols", ["img_no"], "list of str",
                "Index calc column names")
        elif ("type", "movie") in param.items():
            self.info.add_column(
                1, "img_no", "int32", "num", "Image number")
            self.info.add_column(
                2, "frm_no", "int32", "num", "Trajectory number")
            self.info.add_param(
                "calc_cols", ["img_no", "frm_no"], "list of str",
                "Index calc column names")
        else:
            for col_name in param["calc_cols"]:
                self.info.add_column(
                    None, col_name, "int32", "num", col_name + " index")
            self.info.add_param(
                "calc_cols", param["calc_cols"], "list of str",
                "Index calc column names")
        if "index_value" in param:
            self.info.add_param(
                "index_value", param["index_value"], "num",
                "Specific index value")
        self.info.add_param(
            "index_counts", param["index_counts"], "num",
            "Total counts of each column")
        if "param" in param:
            for pp in param["param"]:
                self.info.add_param(*pp)
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Create nested index table.

        Args:
            reqs (None): Empty list.
            param["calc_cols"] (list of str): List of column names.
            param["index_counts"] (list of int): Total counts of each column.
            param["index_value"] (int, optional): An explicit value of the top
                level column.

        Returns:
            pandas.DataFrame: Index table of iterated numbers
        """
        iters = []
        for i in param["index_counts"]:
            iters.append(tuple(range(1, i + 1)))
        df = pd.DataFrame(list(itertools.product(*iters)))
        df.columns = param["calc_cols"]
        if "index_value" in param:
            df[param["calc_cols"][0]] = param["index_value"]
        return df
