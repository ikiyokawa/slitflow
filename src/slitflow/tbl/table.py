import numpy as np
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
        df_index = self.info.index
        index_cols = [col for col in df_index.columns if col not in
                      ["_file", "_split", "_dest", "_keep", "_load"]]
        self.data = [df for df in self.data if df is not None]
        if len(self.data) == 0:
            # make None list
            dest_abs = df_index["_dest"].abs().values
            dest_abs = dest_abs[dest_abs != 0]
            self.data = [None] * len(np.sort(np.unique(dest_abs)))
            # delete temporary rows
            # find "_file", "_split", "_keep" are all nan and delete its rows
            df_index = df_index.dropna(subset=["_file", "_split", "_keep"],
                                       how="all")
            self.info.index = df_index.reset_index(drop=True)
        else:
            df_data = pd.concat(self.data)
            if len(index_cols) == 0:
                df_dest = df_index[["_dest"]].drop_duplicates()
                df_dest['_key'] = 1
                df_data['_key'] = 1
                df = pd.merge(
                    df_dest, df_data, on='_key').drop('_key', axis=1)
            else:
                df = pd.merge(df_index[index_cols + ["_dest"]],
                              df_data, on=index_cols, how="left")
            df = df[df["_dest"] != 0]
            df['_dest_abs'] = df['_dest'].abs()

            df = df.sort_values(by=['_dest_abs'] +
                                index_cols).reset_index(drop=True)
            df.drop(columns=['_dest_abs'], inplace=True)
            self.data = [None if dest < 0 else group.drop(columns=["_dest"])
                         for dest, group in df.groupby("_dest", sort=False)]

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
    if len(df_index) == 0:
        return
    dfs = []
    for i, (_, row) in enumerate(df_index.groupby(["_file", "_split"])):
        row_index = row.drop_duplicates().reset_index(drop=True)
        for col in "_file", "_split", "_dest", "_keep":
            if col in row_index.columns:
                row_index.drop(col, axis=1, inplace=True)
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
