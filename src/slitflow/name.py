"""
This module provides file path processing functions.
"""

import os
import re
import glob
import json

from .fun.sort import natural_sort


def make_info_path(root_dir, grp_no, ana_no, obs_name,
                   ana_name=None, grp_name=""):
    """Return an info path with creating all folders required.

    Args:
        root_dir (str): Top level project directory path.
        grp_no (int): Group number.
        ana_no (int): Analysis number.
        obs_name (str): Observation name.
        ana_name (str, optional): Set ana name if you make a new analysis.
        grp_name (str, optional): Set group name if you make a new group.

    Returns:
        str: Path to info JSON file with ``.sf`` extension
    """
    grp_id = "g" + str(grp_no)
    if grp_name == "":  # find from folder
        path = os.path.join(root_dir, grp_id + "_*")
        grp_dir = glob.glob(path)[0]
        end_no = re.match(".*" + grp_id + "_", grp_dir).end()
        grp_name = grp_dir[end_no:]
    else:  # create group folder
        grp_dir = make_group(root_dir, grp_no, grp_name)
    ana_id = "a" + str(ana_no)
    if ana_name is None:  # find from folder
        path = os.path.join(grp_dir, ana_id + "_*")
        ana_dirs = glob.glob(path)
        if len(ana_dirs) == 1:
            ana_dir = ana_dirs[0]
        elif len(ana_dirs) > 1:
            raise Exception("More than one analysis folders are found.")
        else:
            raise Exception("New analysis folder name is needed.")
        end_no = re.match(".*" + ana_id + "_", ana_dir).end()
        ana_name = ana_dir[end_no:]
    else:  # create analysis folder
        ana_dir = os.path.join(grp_dir, ana_id + "_" + ana_name)
        if not os.path.exists(ana_dir):
            os.mkdir(ana_dir)
    return os.path.join(ana_dir, obs_name + "_" + grp_name + "_"
                        + ana_name + ".sf")


def split_info_path(info_path):
    """Split info path string into part names.

    Args:
        info_path (str): Path to an information JSON file.

    Returns:
        Tuples containing

        - ana_path (str): path to the analysis folder
        - obs_name (str): observation name
        - ana_name (str): analysis name without extension
        - grp_name (str): group name without extension
    """
    if info_path[-3:] == ".sf":
        info_path = os.path.splitext(info_path)[0]
    ana_path, file_name = os.path.split(info_path)
    grp_path, ana_dir = os.path.split(ana_path)
    _, grp_dir = os.path.split(grp_path)
    ana_id_ = re.match("a.*?_", ana_dir)
    grp_id_ = re.match("g.*?_", grp_dir)
    ana_name = ana_dir[ana_id_.end():]
    grp_name = grp_dir[grp_id_.end():]
    obs_name = file_name[:-len(grp_name) - len(ana_name) - 2]
    return ana_path, obs_name, ana_name, grp_name


def make_data_paths(Info, ext):
    """Create a set of data paths.

    Args:
        Info (Info): Information object.
        ext (str): Data file extension.

    Returns:
        list of str: List of paths to the data files
    """
    depth_ids = Info.get_depth_id()
    if depth_ids is None:  # data path is the same as info path
        info_path = os.path.splitext(Info.path)[0] + ext
        return [info_path]
    ana_path, obs_name, ana_name, grp_name = split_info_path(Info.path)
    data_paths = []
    for depth_id in depth_ids:
        file_name = obs_name + "_" + depth_id + "_" + grp_name + "_" + ana_name + ext
        data_paths.append(os.path.join(ana_path, file_name))
    return natural_sort(data_paths)


def load_data_paths(Info, ext):
    """Find saved data and create the path list.

    Args:
        Info (Info): Information object.
        ext (str): Data file extension.

    Returns:
        list of str: List of paths to the data files
    """
    ana_path, obs_name, ana_name, grp_name = split_info_path(Info.path)
    path = os.path.join(ana_path, obs_name
                        + "_*" + grp_name + "_" + ana_name + ext)
    data_paths = glob.glob(path)
    data_paths = list(set(data_paths) - set([Info.path]))
    return natural_sort(data_paths)


def make_group(root_dir, grp_no, grp_name):
    """Create a group folder.

    Args:
        root_dir (str): Path to the project directory.
        grp_no (int): Group number.
        grp_name (str): Group name.

    Returns:
        str: Path to the group directory
    """
    grp_id = "g" + str(grp_no)
    grp_dir = os.path.join(root_dir, grp_id + "_" + grp_name)
    if os.path.exists(grp_dir):
        return grp_dir
    path_wildcard = os.path.join(root_dir, grp_id + "_*")
    if len(glob.glob(path_wildcard)) > 0:
        raise Exception("Group No." + str(grp_no) + " is used as other name.")
    else:
        os.mkdir(grp_dir)
    return grp_dir


def get_obs_names(root_dir, req_address):
    """Return observation names from existing folder.

    Args:
        root_dir (str): Path to the project directory.
        req_address (tuple of int): (group number, analysis number) of
            the directory to search observations names.

    Returns:
        list of str: List of observation names
    """
    grp_no = req_address[0]
    ana_no = req_address[1]
    path_wildcard = os.path.join(root_dir, "g" + str(grp_no) + "_*")
    grp_path = glob.glob(path_wildcard)[0]
    path_wildcard = os.path.join(grp_path, "a" + str(ana_no) + "_*")
    ana_paths = glob.glob(path_wildcard)
    if len(ana_paths) == 1:
        ana_path = ana_paths[0]
    elif len(ana_paths) > 1:
        raise Exception("More than one analysis folders are found.")
    else:
        return None
    info_path_wildcard = os.path.join(ana_path, "*.sf")
    info_paths = glob.glob(info_path_wildcard)
    obs_names = []
    for info_path in info_paths:
        _, obs_name, _, _ = split_info_path(info_path)
        obs_names.append(obs_name)
    return obs_names


def get_class_name(info_path):
    """Return the class name string from info meta data.

    Args:
        info_path (str): Path to information file with ``.sf`` extension.

    Returns:
        str: :func:`eval()` executable class_name string
    """
    if info_path[-3:] == ".sf":
        info_path = os.path.splitext(info_path)[0]
    with open(info_path + ".sf") as f:
        info = json.load(f)
    meta = info["meta"]
    class_name = meta["class"]
    class_name = class_name.replace("slitflow", "sf") + "()"
    return class_name
