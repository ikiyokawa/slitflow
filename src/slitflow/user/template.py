"""This module is user-defined class template.
"""

from ..tbl.table import Table


class AddOne(Table):
    """Add one to selected column.

    [Write description here]

    Args:
        reqs[0] (Table): Table to add one.
        param["calc_col"] (str): Column name to add one.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Table containing a calculated column
    """

    def set_info(self, param):
        """[Write brief description]
        """
        self.info.copy_req(0)

        # this class should remove zero depth columns except for calc_column
        index_cols = self.info.get_column_name("index")
        self.info.delete_column(keeps=index_cols + [param["calc_col"]])

        # index column names are also required to specify which column should
        # be remained
        self.info.add_param("index_cols", index_cols, "str",
                            "Index column names")

        self.info.add_param(
            "calc_col", param["calc_col"], "str", "Column name to calculate")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Add one to selected column.

        Args:
            reqs[0] (pandas.DataFrame): Table to add one.
            param["calc_col"] (str): Column name to add one.
            param["index_cols"] (str): Column names of index columns.

        Returns:
            pandas.DataFrame: Table containing a calculated column
        """
        df = reqs[0].copy()
        df_result = df[param["index_cols"]].copy()
        df_result[param["calc_col"]] = df[param["calc_col"]].values + 1
        return df_result
