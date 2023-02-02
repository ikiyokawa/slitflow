import pandas as pd

from ..data import Data
from .. import setindex


class Table(Data):
    EXT = ".csv"

    def __init__(self, info_path=None):
        super().__init__(info_path)

    def load_data(self, path):
        return pd.read_csv(path, dtype=self.info.get_column_type())

    def save_data(self, df, path):
        df = df.set_axis(self.info.get_column_name("all"), axis=1)
        df.to_csv(path, index=False)

    def split_data(self):
        if len([x for x in self.data if x is not None]) == 0:
            return
        df = pd.concat(self.data)
        df_index = self.info.index.copy()
        common_cols = list(set(df.columns) & set(df_index.columns))
        if len(common_cols) == 0:
            return
        df = df_index.merge(df)
        grouped = df.groupby("_split")
        self.data = list(list(zip(*grouped))[1])
        data = []
        for df in self.data:
            data.append(df.drop(["_file", "_split"], axis=1))
        self.data = data

    def set_index(self):
        setindex.from_data(self)
