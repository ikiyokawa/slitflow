import pandas as pd

from ..data import Data
from .. import setindex


class Table(Data):
    """Table Data class using pandas.DataFrame saved as CSV files.

    See also :class:`~slitflow.data.Data` for properties and methods.
    Concrete subclass is mainly in :mod:`slitflow.tbl`,
    :mod:`slitflow.trj` and :mod:`slitflow.loc`.

    """
    EXT = ".csv"

    def __init__(self, info_path=None):
        super().__init__(info_path)

    def load_data(self, path):
        """Load CSV file as :class:`pandas.DataFrame`.
        """
        return pd.read_csv(path, dtype=self.info.get_column_type())

    def save_data(self, df, path):
        """Save :class:`pandas.DataFrame` data into CSV file.
        """
        df = df.set_axis(self.info.get_column_name("all"), axis=1)
        df.to_csv(path, index=False)

    def split_data(self):
        """Split data table according to info.index.
        """
        if len([x for x in self.data if x is not None]) == 0:
            return  # e.g. data.load.table.CsvFromFolder
        df = pd.concat(self.data)
        df_index = self.info.index.copy()
        common_cols = list(set(df_index.columns) & set(df.columns))
        if len(common_cols) == 0:
            return
        if len(df) == 0:
            return  # see test_trj_filter
        df = pd.merge(df, df_index, on=common_cols, how="left")
        grouped = df.groupby(["_file", "_split"])
        self.data = list(list(zip(*grouped))[1])
        data = []
        for df in self.data:
            data.append(df.drop(["_file", "_split"], axis=1))
        self.data = data

    def set_index(self):
        """How to get info.index.

        Default function for Table is
        :func:`slitflow.setindex.from_data`.

        """
        setindex.from_data(self)


def merge_different_index(self, req_no):
    """Merge the index table to the split result data.

    This function is used in :meth:`~slitflow.data.Data.post_run`
    to append index information into the result data table.
    For example, if :meth:`process` does not return any ``img_no`` because
    required data is :class:`numpy.ndarray` that do not have ``img_no``
    information, we have to add ``img_no`` from
    :attr:`~slitflow.info.Info.index`.

    """
    df_index = self.reqs[req_no].info.file_index()
    dfs = []
    for i, (_, row) in enumerate(df_index.groupby(["_file", "_split"])):
        row_index = row.drop_duplicates()\
            .drop(["_file", "_split"], axis=1).reset_index(drop=True)
        df = self.data[i]
        df_mrg = pd.concat([row_index, df], axis=1)
        dfs.append(df_mrg.fillna(method="ffill").astype(
            self.info.get_column_type()))
    self.data = dfs


def merge_overlap_index(self, req_no, on_col_name):
    """Merge the index table to the split result data.

    This function is used in :meth:`~slitflow.data.Data.post_run`
    to append index information into the result data table.
    This function merge index tables that have overlapping columns.

    """
    df_index = self.reqs[req_no].info.file_index()
    dfs = []
    for i, (_, row) in enumerate(df_index.groupby(["_file", "_split"])):
        row_index = row.drop_duplicates()\
            .drop(["_file", "_split"], axis=1).reset_index(drop=True)
        df = self.data[i]
        df_mrg = row_index.merge(df, on=on_col_name)
        dfs.append(df_mrg.fillna(method="ffill").astype(
            self.info.get_column_type()).reset_index(drop=True))
    self.data = dfs
