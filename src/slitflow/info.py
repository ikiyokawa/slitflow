import numpy as np
import pandas as pd

import json
import os
import datetime

from .fun.misc import reduce_list as rl
from . import __version__


class Info():
    """Data information class.


    Args:
        Data (Data): Parent Data class.

    Attributes:
        column (list of dict): Column information dictionaries. The
            dictionary should contain ``depth``, ``name``, ``type``,
            ``unit`` and  ``description``.
        param (list of dict): Parameter dictionaries. The dictionary should
            contain ``name``, ``value``, ``unit`` and ``description``.
        meta (dict): Metadata containing information about the data
            path, datetime, and required data.
        path (str): Absolute path to save this Info object in JSON format
            with an extension of ``.sf``,
            including column, param, and meta dictionaries.
        index (pandas.DataFrame): Index table to describe the data
            hierarchy.
        file_nos (list of int): List of split file numbers.
        split_depth_req (int): Split depth number used for reqs_split.

    """

    def __init__(self, Data, info_path=None):
        """Initiate attributes and load info file if it exists.

        Args:
            Data (Data): Parent Data class.
            info_path (str, optional): Path to the information file. Defaults
                to None.
        """
        self.Data = Data
        self.column = []
        self.param = []
        self.meta = {}
        self.index = pd.DataFrame()
        self.set_path(info_path)
        self.load()
        self.split_depth_req = None

    def __str__(self):
        info_str = "Data: " + fullname(self.Data)
        if self.path is not None:
            info_str = info_str + os.linesep + "Path: " + self.path \
                + os.linesep
        else:
            info_str = info_str + os.linesep + "Path: None"
        return info_str

    def set_path(self, info_path):
        """Set path string to this object.

        Args:
            info_path (str): Absolute path to the information file.
        """
        if info_path is not None:
            if info_path[-3:] != ".sf":
                self.path = os.path.splitext(info_path)[0] + ".sf"
            else:
                self.path = info_path
        elif hasattr(self, "path"):
            pass
        else:
            self.path = None

    def load(self, info_path=None):
        """Load information file.

        Args:
            info_path (str, optional): Absolute path to the information file.
                Defaults to None.
        """
        self.set_path(info_path)
        if self.path is None:
            pass
        elif os.path.exists(self.path):
            with open(self.path) as f:
                info = json.load(f)
                self.meta = info["meta"]
                self.column = info["column"]
                self.param = info["param"]
                self.load_index()
                self.set_file_nos(None)
        else:
            pass

    def load_index(self):
        """Load index table from the index file.

        Info object should have the :attr:`path` attribute. See
        :meth:`~slitflow.info.Info.save_index()` docstring for the
        index file format.

        """
        index_path = self.path + "x"
        if os.path.exists(index_path):
            if os.stat(index_path).st_size == 0:
                return  # sfx of split_depth=0
            df = pd.read_csv(index_path, header=None)\
                .fillna(method="ffill").astype(np.int32)
            df.columns = self.get_column_name("index")
            if "_split" in self.index.columns:
                self.index.drop(columns=["_split"], inplace=True)
            if "_file" in self.index.columns:
                self.index.drop(columns=["_file"], inplace=True)
            self.index = pd.concat([self.index, df]).drop_duplicates()
            self.set_index_file_no()

    def save_index(self, load_index=True):
        """Update index information file.

        The file size is reduced by excluding duplicate higher-level
        hierarchical numbers as follows:

        .. code-block:: python

            img_no frm_no
                 1      1      1,1
                 1      2  ->  ,2
                 1      3      ,3

        .. caution::

            This method updates rather than overwrites existing index files.
            This process is necessary to save the split file, but if there is
            an unrelated index file with the same name, it must be deleted.

        """
        if load_index:
            self.load_index()
        index_path = self.path + "x"
        if "_split" in self.index.columns:
            self.index.drop(columns=["_split"], inplace=True)
        if "_file" in self.index.columns:
            self.index.drop(columns=["_file"], inplace=True)

        # size reducing code
        idx = self.index.to_numpy()
        to_sel = idx[:-1, :] == idx[1:, :]
        to_sel = np.cumprod(to_sel.astype(np.int8), axis=1).astype(np.bool8)
        to_sel = np.insert(to_sel, 0, False, axis=0)
        idx = np.where(to_sel, -99999, idx)
        fmt = ','.join(['%d'] * idx.shape[1])
        fmt = '\n'.join([fmt] * idx.shape[0])
        idx = fmt % tuple(idx.ravel())
        idx = idx.replace('-99999', '')

        # to avoid empty index with \n
        if len(idx.replace('\n', '')) == 0:
            idx = ''

        with open(index_path, mode="w") as f:
            f.write(idx)

    def set_index_file_no(self):
        """Add file number column to the index table according to split depth.
        """
        if "_file" in self.index.columns:
            if not self.index['_file'].isna().any():
                return
        index_names = self.get_column_name("index")
        if len(self.index) == 0:
            return
        elif self.split_depth() > 0:
            grouped = self.index.groupby(rl(index_names[:self.split_depth()]))
            dfs = list(list(zip(*grouped))[1])
            for i, df in enumerate(dfs):
                df["_file"] = i
            self.index = pd.concat(dfs)
        else:
            self.index["_file"] = 0

    def set_file_nos(self, file_nos):
        """Add current file number list of split data.

        Args:
            file_nos (array-like): File numbers corresponding to
                the split data.
        """
        stash_split_depth = self.split_depth()
        if isinstance(file_nos, list):
            pass
        elif isinstance(file_nos, np.ndarray):
            file_nos = list(file_nos.astype(int))
        elif file_nos is None or pd.isna(file_nos):  # fill from index
            if len(self.index) == 0:
                file_nos = [0]
            else:
                file_nos = list(np.unique(self.index["_file"].values))
        elif type(file_nos) in (int, np.int64, float, np.float64):
            file_nos = [int(file_nos)]
        else:
            raise Exception("Type of file_nos is invalid.")
        self.file_nos = file_nos
        self.set_split_depth(stash_split_depth)

    def file_index(self):
        """Return index table of current file number.

        Returns:
            pandas.DataFrame: Index table of current split file
        """
        self.set_index_file_no()
        index = self.index.copy()
        if len(index) == 0:
            self.file_nos = [0]
            return index
        if not hasattr(self, "file_nos"):
            self.set_file_nos(None)
        return index[index["_file"].isin(self.file_nos)]

    def save(self, info_path=None):
        """Save data information as a JSON file.

        Args:
            info_path (str, optional): Path to the info file. Defaults to None.
        """
        self.set_path(info_path)
        self.delete_private_param()
        self.set_meta()
        self.save_index()
        with open(self.path, "w") as f:
            json.dump(self.get_dict(), f, indent=2)

    def split(self, split_depth=None):
        """Add a _split column to the index table.

        .. caution::

            This split depth is used to save newly generated data. Do not use
            :meth:`set_split_depth()` for this usage. If you use
            :meth:`set_split_depth()`, an error will occur when loading data
            that has already been saved.

        Args:
            split_depth (int, optional): Split depth for the save data.
                Defaults to None.
        """
        if split_depth is None:
            split_depth = self.split_depth()
        self.split_depth_req = split_depth
        index_names = self.get_column_name("index")
        if split_depth > 0:
            if "_split" in self.index.columns:
                index = self.index.drop(["_split"], axis=1)
            else:
                index = self.index
            if "_file" not in self.index.columns:
                index["_file"] = []
            if len(index) == 0:
                self.index = index
                return  # if no data is selected.
            grouped = index.groupby("_file")
            dfs_split = []
            for _, df_file in grouped:
                df_split = df_file[index_names[:split_depth]].drop_duplicates()
                df_split["_split"] = range(len(df_split))
                dfs_split.append(df_split)
            df_split = pd.concat(dfs_split)
            self.index = index.merge(df_split, on=index_names[:split_depth])
            self.index = self.index.reindex(
                index_names + ["_file", "_split"], axis=1)
        else:
            self.index["_file"] = 0
            self.index["_split"] = 0

    def get_dict(self):
        """Return a dictionary of all information for saving.

        Returns:
            dict: Dictionary of column, param and meta dictionaries
        """
        return {"column": self.column, "param": self.param, "meta": self.meta}

    def add_column(self, depth, name, type, unit, description):
        """Add column information of data hierarchy.

        Frequently used in :meth:`slitflow.data.Data.set_info()`.

        Args:
            depth (int): Column depth. If None then set as the last depth + 1.
            name (str): Column name used for :class:`pandas.DataFrame`
                columns.
            type (str): Value type.
            unit (str): Unit of column value.
            description (str): Explanation of column value.
        """

        if name in self.get_column_name("all"):
            self.delete_column(name)
        if depth is None:
            self.sort_index()
            depth = len(self.get_column_name("index")) + 1
        if depth > 0:
            if depth in self.get_column_depth():
                self.insert_depth(depth)
        dict = {"depth": depth, "name": name, "type": type, "unit": unit,
                "description": description}
        self.column.append(dict)
        self.sort_column()

    def insert_depth(self, insert_depth):
        """Add 1 to the depth after the specified depth.

        Args:
            insert_depth (int): First index depth at which you want to shift
                depth.
        """
        index_names = self.get_column_name("index")[insert_depth - 1:]
        for i in range(0, len(self.column)):
            if self.column[i]["name"] in index_names:
                self.column[i]["depth"] = self.column[i]["depth"] + 1

    def copy_req_columns(self, req_no=0, names=None):
        """Import column info from required data info.

        Frequently used in :meth:`slitflow.data.Data.set_info()`.

        Args:
            req_no (int, optional): Index of required data list. Defaults to 0.
            names (list of str, optional): Column names to copy from req.
                All columns are copied if None. Defaults to None.
        """
        if names is None:
            names = self.Data.reqs[req_no].info.get_column_name("all")
        for name in names:
            col_dict = self.Data.reqs[req_no].info.get_column_dict(name)
            self.add_column(col_dict["depth"], col_dict["name"],
                            col_dict["type"], col_dict["unit"],
                            col_dict["description"])

    def delete_column(self, names=None, keeps=None):
        """Delete column information.

        Frequently used in :meth:`slitflow.data.Data.set_info()`.

        Args:
            names (list of str, optional): Column names to delete.
                All columns are deleted if None. Defaults to None.
            keeps (list of str, optional): Column names not to delete.
        """
        if isinstance(names, str):
            names = [names]
        if keeps is not None:
            names = self.get_column_name()
            names = [name for name in names if name not in keeps]
        del_nos = []
        for name in names:
            for i in range(0, len(self.column)):
                if self.column[i]["name"] == name:
                    del_nos.append(i)
        self.column = [col for del_no, col in enumerate(self.column)
                       if del_no not in del_nos]

    def get_column_name(self, type="all"):
        """Get column names from the column property.

        Args:
            type (str) : Column type to return

                * ``all`` : all column names.
                * ``index`` : column names whose depth > 0.
                * ``col`` : column names that do not belong to the index.

        Returns:
            list of str: List of column names
        """
        if type == "all":
            return [d["name"] for d in self.column if d is not None]
        elif type == "index":
            return [d["name"] for d in self.column if d["depth"] > 0]
        elif type == "col":
            return [d["name"] for d in self.column if d["depth"] == 0]

    def change_column_item(self, name, item, new_value):
        """Change a column item.

        Used when you want to change a item in the column information.
        e.g.  int32 to float32 in "type".

        Args:
            name (str): Column name.
            item (str): Column item to change. The item should be "depth",
                "type", "unit" or "description".
            new_value (str): New value.
        """
        col_dict = self.get_column_dict(name)
        col_dict[item] = new_value
        self.delete_column(name)
        self.add_column(col_dict["depth"], name, col_dict["type"],
                        col_dict["unit"], col_dict["description"])

    def get_column_type(self):
        """Get column type dict for DataFrame dtype.

        Returns:
            dict: Dictionary of column types
        """
        type_dict = {}
        names = [d["name"] for d in self.column]
        types = [d["type"] for d in self.column]
        for name, type in zip(names, types):
            type_dict[name] = type
        return type_dict

    def get_column_dict(self, name):
        """Return dictionary of selected column information.

        Args:
            name (str): Column name to select.

        Returns:
            dict: "name", "type", "unit" and "description" of the column
        """
        col_dict = [d for d in self.column if d["name"] == name]
        if len(col_dict) == 0:
            raise Exception(name + " is not found in columns.")
        elif len(col_dict) == 1:
            return col_dict[0].copy()
        else:
            raise Exception("More than one " + name + " is found.")

    def get_column_depth(self, name=None):
        """Get column depth list.

        Args:
            name (str): Column name to get depth number.

        Returns:
            list: List of depth number
        """
        if name is None:
            return [d["depth"] for d in self.column]
        else:
            return [d["depth"] for d in self.column if d["name"] == name][0]

    def reset_depth(self, name, depth=None):
        """Change the depth of selected column.

        Args:
            name (str): Column name to change depth.
            depth (int, optional): Target depth. If not specified, then the
                deepest depth + 1 is set. Defaults to None.
        """
        if depth is None:
            for i in range(0, len(self.column)):
                if self.column[i]["name"] == name:
                    self.column[i]["depth"] = max(
                        self.get_column_depth()) + 1
        else:
            for i in range(0, len(self.column)):
                if self.column[i]["name"] == name:
                    self.column[i]["depth"] = depth

    def sort_index(self):
        """Rewrite depth so that there are no missing index numbers.
        """
        cols = self.get_column_name("index")
        for i, name in enumerate(cols):
            self.reset_depth(name, i + 1)

    def sort_column(self):
        """Sort column dictionaries according to depth.
        """
        df = pd.DataFrame(self.column)
        unindexed = df[df["depth"] == 0]
        indexed = df[df["depth"] > 0].sort_values("depth")
        df = pd.concat([indexed, unindexed])
        self.column = df.to_dict(orient="records")

    def add_param(self, name, value, unit, description):
        """Add parameter dictionary to the param property.

        Frequently used in :meth:`slitflow.data.Data.set_info()`.

        Args:
            name (str): Parameter name.
            value (any): Parameter value.
            unit (str) : Unit of parameter value.
            description (str) : Explanation of parameter.
        """
        for d in self.get_param_names():
            if d == name:
                self.delete_param(name)
        dict = {"name": name, "value": value, "unit": unit,
                "description": description}
        self.param.append(dict)

    def copy_req_params(self, req_no=0, names=None):
        """Reuse parameters from the information of required data.

        Frequently used in :meth:`slitflow.data.Data.set_info()`.

        Args:
            req_no (int, optional): Index of required data list. Defaults to 0.
            names (list of str, optional): Parameter names to copy from req.
                All parameters are copied if None. Defaults to None.
        """
        if names is None:
            names = self.Data.reqs[req_no].info.get_param_names()
        for name in names:
            param_dict = self.Data.reqs[req_no].info.get_param_dict(name)
            self.add_param(param_dict["name"], param_dict["value"],
                           param_dict["unit"], param_dict["description"])

    def delete_param(self, name):
        """Delete selected parameter from params.

        Args:
            name (str): Parameter name to delete.
        """
        for i in range(0, len(self.param)):
            if self.param[i]["name"] == name:
                del self.param[i]
                return

    def delete_private_param(self):
        """Delete parameters containing _ prefix.

        The parameter prefixed with "_" is used when the same large parameter
        is needed for all processes. This method is used in
        :meth:`slitflow.data.Data.post_run()` when you have
        registered with :meth:`slitflow.data.Data.set_info()` but do
        not want to save it in the info file.

        """
        names = self.get_param_names()
        del_names = [name for name in names if name[0] == "_"]
        if len(del_names) > 0:
            for del_name in del_names:
                self.delete_param(del_name)

    def add_user_param(self, param):
        """Add user-defined parameters from param["user_param"].

        Args:
            param (dict): Parameter dictionary containing the "user_param"
                item. param["user_param"] should be list of list contain [name,
                value, unit, description].
        """
        if "user_param" in param:
            for user_param in param["user_param"]:
                self.add_param(*user_param)

    def get_param_names(self):
        """Return parameter names from the param property.

        Returns:
            list of str: List of parameter names
        """
        return [d["name"] for d in self.param]

    def get_param_value(self, name):
        """Return parameter value from the param property.

        Args:
            name (str) : Parameter name to get the value.

        Returns:
            any : Value of selected parameter
        """
        for d in self.param:
            if d["name"] == name:
                return d["value"]

    def get_param_dict(self, name=None):
        """Return dictionary of selected parameter information.

        Args:
            name (str, optional): Parameter name to select.

        Returns:
            dict: "name", "type", "unit" and "description" of the parameter
        """
        if name is None:
            param_dict = {}
            for d in self.param:
                param_dict[d["name"]] = d["value"]
            return param_dict
        else:
            for d in self.param:
                if d["name"] == name:
                    return d

    def set_split_depth(self, depth):
        """Set split depth into parameter dictionary.

        .. caution::

            This method is used in
            :meth:`slitflow.data.Data.set_info()` to set how to split
            the result data. If you want split load data, please use
            :meth:`split()`.

        Args:
            depth (int): File split depth number.
        """
        self.add_param("split_depth", depth, "num", "File split depth number")

    def split_depth(self):
        """Return split depth of the result data.
        """
        return self.get_param_value("split_depth")

    def set_group_depth(self, depth):
        """Add index_cols into param.

        This method adds the "index_cols" parameter to split data using
        :meth:`pandas.DataFrame.groupby`.

        Args:
            depth (int): Data grouping depth number.
        """

        self.add_param("group_depth", depth, "num", "DataFrame groupby depth")
        self.add_param("index_cols", self.group_cols(),
                       "list of str", "Index columns for groupby")

    def group_depth(self):
        """Return group depth number.

        Returns:
            int: Group depth number
        """
        return self.get_param_value("group_depth")

    def group_cols(self):
        """Return index column names for groupby of DataFrame.

        Returns:
            list of str: List of index column names
        """
        return self.get_column_name("index")[:self.group_depth()]

    def copy_req(self, req_no=0, type="all", names=None):
        """Import column and parameter info from required data.

        Args:
            req_no (int, optional): List number of required data.
            type (str, optional): "all", "column", "index" or "param".
            names (list of str, optional): List of copy names.
        """
        if type == "all":
            self.copy_req_columns(req_no)
            self.copy_req_params(req_no)
        elif type == "column":
            self.copy_req_columns(req_no, names)
        elif type == "index":
            names = self.Data.reqs[req_no].info.get_column_name("index")
            self.copy_req_columns(req_no, names)
        elif type == "param":
            self.copy_req_params(req_no, names)

    def set_meta(self):
        """Set meta data.

        Analysis records, including path, timestamp, and required data
        information, are created in :attr:`meta` property to save them into the
        info file.

        """
        reqs_dict = {}
        if self.Data.reqs is not None:
            for i, req in enumerate(self.Data.reqs):
                if len(req.info.meta) > 0:
                    req.info.meta["reqs"] = {}
                reqs_dict["req_" + str(i)] = req.info.get_dict()
        now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        dict = {"version": __version__, "class": fullname(self.Data),
                "description": self.Data.__class__.__doc__.splitlines()[0],
                "datetime": now, "path": self.path, "reqs": reqs_dict}
        self.meta = dict

    def to_json(self):
        """Returns a string representation of info file to export.

        .. caution::

            Private parameters will be removed.

        Returns:
            str: a string representation of info file
        """
        self.delete_private_param()
        if not self.meta:
            self.set_meta()
        return json.dumps(self.get_dict(), indent=2)

    def get_depth_id(self):
        """Return depth id used in data file names.

        This id is used in split file names.

        Returns:
            list of str: List of depth id string. The id format is
            "D[depth 1 value]D[depth 2 value]...".

        """

        if self.split_depth() == 0:
            return None
        else:
            df = self.file_index().iloc[:, :self.split_depth()]
            numbers = df.drop_duplicates().values
            depth_ids = []
            for vals in numbers:
                depth_id = ""
                for val in vals:
                    depth_id = depth_id + "D" + str(int(val))
                depth_ids.append(depth_id)
        return depth_ids


def fullname(o):
    """Returns full name of object.

    Args:
        o (object): Object.

    Returns:
        str: Full name of object
    """
    klass = o.__class__
    module = klass.__module__
    return module + "." + klass.__name__
