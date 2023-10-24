import os
import sys
import re
import gc
import shutil
import json
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from netgraph import Graph, get_sugiyama_layout
if 'ipykernel' in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

import slitflow as sf  # used in eval
from . import name as nm
from . import info, setreqs, data
from .name import get_obs_names
from .name import make_info_path as ipath


class Pipeline():
    """Manage the sequential running of the Data class and file IO.

    Attributes:
        root_dir (str): File path to the project directory.
        df (pandas.DataFrame): Pipeline table consisting of a series of data
            classes.

    """

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.init_df()
        self.init_folder()

    def init_df(self):
        """Create a pipeline table.
        """
        cols = ["class_name", "run_mode", "address", "grp_name", "ana_name",
                "obs_names", "reqs_address", "reqs_split", "param"]
        self.df = pd.DataFrame(index=[], columns=cols)

    def init_folder(self):
        """Make the project folder if it doesn't exist.
        """
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)
        path = os.path.join(self.root_dir, "g0_config")
        if not os.path.exists(path):
            os.mkdir(path)

    def save(self, sheet_name):
        """Export the pipeline table as a CSV file.

        The CSV file is saved in the g0_config folder.

        Args:
            sheet_name (str): Pipeline CSV file name without extension.
        """
        sheet_name = sheet_name + ".csv"
        path = os.path.join(self.root_dir, "g0_config", sheet_name)
        self.df.to_csv(path, index=False, encoding="shift-jis")

    def load(self, sheet_names):
        """Import pipeline table from the CSV file.

        The CSV file is loaded from the g0_config folder.

        Args:
            sheet_names (str or list of str): Pipeline CSV file name without
                extension.
        """
        if isinstance(sheet_names, str):
            sheet_names = [sheet_names]
        for sheet_name in sheet_names:
            sheet_name = sheet_name + ".csv"
            path = os.path.join(self.root_dir, "g0_config", sheet_name)
            df = pd.read_csv(path, encoding="shift-jis")
            for _, row in df.iterrows():
                self.add(row.class_name, row.run_mode,
                         row.address, row.grp_name, row.ana_name,
                         row.obs_names, row.reqs_address, row.reqs_split,
                         row.param)

    def add(self, class_name, run_mode, address, grp_name, ana_name, obs_names,
            reqs_address, reqs_split, param):
        """Add a task to the pipeline table.

        Args:
            class_name (str): Class name string.
            run_mode (int): Run mode (0=single data, single CPU; 1=single data
                , multi CPU; 2=multi data, multi CPU; 3=multi data, multi CPU).
            address (tuple): (group no, analysis no) to save the task.
            grp_name (str): Group name.
            ana_name (str): Analysis name.
            obs_names (list of str): List of observation names that are used
                for data file names.
            reqs_address (list of tuple): List of (group no, analysis no) of
                required data files.
            reqs_split (list of int): List of ``split_depth`` to resplit
                required data.
            param (dict): Parameter dictionary.
        """
        class_name = self.set_class_name(class_name)
        run_mode = self.set_run_mode(run_mode)
        address = self.set_address(address)
        grp_name = self.set_grp_name(address, grp_name)
        ana_name = self.set_ana_name(ana_name)
        reqs_address = self.set_reqs_address(reqs_address)
        obs_names = self.set_obs_names(obs_names)
        reqs_split = self.set_reqs_split(reqs_split, reqs_address)
        param = self.set_param(param)
        row = pd.Series([class_name, run_mode, address, grp_name, ana_name,
                         obs_names, reqs_address, reqs_split, param],
                        index=self.df.columns)
        self.df.loc[len(self.df)] = row

    def set_class_name(self, class_name):
        """Standardize various type of class_name to formatted string.

        Args:
            class_name (Data or str): Input to set the class name.

        Returns:
            str: :func:`eval()` executable class_name string. "slitflow"
            package can be imported as "sf".
        """
        if isinstance(class_name, data.Data):
            class_name = info.fullname(class_name)
        elif not isinstance(class_name, str):
            raise Exception("Set class name as string.")
        class_name = re.sub("^slitflow", "sf", class_name)
        if class_name[:2] == "sf" or class_name[:4] == "Copy" or\
                class_name[:6] == "Delete":
            if class_name[-2:] == "()":
                return class_name
            else:
                return class_name + "()"
        else:
            raise Exception("class_name is invalid. (" + class_name + ")")

    def set_run_mode(self, run_mode):
        """Convert run mode to integer.

        Args:
            run_mode (int or str): Input to set the run mode.

        Returns:
            int: Run mode number (0=single data, single CPU; 1=single data,
            multi CPU; 2=multi data, multi CPU; 3=multi data, multi CPU).
        """
        if isinstance(run_mode, int):
            pass
        elif isinstance(run_mode, str):
            run_mode = int(run_mode)
        if run_mode not in range(4):
            raise Exception("Set run mode number. (number,data,process)=\
                (0,s,s),(1,s,m),(2,m,s),(3,m,m). s=single,m=multi.")
        return run_mode

    def set_address(self, address):
        """Check address format.

        Args:
            address (tuple of int, or str): Input address should be (group_no,
                analysis_no).

        Returns:
            tuple of int: (group_no, analysis_no)
        """
        if address is None:
            return None
        elif isinstance(address, str):
            address = eval(address)
        elif isinstance(address, tuple):
            pass
        else:
            raise Exception("Set address as tuple (group_no, analysis_no).")
        if len(address) != 2:
            raise Exception("Address tuple should be (group_no, analysis_no).")
        return address

    def set_grp_name(self, address, grp_name):
        """Check input group name.

        Additional restrictions will be written here.

        Args:
            address (tuple of int, or str): Input address should be (group_no,
                analysis_no).
            grp_name (str): Group name to check.

        Returns:
            str: Group name
        """
        if address is None:
            return ""
        if not grp_name or (grp_name == "") or \
                (not isinstance(grp_name, str) and np.isnan(grp_name)):
            grp_id = "g" + str(address[0])
            path = os.path.join(self.root_dir, grp_id + "_*")
            if len(glob.glob(path)) > 0:
                grp_dir = glob.glob(path)[0]
                end_no = re.match(".*" + grp_id + "_", grp_dir).end()
                grp_name = grp_dir[end_no:]
            else:
                grp_name = ""
        if not isinstance(grp_name, str):
            raise Exception("Group name should be string.")
        return grp_name

    def set_ana_name(self, ana_name):
        """Check input analysis name.

        Additional restrictions will be written here.

        Args:
            ana_name (str): Analysis name to check.

        Returns:
            str: Analysis name
        """
        if not isinstance(ana_name, str):
            raise Exception("Analysis name should be string.")
        return ana_name

    def set_reqs_address(self, reqs_address):
        """Check required addresses.

        Args:
            reqs_address (list of tuple): List of (group_no, analysis_no) of
                required data.

        Returns:
            list of tuple: List of required data address
        """
        if isinstance(reqs_address, str):
            reqs_address = eval(reqs_address)
        elif isinstance(reqs_address, list):
            reqs_address = reqs_address.copy()
        elif reqs_address is None:
            reqs_address = []
        else:
            raise Exception(
                "Set address as list of tuple (group_no, analysis_no).")
        if len(reqs_address) > 0:
            for req_address in reqs_address:
                if not isinstance(req_address, tuple):
                    raise Exception(
                        "Set address as tuple (group_no, analysis_no).")
                if len(req_address) != 2:
                    raise Exception(
                        "Address tuple should be(group_no, analysis_no).")
        return reqs_address

    def set_obs_names(self, obs_names):
        """Check and convert observation names.

        Args:
            obs_names (list or str): List of observation names.

        Returns:
            list of str: Observation names
        """
        if obs_names is None:
            obs_names = []
        else:
            if isinstance(obs_names, str):
                obs_names = eval(obs_names)
            elif isinstance(obs_names, list):
                obs_names = obs_names.copy()
            if len(obs_names) != 0:
                for obs_name in obs_names:
                    if not isinstance(obs_name, str):
                        raise Exception("Set obs_names as list of string.")
        return obs_names

    def set_reqs_split(self, reqs_split, reqs_address):
        """Check and convert split depth to resplit required data.

        Args:
            reqs_split (list or str): List of ``split_depth`` of required data.
            reqs_address (list of tuple): List of required address to check
                then number of required data.

        Returns:
            list of int: List of ``split_depth`` of required data
        """
        if isinstance(reqs_split, str):
            reqs_split = eval(reqs_split)
        elif type(reqs_split) in (list, np.ndarray):
            reqs_split = reqs_split.copy()
        elif reqs_split is None:
            return []
        else:
            raise Exception("Set split_depth as list of numbers.")
        if len(reqs_address) != len(reqs_split):
            raise Exception(
                "Numbers of reqs_address and reqs_split are not identical.")
        return reqs_split

    def set_param(self, param):
        """Check parameter dictionary.

        Args:
            param (dict, str, or None): Input to set as a parameter
                dictionary.

        Returns:
            dict: Parameter dictionary
        """
        if isinstance(param, str):
            return eval(param)
        elif isinstance(param, dict):
            return param.copy()
        elif param is None:
            return None
        else:
            raise Exception("Set param as dictionary.")

    def run(self, sheet_name=None, indices=None):
        """Run selected tasks.

        Args:
            sheet_name (str, optional): Pipeline CSV file name without
                extension.
            indices (list of int, optional): Task indices to run.

        """
        if sheet_name is not None:
            self.load(sheet_name)
        indices = self.convert_indices(indices)
        print("Run All start...")
        for index, row in self.df.iterrows():  # repeat task
            if index not in indices:
                continue
            class_name = row.class_name
            print("Task start... " + class_name)
            run_mode = row.run_mode
            address = row.address
            grp_name = row.grp_name
            ana_name = row.ana_name
            reqs_address = row.reqs_address
            obs_names = self.load_obs_names(row.obs_names, reqs_address)
            reqs_split = row.reqs_split
            param = row.param

            if class_name in \
                ["sf.tbl.convert.Obs2Depth()",
                 "sf.img.convert.Obs2Depth()",
                 "sf.img.convert.Obs2DepthRGB()"]:
                self.run_Obs2Depth(class_name, reqs_split, reqs_address,
                                   obs_names, param, grp_name,
                                   ana_name, run_mode, address)
            elif class_name == "Delete()":
                self.run_delete(reqs_address, obs_names, param)
            elif class_name == "Copy()":
                self.run_copy(address, ana_name, grp_name, reqs_address,
                              obs_names, param)
            else:
                for obs_name in tqdm(obs_names):  # repeat observation
                    if run_mode < 2:
                        self.run_one_data(class_name, reqs_split, reqs_address,
                                          obs_name, param, grp_name,
                                          ana_name, run_mode, address)
                    else:
                        self.run_multi_data(
                            class_name, reqs_split, reqs_address, obs_name,
                            param, grp_name, ana_name, run_mode,
                            address)
                    plt.close()

    def load_obs_names(self, obs_names, reqs_address):
        """Get observation names from saved files if obs_names is empty list.

        Args:
            obs_names (list): Observation names. Empty list is required to
                execute this method.
            reqs_address (list of tuple): List of required address tuples.
                The first address is used to pick up observation names.

        Returns:
            list of str: List of observation names
        """
        if len(obs_names) == 0:
            obs_names = get_obs_names(self.root_dir, reqs_address[0])
        return obs_names

    def convert_indices(self, indices=None):
        """Standardize the indices argument of run method.

        Args:
            indices (None or int or tuple or list): Task row indices to

                * None : run all rows.
                * int : run a row of selected directly.
                * list : run rows of selected directly.
                * tuple : run rows of selected by (start, end, step(optional)). tuple[1]==0 make select to the last row.

        Returns:
            pandas.Int64Index: Task row indices to run

        Examples:
            When index of self.df is reset:

            .. code-block:: python

                >>> self.convert_indices()
                self.df.index
                >>> self.convert_indices(-1)
                pd.Index([self.df.index[-1]])
                >>> self.convert_indices([1, -1])
                pd.Index([self.df.index[1], self.df.index[-1]])
                >>> self.convert_indices(range(3))
                self.df.index[:3]
                >>> self.convert_indices((1, -1))
                self.df.index[1:-1]
                >>> self.convert_indices((1, 0, 2))
                self.df.index[1::2]

        """
        index_buf = self.df.index
        if indices is None:
            return index_buf
        elif isinstance(indices, tuple):
            if len(indices) == 3:
                if indices[1]:
                    return index_buf[indices[0]:indices[1]:indices[2]]
                else:
                    return index_buf[indices[0]::indices[2]]
            elif indices[1]:
                return index_buf[indices[0]:indices[1]]
            else:
                return index_buf[indices[0]:]
        ln = len(index_buf)
        if isinstance(indices, (int, float, np.number)):
            lind = [ln + indices if indices < 0 else indices]
        else:  # array-like
            lind = [ln + indx if indx < 0 else indx for indx in indices]
        return pd.Index(lind)

    def run_one_data(self, class_name, reqs_split, reqs_address,
                     obs_name, param, grp_name, ana_name, run_mode,
                     address):
        """Execute a task that is not split into multiple files.

        Args:
            class_name (str): :func:`eval()` executable class name string.
            reqs_split (list): List of split depth of each required data.
            reqs_address (list of tuple): List of required data address.
            obs_name (list of str): Observation names.
            param (dict): Parameter dictionary.
            grp_name (str): Group name.
            ana_name (str): Analysis name.
            run_mode (int): Run mode number. This should be 0 or 1.
            address (tuple): (group_no, analysis_no) of the result data.
        """
        D = eval(class_name)
        D.info.set_path(ipath(self.root_dir, address[0], address[1],
                              obs_name, ana_name, grp_name))
        reqs = []
        for req_address, req_split in zip(reqs_address, reqs_split):
            info_path = ipath(
                self.root_dir, req_address[0], req_address[1], obs_name)
            req_class_name = nm.get_class_name(info_path)
            R = eval(req_class_name)
            R.info.load(info_path)
            R.load()
            R.split(req_split)
            reqs.append(R)
        if run_mode == 1:
            D.run_mp(reqs, param)
        else:
            D.run(reqs, param)

        D.save()
        del D
        gc.collect()

    def run_multi_data(self, class_name, reqs_split, reqs_address,
                       obs_name, param, grp_name, ana_name,
                       run_mode, address):
        """Execute a task that is split into multiple files.

        Args:
            class_name (str): :func:`eval()` executable class_name string.
            reqs_split (list): List of split depth of each required data.
            reqs_address (list of tuple): List of required data address.
            obs_name (list of str): Observation names.
            param (dict): Parameter dictionary.
            grp_name (str): Group name.
            ana_name (str): Analysis name.
            run_mode (int): Run mode number. This should be 0 or 1.
            address (tuple): (group_no, analysis_no) of the result data.
        """
        D = eval(class_name)
        D.info.set_path(ipath(self.root_dir, address[0], address[1],
                              obs_name, ana_name, grp_name))
        reqs = []
        for req_address, req_split in zip(reqs_address, reqs_split):
            info_path = ipath(
                self.root_dir, req_address[0], req_address[1], obs_name)
            req_class_name = nm.get_class_name(info_path)
            R = eval(req_class_name)
            R.info.load(info_path)
            reqs.append(R)
        if "split_depth" not in param:
            param["split_depth"] = reqs[0].info.split_depth()
        reqs_file_nos, save_nos = setreqs.set_reqs_file_nos(
            reqs, param["split_depth"])
        # if reqs are not required
        if len(reqs_file_nos) == 0:
            raise Exception("Mode 2,3 are not available.")
        else:
            for reqs_file_no, save_no in tqdm(
                    zip(reqs_file_nos, save_nos), leave=False,
                    total=len(save_nos)):
                for req, req_split, req_file_no in zip(
                        reqs, reqs_split, reqs_file_no):
                    if ~np.isnan(req_file_no):
                        req.load(req_file_no)
                        req.split(req_split)
                D.info.set_file_nos(save_no)
                if run_mode == 3:
                    D.run_mp(reqs, param)
                else:
                    D.run(reqs, param)
                if ~np.isnan(save_no):
                    D.save()
        del D
        gc.collect()

    def run_Obs2Depth(self, class_name, reqs_split, reqs_address,
                      obs_names, param, grp_name, ana_name,
                      run_mode, address):
        """Merge different observations into one observation with depth.

        .. caution::

            Currently only run_mode=0 is supported.

        Args:
            class_name (str): :func:`eval()` executable class_name string.
            reqs_split (list): List of split depth of each required data.
            reqs_address (list of tuple): List of required data address.
            obs_name (list of str): Observation names.
            param (dict): Parameter dictionary.
            grp_name (str): Group name.
            ana_name (str): Analysis name.
            run_mode (int): Run mode number. This should be 0 or 1.
            address (tuple): (group_no, analysis_no) of the result data.
            param (dict): Parameter dictionary. This should have the
                below item.
            param["obs_name"] (str): Newly created observation name.

        """
        D = eval(class_name)
        D.info.set_path(ipath(self.root_dir, address[0], address[1],
                              param["obs_name"], ana_name, grp_name))
        param["merged_obs_names"] = obs_names
        reqs = []
        for obs_name, req_address in zip(obs_names, reqs_address):
            req_info_path = nm.make_info_path(
                self.root_dir, req_address[0], req_address[1], obs_name)
            req_class_name = nm.get_class_name(req_info_path)
            R = eval(req_class_name)
            R.info.load(req_info_path)
            R.info.set_split_depth(0)
            R.load()
            reqs.append(R)
        D.run(reqs, param)
        D.save()
        del D
        gc.collect()

    def run_delete(self, reqs_address, obs_names, param):
        """Delete selected data.

        Args:
            reqs_address (list of tuple): List of (group name, analysis name)
                to delete.
            obs_names (list of str): Observation names to delete.
            param (dict, optional): Parameter dictionary. param would have the
                below item.
            param["keep"] (str, optional): Defines delete type.

                * ``info`` : Not delete information files.
                * ``folder`` : Delete the information files but not the folder itself.

        """
        if "keep" not in param:
            param = {"keep": "none"}
        for req_address in reqs_address:
            for obs_name in obs_names:
                info_path = ipath(
                    self.root_dir, req_address[0], req_address[1], obs_name)
                if info_path:
                    req_class_name = nm.get_class_name(info_path)
                    R = eval(req_class_name)
                    R.info.load(info_path)
                    for data_path in nm.load_data_paths(R.info, R.EXT):
                        if os.path.exists(data_path):
                            os.remove(data_path)
                    if os.path.exists(info_path + "x"):
                        os.remove(info_path + "x")
                    if param["keep"] in ["folder", "none"]:
                        if os.path.exists(info_path):
                            os.remove(info_path)
                    if param["keep"] == "none":
                        try:
                            os.rmdir(os.path.dirname(info_path))
                        except OSError as e:
                            pass  # existing other files

    def run_copy(self, address, ana_name, grp_name, reqs_address, obs_names,
                 param):
        """Copy data from a different analysis.

        Args:
            address (tuple): (group_no, analysis_no) of copy destination.
            ana_name (str): Analysis name.
            grp_name (str): Group name.
            reqs_address (list of tuple): List containing only one data
                address of copy source.
            obs_names (list of str): List containing only one observation
                name of copy destination.
            param (dict): Parameter dictionary. This should have the
                below item.
            param["obs_name"] (str): Observation name of copy source.

        """
        if len(reqs_address) > 1:
            raise Exception("Only one req address is allowed.")
        else:
            req_address = reqs_address[0]
        if len(obs_names) > 1:
            raise Exception("Only one observation is allowed.")
        else:
            new_obs_name = obs_names[0]
        if grp_name == "":
            raise Exception("Group name must be defined explicitly.")

        new_info_path = ipath(
            self.root_dir, address[0], address[1], new_obs_name, ana_name,
            grp_name)
        new_dir = os.path.dirname(new_info_path)

        src_info_path = ipath(
            self.root_dir, req_address[0], req_address[1], param["obs_name"])
        _, _, src_ana_name, src_grp_name = nm.split_info_path(src_info_path)
        src_class_name = nm.get_class_name(src_info_path)

        R = eval(src_class_name)
        R.info.load(src_info_path)
        for src_data_path in nm.load_data_paths(R.info, R.EXT):
            src_data_name = os.path.basename(src_data_path)
            # change data file name
            new_data_name = src_data_name.replace(
                src_grp_name + "_" + src_ana_name, grp_name + "_" + ana_name)
            new_data_name = new_data_name.replace(
                param["obs_name"], new_obs_name)
            new_data_path = os.path.join(new_dir, new_data_name)
            if os.path.exists(src_data_path):
                shutil.copy2(src_data_path, new_data_path)

        shutil.copy2(src_info_path, new_info_path)
        shutil.copy2(src_info_path + "x", new_info_path + "x")

        # rewrite copied info path
        with open(new_info_path) as f:
            info = json.load(f)
            info["meta"]["path"] = new_info_path
        with open(new_info_path, "w") as f:
            json.dump(info, f, indent=2)

    def make_flowchart(self, fig_name, label_type, is_vertical=False,
                       scale=(0.5, 1), format="png", dpi=300):
        """Create workflow graph into the g0_config directory.

        Args:
            fig_name (str): Name of the flowchart file.
            label_type (str): Description type. This should be

                * "class_desc" : shows the one-line class description from class docstring.
                * "grp_ana" : shows "grp_name (newline) ana_name".

            is_vertical (bool): Flowchart direction. Defaults to False
                (horizontal).
            scale (tuple of int): Scale factors of (width, height).
            format (str): File save format. Defaults to "png".
            dpi (int): Dot per inch of exporting file.
        """

        graph_df = self.df[["address", "grp_name", "ana_name",
                            "reqs_address", "class_name"]].copy()
        graph_df["address"] = graph_df["address"].apply(lambda x: str(x))
        graph_df["reqs_address"] = graph_df["reqs_address"].\
            apply(lambda x: str(x))
        graph_df = graph_df.drop_duplicates()

        # fill grp_name and set grp color
        graph_df.loc[:, "grp_no"] = graph_df["address"].\
            apply(lambda x: eval(x)[0])
        grp_df = graph_df[["grp_name", "grp_no"]].copy().dropna()
        grp_colors = []
        for i in range(len(grp_df)):
            grp_colors.append(rgb2hex(plt.cm.Pastel1(np.mod(i, 8))[:-1]))
        grp_df["grp_color"] = grp_colors
        for _, row in grp_df.iterrows():
            graph_df.loc[
                graph_df["grp_no"] == row.grp_no, "grp_name"] = row.grp_name
            graph_df.loc[
                graph_df["grp_no"] == row.grp_no, "grp_color"] = row.grp_color

        # fill description
        graph_df["description"] = graph_df["class_name"].apply(lambda x: eval(
            re.sub("slitflow", "sf", x)[:-2]
            + ".__doc__.splitlines()[0]"))

        # replace address
        node_df = graph_df[["address"]].reset_index(drop=True).reset_index()
        node_df = node_df.rename(columns={"index": "id"})
        for _, row in node_df.iterrows():
            graph_df["reqs_address"] = graph_df["reqs_address"].\
                str.replace(row.address, str(row.id), regex=False)
            graph_df["address"] = graph_df["address"].\
                str.replace(row.address, str(row.id), regex=False)
        graph_df["address"] = graph_df["address"].apply(lambda x: eval(x))
        graph_df["reqs_address"] = graph_df["reqs_address"].apply(
            lambda x: eval(x))

        # set class type
        graph_df["class_type"] = graph_df["class_name"].apply(
            lambda x: re.findall(r'sf\.(.*?)\.', x)[0])
        class_colors = [["img", rgb2hex(plt.cm.Set1(0)[:-1])],
                        ["tbl", rgb2hex(plt.cm.Set1(1)[:-1])],
                        ["trj", rgb2hex(plt.cm.Set1(2)[:-1])],
                        ["loc", rgb2hex(plt.cm.Set1(3)[:-1])],
                        ["fig", rgb2hex(plt.cm.Set1(4)[:-1])],
                        ["load", rgb2hex(plt.cm.Set1(5)[:-1])],
                        ["dev", rgb2hex((0.3, 0.3, 0.3))],
                        ["user", rgb2hex((0.3, 0.3, 0.3))]]
        for class_color in class_colors:
            graph_df.loc[graph_df["class_type"] == class_color[0],
                         "class_color"] = class_color[1]

        # make graph
        edges = []
        node_labels = {}
        for _, row in graph_df.iterrows():
            if label_type == "grp_ana":
                node_labels[row.address] = '\n'.join(
                    [row.grp_name, row.ana_name])
            elif label_type == "class_desc":
                node_labels[row.address] = '\n'.join(
                    [row.class_name, row.description])
            else:
                raise Exception(
                    'label_type should be "grp_ana" or "class_desc".')
            reqs = row.reqs_address
            if len(reqs) == 0:
                continue
            for req in reqs:
                edges.append((req, row.address))
        nodes = list(range(len(node_labels)))
        node_pos = get_sugiyama_layout(
            edges, nodes=nodes, scale=scale, origin=(0, 0))
        if is_vertical:
            node_label_offset = (0.03, 0)
            align = "left"
        else:
            node_pos = {node: (-x, y) for node, (y, x) in node_pos.items()}
            node_label_offset = (0, 0.06)
            align = "center"

        # make figure
        fig, ax = plt.subplots()
        g = Graph(edges, nodes=nodes, node_layout=node_pos,
                  node_labels=node_labels,
                  arrows=True, node_label_offset=node_label_offset,
                  node_label_fontdict=dict(
                      family="Arial", size=6, horizontalalignment=align))
        for i in range(len(g.node_artists)):
            g.node_artists[i].set_facecolor(graph_df["grp_color"].values[i])
            g.node_artists[i].set_edgecolor(graph_df["class_color"].values[i])
        path = os.path.join(self.root_dir, "g0_config", fig_name + ".png")
        plt.savefig(path, format=format, dpi=dpi,
                    bbox_inches='tight', pad_inches=0)
