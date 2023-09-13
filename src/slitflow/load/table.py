import pandas as pd
from ..tbl.table import Table


class SingleCsv(Table):
    """Import a CSV table as the top level of the observation data.

    Args:
        reqs[] (None): Input Data is not required.
        param["path"] (str): Path to a CSV file.
        param["col_info"] (list of list, optional): Column information.
            Each list should have [depth number, column name, unit, type, 
            description]. e.g. [[1, "img_no", "int32", "num", "Image number"]].
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Imported Table class
    """

    def set_info(self, param):
        """Create information.
        """
        for col_info in param["col_info"]:
            self.info.add_column(
                col_info[0], col_info[1], col_info[2],
                col_info[3], col_info[4])
        self.info.add_param("path", param["path"], "str", "Path to a CSV file")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Load a CSV file from the path string.

        Args:
            param["path"] (str): Path to a CSV file.

        Returns:
            pandas.DataFrame: Imported table
        """
        return pd.read_csv(param["path"])
