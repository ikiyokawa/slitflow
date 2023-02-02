import os
import re
import glob
import json


def make_info_path(root_dir, grp_no, ana_no, obs_name,
                   ana_name=None, grp_name=None):
    grp_id = "g" + str(grp_no)
    if grp_name is not None:
        if type(grp_name) == float:
            grp_name = None
        elif len(grp_name) == 0:
            grp_name = None
    if grp_name is None:  # find from folder
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
    return os.path.join(ana_dir, obs_name + "_" + ana_name + ".sf")


def split_info_path(info_path):
    if info_path[-3:] == ".sf":
        info_path = os.path.splitext(info_path)[0]
    ana_path, file_name = os.path.split(info_path)
    _, ana_dir = os.path.split(ana_path)
    result = re.match("a.*?_", ana_dir)
    ana_name = ana_dir[result.end():]
    obs_name = file_name[:-len(ana_name) - 1]
    return ana_path, obs_name, ana_name


def make_data_paths(Info, ext):
    depth_ids = Info.get_depth_id()
    if depth_ids is None:  # data path is the same as info path
        info_path = os.path.splitext(Info.path)[0] + ext
        return [info_path]
    ana_path, obs_name, ana_name = split_info_path(Info.path)
    data_paths = []
    for depth_id in depth_ids:
        file_name = obs_name + "_" + depth_id + "_" + ana_name + ext
        data_paths.append(os.path.join(ana_path, file_name))
    return natural_sort(data_paths)


def load_data_paths(Info, ext):
    ana_path, obs_name, ana_name = split_info_path(Info.path)
    path = os.path.join(ana_path, obs_name
                        + "_*" + ana_name + ext)
    data_paths = glob.glob(path)
    data_paths = list(set(data_paths) - set([Info.path]))
    return natural_sort(data_paths)


def make_group(root_dir, grp_no, grp_name):
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
    grp_no = req_address[0]
    ana_no = req_address[1]
    path_wildcard = os.path.join(root_dir, "g" + str(grp_no) + "_*")
    grp_path = glob.glob(path_wildcard)[0]
    path_wildcard = os.path.join(grp_path, "a" + str(ana_no) + "_*")
    ana_paths = glob.glob(path_wildcard)
    if len(ana_paths) == 1:
        ana_path = glob.glob(path_wildcard)[0]
    elif len(ana_paths) > 1:
        raise Exception("More than one analysis folders are found.")
    else:
        return None
    info_path_wildcard = os.path.join(ana_path, "*.sf")
    info_paths = glob.glob(info_path_wildcard)
    obs_names = []
    for info_path in info_paths:
        _, obs_name, _ = split_info_path(info_path)
        obs_names.append(obs_name)
    return obs_names


def get_class_name(path):
    if path[-3:] == ".sf":
        path = os.path.splitext(path)[0]
    with open(path + ".sf") as f:
        info = json.load(f)
    meta = info["meta"]
    class_name = meta["class"]
    class_name = class_name.replace("slitflow", "sf") + "()"
    return class_name


def get_data_paths(info_path):
    ana_path, obs_name, ana_name = split_info_path(info_path)
    path = os.path.join(ana_path, obs_name
                        + "_*" + ana_name + ".*[!.sf]")
    data_paths = glob.glob(path)
    data_paths = list(set(data_paths) - set([info_path]))
    return natural_sort(data_paths)


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def natural_sort(list_to_sort):
    return sorted(list_to_sort, key=natural_keys)
