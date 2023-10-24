import numpy as np
import concurrent.futures
import psutil
import os
import sys
import pickle

from .info import Info
from . import name as nm
if 'ipykernel' in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm
from . import setindex


class Data():
    """Basic Data super class.

    All analysis classes should be subclasses of this class. In this class,
    :meth:`run` executes :meth:`process` to all split data.

    Attributes:
        info (Info): Information object containing column and parameter
            information.
        reqs (list of :class:`~slitflow.data.Data`):
            List of Data objects required to run :meth:`process` static method
            of this class.
        data (list of data such as :class:`pandas.DataFrame` or :class:`numpy.ndarray`):
            List of result data calculated by :meth:`process`.
        n_worker (int): Number of CPU used by :meth:`process`. This number is
            defined by cpu_count * :data:`slitflow.CPU_RATE`. This
            attribute is used during :meth:`run_mp`.
        memory_limit (int): Max usage of memory. This value is defined by
            :data:`slitflow.MEMORY_LIMIT`. This attribute prevents
            crashing memory during loading data and calculation.
        EXT (str): Extension of data file with ".". Implement in subclass.
    """
    MEMORY_LIMIT = 0.9
    CPU_RATE = 0.7

    def __init__(self, info_path=None):
        self.reqs = None
        self.data = []
        self.info = Info(self, info_path)
        self.n_worker = np.max(
            [np.floor(os.cpu_count() * Data.CPU_RATE).astype(int), 1])
        self.memory_limit = Data.MEMORY_LIMIT * 100

    def load(self, file_nos=None):
        """Load and split data files.
        """
        self.info.set_file_nos(file_nos)
        if not hasattr(self.info, "data_paths"):
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
        """Implement in each subclass.
        """
        pass

    def save(self):
        """Split and save data files.
        """
        self.split(self.info.split_depth())
        self.info.data_paths = nm.make_data_paths(self.info, self.EXT)
        for data, path in zip(self.data, self.info.data_paths):
            if data is not None:
                self.save_data(data, path)
        self.info.save()
        self.data = []

    def save_data(self, data, path):
        """Implement in each subclass.
        """
        print("save_data() is not defined.")

    def split(self, split_depth):
        """Split info index and data.
        """
        self.info.split(split_depth)
        if len(self.data) > 0:
            self.split_data()

    def set_split(self, split_depth):
        """Split info index and data.

        This method can be used to overwrite ``split_depth``.
        """
        self.info.set_split_depth(split_depth)
        if len(self.data) > 0:
            self.split_data()

    def split_data(self):
        """Implement in each subclass.
        """
        # split_depth is not needed as an argument because info.index already
        # has split information by self.info.split(split_depth).
        pass

    def set_reqs(self, reqs=None, param=None):
        """Preparation of required data.

        This step strongly depends on the analysis type. Frequently used
        processes are in  :mod:`slitflow.setreqs`.

        """
        if reqs is None:
            reqs = []
        if len(reqs) == 0:
            self.reqs = [Data()]
            self.reqs[0].info = Info(Data())
            self.reqs[0].data = [np.nan]
        else:
            self.reqs = reqs

    def set_info(self, param={}):
        """Convert input information to Info object.

        This method creates columns and parameters information. The columns
        information is used to handle data structure. The parameter
        dictionaries are set as param of :meth:`process`.
        This method is called before :meth:`~slitflow.data.Data.run`.
        Implemented in subclass.

        Args:
            param (dict, optional): Parameters for columns or params.
        """
        pass

    def set_index(self):
        """Create index structure of this analysis data.

        This step strongly depends on the analysis type. Frequently used
        processes are in :mod:`slitflow.setindex`.

        """
        setindex.from_req(self, 0)

    def run(self, reqs=None, param=None):
        """Execute a series of processes to all data.

        Args:
            reqs (list of any): List of required data.
            param (dict): Dictionary of parameters.
        """
        if reqs is not None:
            self.set_reqs(reqs, param)
        if param is not None:
            self.set_info(param)
        self.info.add_user_param(param)

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

    def run_mp(self, reqs=None, param=None):
        """Execute run method using multiple CPU.

        This method uses :class:`~concurrent.futures.ProcessPoolExecutor`.

        """
        if reqs is not None:
            self.set_reqs(reqs, param)
        if param is not None:
            self.set_info(param)
        self.info.add_user_param(param)

        reqs_data = []
        for req in self.reqs:
            reqs_data.append(req.data)
        reqs_data = list(zip(*reqs_data))
        param = self.info.get_param_dict()
        futures = []
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=self.n_worker) as executor:
            for req_data in reqs_data:
                future = executor.submit(
                    self.process, list(req_data), param)
                futures.append(future)
            data_list = []
            for x in tqdm(futures, leave=False):
                data_list.append(x.result())
            self.data.extend(data_list)
        self.post_run()
        self.info.set_meta()
        self.set_index()
        self.split(self.info.split_depth())

    def post_run(self):
        """Implement in each subclass.

        This method is used when an additional process is required. Example;
        the addition of the index into a calculated data table and the
        calculated result into param information.

        """
        pass

    @ staticmethod
    def process(reqs, param={}):
        """Calculation code.
        """
        return reqs[0]


class Pickle(Data):
    """Pickle Data class.

    .. warning::

        Pickle Data class is not recommended for data inaccessibility of saved
        data. It is recommended to create subsequent export classes that
        convert binary data to a table or image.

    """
    EXT = '.pickle'

    def __init__(self, info_path=None):
        super().__init__(info_path)

    def load_data(self, path):
        """Load pickle data.
        """
        with open(path, "rb") as f:
            return pickle.load(f)

    def split_data(self):
        """Pickle object can not be split.
        """
        if len([x for x in self.data if x is not None]) == 0:
            return  # e.g. data.load.xxx.FromFolder

    def save_data(self, data, path):
        """Save pickle data.
        """
        with open(path, "wb") as f:
            pickle.dump(data, f)
