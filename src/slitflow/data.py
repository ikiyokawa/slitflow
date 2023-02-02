import numpy as np
import psutil
import os

from .info import Info
from . import name as nm
from tqdm import tqdm
from . import setindex

from . import CPU_RATE
from . import MEMORY_LIMIT


class Data():

    def __init__(self, info_path=None):
        self.reqs = None
        self.data = []
        self.info = Info(self, info_path)
        self.n_worker = np.max(
            [np.floor(os.cpu_count() * CPU_RATE).astype(int), 1])
        self.memory_limit = MEMORY_LIMIT * 100

    def load(self, file_nos=None):
        self.info.set_file_nos(file_nos)
        if ~hasattr(self.info, "data_paths"):
            self.info.data_paths = nm.load_data_paths(self.info, self.EXT)
        dfs = []
        for i, path in enumerate(self.info.data_paths):
            if psutil.virtual_memory().percent > self.memory_limit:
                raise Exception("Memory usage limit reached.")
            if i in self.info.file_nos:
                dfs.append(self.load_data(path))
        self.data = dfs
        self.split(self.info.split_depth())

    def load_data(self, path):
        pass

    def save(self):
        self.split(self.info.split_depth())
        self.info.data_paths = nm.make_data_paths(self.info, self.EXT)
        for data, path in zip(self.data, self.info.data_paths):
            if data is not None:
                self.save_data(data, path)
        self.info.save()
        self.data = []

    def save_data(self, data, path):
        pass

    def split(self, split_depth):
        self.info.split(split_depth)
        if len(self.data) > 0:
            self.split_data()

    def split_data(self):
        pass

    def set_reqs(self, reqs=None, param=None):
        if reqs is None:
            reqs = []
        if len(reqs) == 0:
            self.reqs = [Data()]
            self.reqs[0].info = Info(Data())
            self.reqs[0].data = [np.nan]
        else:
            self.reqs = reqs

    def set_info(self, param={}):
        pass

    def set_index(self):
        setindex.from_req(self, 0)

    def run(self, reqs=None, param=None):
        if reqs is not None:
            self.set_reqs(reqs, param)
        if param is not None:
            self.set_info(param)
        reqs_data = []
        for req in self.reqs:
            reqs_data.append(req.data)
        reqs_data = list(zip(*reqs_data))
        param = self.info.get_param_dict()
        for req_data in tqdm(reqs_data, leave=False):
            if psutil.virtual_memory().percent > self.memory_limit:
                raise Exception("Memory usage limit reached.")
            self.data.append(self.process(list(req_data), param))
        self.post_run()
        self.info.set_meta()
        self.set_index()
        self.split(self.info.split_depth())

    def post_run(self):
        pass

    @ staticmethod
    def process(reqs, param={}):
        return reqs[0]
