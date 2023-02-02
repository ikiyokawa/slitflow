import numpy as np
import pandas as pd

import json
import os
import datetime


class Info():
    def __init__(self, Data, info_path=None):
        self.Data = Data
        self.column = []
        self.param = []
        self.meta = []
        self.index = pd.DataFrame()
        self.set_path(info_path)
        self.load()

    def __str__(self):
        info_str = "Data: " + fullname(self.Data)
        if self.path is not None:
            info_str = info_str + os.linesep + "Path: " + self.path \
                + os.linesep
        else:
            info_str = info_str + os.linesep + "Path: None"
        return info_str

    def set_path(self, info_path):
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
        index_path = self.path + "idx"
        if os.path.exists(index_path):
            if os.stat(index_path).st_size == 0:
                return
            df = pd.read_csv(index_path, header=None)\
                .fillna(method="ffill").astype(np.int32)
            df.columns = self.get_column_name("index")
            if "_split" in self.index.columns:
                self.index.drop(columns=["_split"], inplace=True)
            if "_file" in self.index.columns:
                self.index.drop(columns=["_file"], inplace=True)
            self.index = pd.concat([self.index, df]).drop_duplicates()
            self.set_index_file_no()

    def save_index(self):
        self.load_index()
        index_path = self.path + "idx"
        if "_split" in self.index.columns:
            self.index.drop(columns=["_split"], inplace=True)
        if "_file" in self.index.columns:
            self.index.drop(columns=["_file"], inplace=True)
        idx = self.index.to_numpy()
        to_sel = idx[:-1, :] == idx[1:, :]
        to_sel = np.cumprod(to_sel.astype(np.int8), axis=1).astype(np.bool8)
        to_sel = np.insert(to_sel, 0, False, axis=0)
        idx = np.where(to_sel, -99999, idx)
        fmt = ','.join(['%d'] * idx.shape[1])
        fmt = '\n'.join([fmt] * idx.shape[0])
        idx = fmt % tuple(idx.ravel())
        idx = idx.replace('-99999', '')
        with open(index_path, mode="w") as f:
            f.write(idx)

    def set_index_file_no(self):
        index_names = self.get_column_name("index")
        if self.split_depth() > 0:
            grouped = self.index.groupby(index_names[:self.split_depth()])
            dfs = list(list(zip(*grouped))[1])
            for i, _ in enumerate(dfs):
                dfs[i]["_file"] = i
            self.index = pd.concat(dfs)
        else:
            self.index["_file"] = 0

    def set_file_nos(self, file_nos):
        stash_split_depth = self.split_depth()
        if file_nos is None:  # fill from index
            if len(self.index) == 0:
                file_nos = [0]
            else:
                file_nos = list(np.unique(self.index["_file"].values))
        elif np.isnan(file_nos):
            if len(self.index) == 0:
                file_nos = [0]
            else:
                file_nos = list(np.unique(self.index["_file"].values))
        elif type(file_nos) in (int, np.int64, float, np.float64):
            file_nos = [int(file_nos)]
        elif isinstance(file_nos, np.array):
            file_nos = list(file_nos.astype(int))
        else:
            raise Exception("type of file_nos is invalid.")
        self.file_nos = file_nos
        self.set_split_depth(stash_split_depth)

    def file_index(self):
        self.set_index_file_no()
        index = self.index.copy()
        if not hasattr(self, "file_nos"):
            self.set_file_nos(None)
        return index[index["_file"].isin(self.file_nos)]

    def save(self, info_path=None):
        self.set_path(info_path)
        self.delete_private_param()
        self.set_meta()
        self.save_index()
        with open(self.path, "w") as f:
            json.dump(self.get_dict(), f, indent=2)

    def split(self, split_depth=None):
        if split_depth is None:
            split_depth = self.split_depth()
        index_names = self.get_column_name("index")
        if split_depth > 0:
            if "_split" in self.index.columns:
                index = self.index.drop(["_split"], axis=1)
            else:
                index = self.index
            split = index[index_names[:split_depth]].drop_duplicates()\
                .reset_index(drop=True)
            split["_split"] = split.index
            self.index = index.merge(split, on=index_names[:split_depth])
        else:
            self.index["_split"] = 0

    def get_dict(self):
        return {"column": self.column, "param": self.param, "meta": self.meta}

    def add_column(self, depth, name, type, unit, description):
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

    def copy_req_columns(self, req_no=0, names=None):
        if names is None:
            names = self.Data.reqs[req_no].info.get_column_name("all")
        for name in names:
            col_dict = self.Data.reqs[req_no].info.get_column_dict(name)
            self.add_column(col_dict["depth"], col_dict["name"],
                            col_dict["type"], col_dict["unit"],
                            col_dict["description"])

    def delete_column(self, names=None, keeps=None):
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

    def insert_depth(self, insert_depth):
        index_names = self.get_column_name("index")[insert_depth - 1:]
        for i in range(0, len(self.column)):
            if self.column[i]["name"] in index_names:
                self.column[i]["depth"] = self.column[i]["depth"] + 1

    def get_column_name(self, type="all"):
        if type == "all":
            return [d["name"] for d in self.column if d is not None]
        elif type == "index":
            return [d["name"] for d in self.column if d["depth"] > 0]
        elif type == "col":
            return [d["name"] for d in self.column if d["depth"] == 0]

    def change_column_item(self, name, item, new_value):
        col_dict = self.get_column_dict(name)
        col_dict[item] = new_value
        self.delete_column(name)
        self.add_column(col_dict["depth"], name, col_dict["type"],
                        col_dict["unit"], col_dict["description"])

    def get_column_type(self):
        type_dict = {}
        names = [d["name"] for d in self.column]
        types = [d["type"] for d in self.column]
        for name, type in zip(names, types):
            type_dict[name] = type
        return type_dict

    def get_column_dict(self, name):
        col_dict = [d for d in self.column if d["name"] == name]
        if len(col_dict) == 0:
            raise Exception(name + " is not found in columns")
        elif len(col_dict) == 1:
            return col_dict[0].copy()
        else:
            raise Exception("More than one " + name + " is found.")

    def get_column_depth(self, name=None):
        if name is None:
            return [d["depth"] for d in self.column]
        else:
            return [d["depth"] for d in self.column if d["name"] == name][0]

    def reset_depth(self, name, depth=None):
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
        cols = self.get_column_name("index")
        for i, name in enumerate(cols):
            self.reset_depth(name, i + 1)

    def sort_column(self):
        df = pd.DataFrame(self.column)
        unindexed = df[df["depth"] == 0]
        indexed = df[df["depth"] > 0].sort_values("depth")
        df = pd.concat([indexed, unindexed])
        self.column = df.to_dict(orient="records")

    def add_param(self, name, value, unit, description):
        for d in self.get_param_names():
            if d == name:
                self.delete_param(name)
        dict = {"name": name, "value": value, "unit": unit,
                "description": description}
        self.param.append(dict)

    def copy_req_params(self, req_no=0, names=None):
        if names is None:
            names = self.Data.reqs[req_no].info.get_param_names()
        for name in names:
            param_dict = self.Data.reqs[req_no].info.get_param_dict(name)
            self.add_param(param_dict["name"], param_dict["value"],
                           param_dict["unit"], param_dict["description"])

    def delete_param(self, name):
        for i in range(0, len(self.param)):
            if self.param[i]["name"] == name:
                del self.param[i]
                return

    def delete_private_param(self):
        names = self.get_param_names()
        del_names = [name for name in names if name[0] == "_"]
        if len(del_names) > 0:
            for del_name in del_names:
                self.delete_param(del_name)

    def get_param_names(self):
        return [d["name"] for d in self.param]

    def get_param_value(self, name):
        for d in self.param:
            if d["name"] == name:
                return d["value"]

    def get_param_dict(self, name=None):
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
        self.add_param("split_depth", depth, "num", "File split depth")

    def split_depth(self):
        return self.get_param_value("split_depth")

    def set_group_depth(self, depth):
        self.add_param("group_depth", depth, "num", "DataFrame groupby depth")
        self.add_param("index_cols", self.group_cols(),
                       "list of str", "Index columns for groupby")

    def group_depth(self):
        return self.get_param_value("group_depth")

    def group_cols(self):
        return self.get_column_name("index")[:self.group_depth()]

    def copy_req(self, req_no=0, type="all", names=None):
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
        if self.Data.reqs is not None:
            reqs_dict = {}
            for i, req in enumerate(self.Data.reqs):
                if len(req.info.meta) > 0:
                    req.info.meta["reqs"] = {}
                reqs_dict["req_" + str(i)] = req.info.get_dict()
                reqs_dict["req_" + str(i)]
            now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            dict = {"class": fullname(self.Data),
                    "description": self.Data.__class__.__doc__.splitlines()[0],
                    "datetime": now, "path": self.path, "reqs": reqs_dict}
            self.meta = dict

    def get_depth_id(self):
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
    klass = o.__class__
    module = klass.__module__
    if module == "__builtin__":
        return klass.__name__
    return module + "." + klass.__name__


def row_to_data_id(row, split_depth):
    if len(row) == 0:
        return None
    if split_depth == 0:
        return None
    indexes = list(row.index)
    row = row[indexes[:split_depth]]
    row = row.drop_duplicates()
    ids = []
    for i in range(len(row)):
        depths = list(row.iloc[i, :])
        id = ""
        for depth in depths:
            id = id + "D" + str(depth)
        ids.append(id)
    return ids
