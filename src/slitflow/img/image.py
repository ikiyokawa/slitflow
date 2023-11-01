import numpy as np
import pandas as pd
import tifffile as tf
import psutil
import cv2

from ..data import Data
from .. import setindex


class Image(Data):
    """Stack of Two-dimensional image Data class saved as tiff files.

    Images are loaded upside down to facilitate picking up pixel value.
    See also :class:`~slitflow.data.Data` for properties and methods.
    Concrete subclass is mainly in :mod:`slitflow.img`.

    """
    EXT = ".tif"

    def __init__(self, info_path=None):
        super().__init__(info_path)

    def load_data(self, path):
        """Load tiff file as :class:`numpy.ndarray`.
        """
        stacks = []
        with tf.TiffFile(path, mode="r+b") as tif:
            img = tif.pages[0].asarray()
            total_page = len(tif.pages)
            stack = np.zeros([total_page, img.shape[0], img.shape[1]],
                             dtype=img.dtype)
            for i in np.arange(0, total_page):
                if psutil.virtual_memory().percent > self.memory_limit:
                    raise Exception("Memory usage limit reached.")
                stack[i, :, :] = np.flipud(tif.pages[i].asarray())
            stacks.append(stack)
        return np.concatenate(stacks, axis=0)

    def save_data(self, stack, path):
        """Save :class:`numpy.ndarray` data into tiff file.
        """
        if stack.size == 0:
            return

        col_name = self.info.get_column_name(type="col")
        col_dict = self.info.get_column_type()
        stack = stack.astype(col_dict[col_name[0]])

        with tf.TiffWriter(path) as tif:
            for i in np.arange(0, stack.shape[0]):
                tif.write(np.flipud(stack[i, :, :]),
                          photometric="minisblack",
                          contiguous=True, description="",
                          resolution=(1, 1))

    def split_data(self):
        """Splits the list of 3D np.array based on the index DataFrame.
        """

        index = self.info.index.copy()
        data_concat = np.concatenate(self.data, axis=0)

        # Adjust the data type of the data_concat
        col_name = self.info.get_column_name(type="col")
        col_dict = self.info.get_column_type()
        data_concat = data_concat.astype(col_dict[col_name[0]])

        # Transform the index DataFrame by creating and merging "_pos" column
        index_cols = [
            col for col in index.columns if col not in ["_split", "_dest"]]
        index_concat = index.loc[index["_split"] != 0, index_cols + ["_split"]]
        index_concat.drop_duplicates(inplace=True)
        index_concat["_pos"] = np.arange(len(index_concat)) + 1
        index = pd.merge(index, index_concat,
                         on=index_cols + ["_split"], how="left")
        index["_pos"] = index["_pos"].fillna(0).astype(int)

        # Sort unique dest values by absolute values and filter out zeros
        unique_dests = sorted(
            [dest for dest in index['_dest'].unique() if dest != 0], key=abs)

        # Split the data based on the unique dest values
        data_list = []
        for dest in unique_dests:
            if dest < 0:
                data_list.append(None)
            else:
                dest_pos = index[index["_dest"] == dest]["_pos"].values
                filtered_data = data_concat[dest_pos - 1]
                combined_data = np.concatenate(
                    [arr[np.newaxis] for arr in filtered_data], axis=0)
                data_list.append(combined_data.astype(data_concat.dtype))

        self.data = data_list

    def set_info(self, param={}):
        """Convert input information to Info object.

        This method creates columns and parameters information. The columns
        information is used to handle data structure. The parameter
        dictionaries are set as param of :meth:`process`.
        This method is called before :meth:`run`. Implemented in subclass.

        Args:
            param (dict, optional): Parameters for columns or params.
        """
        self.info.copy_req(0)
        self.info.set_split_depth(param["split_depth"])

    def to_imshow(self, position):
        """Convert image to use in :func:`matplotlib.pyplot.imshow`.

        Returns:
            numpy.ndarray: Grayscale image according to imshow format
        """
        stack = np.concatenate(self.data, axis=0)
        img = np.flipud(stack[int(position), :, :])
        return img.astype(stack.dtype)


def set_img_size(self):
    """Set the image size to the param info in pixel.

    This function is used in :meth:`~slitflow.data.Data.post_run`
    to append image size information into the result information.

    """
    self.info.delete_param("img_size")
    img_size = [self.data[0].shape[2], self.data[0].shape[1]]
    self.info.add_param("img_size", img_size, "pix",
                        "[width, height] of image in pixel")


class RGB(Image):
    """Stack of RGB color image class saved as tiff files.

    uint8, uint16 color can be saved as color tiff stack.
    float32 color can be saved as hyperstack tiff.

    """

    def __init__(self, info_path=None):
        super().__init__(info_path)

    def load_data(self, path):
        """Load tiff file as :class:`numpy.ndarray`.
        """
        stacks = []
        with tf.TiffFile(path, mode="r+b") as tif:
            img = tif.pages[0].asarray()
            total_page = len(tif.pages)
            stack = np.zeros([total_page * 3, img.shape[0], img.shape[1]],
                             dtype=img.dtype)
            cnt = 0
            for i in np.arange(0, total_page):
                if psutil.virtual_memory().percent > self.memory_limit:
                    raise Exception("Memory usage limit reached.")
                rgb = tif.pages[i].asarray()
                stack[cnt, :, :] = np.flipud(rgb[:, :, 0])
                cnt += 1
                stack[cnt, :, :] = np.flipud(rgb[:, :, 1])
                cnt += 1
                stack[cnt, :, :] = np.flipud(rgb[:, :, 2])
                cnt += 1
            stacks.append(stack)
        return np.concatenate(stacks, axis=0)

    def save_data(self, stack, path):
        """Save :class:`numpy.ndarray` data into tiff file.
        """
        if stack.size == 0:
            return

        col_name = self.info.get_column_name(type="col")
        col_dict = self.info.get_column_type()
        stack = stack.astype(col_dict[col_name[0]])

        if "pitch" in self.info.get_param_names():
            pitch = 1 / self.info.get_param_value("pitch")
        else:
            pitch = 1
        with tf.TiffWriter(path) as tif:
            for i in np.arange(0, stack.shape[0] / 3):
                img_r = stack[int(3 * i), :, :]
                img_g = stack[int(3 * i + 1), :, :]
                img_b = stack[int(3 * i + 2), :, :]
                rgb = np.zeros([img_r.shape[0], img_r.shape[1], 3])
                rgb[:, :, 0] = np.flipud(img_r)
                rgb[:, :, 1] = np.flipud(img_g)
                rgb[:, :, 2] = np.flipud(img_b)
                rgb = rgb.astype(stack.dtype)
                tif.write(rgb,
                          photometric="rgb",
                          contiguous=True,
                          description="Created by Slitflow",
                          resolution=(pitch, pitch))

    def set_index(self):
        """How to get :attr:`slitflow.info.Info.index`.

        Default function for RGB is :func:`set_color_index`.

        """
        setindex.from_req_plus_color(self, 0)

    def to_imshow(self, position):
        """Convert image to use in :func:`matplotlib.pyplot.imshow`.

        Returns:
            numpy.ndarray: Color image according to imshow format
        """
        stack = np.concatenate(self.data, axis=0)
        img_r = stack[int(3 * position), :, :]
        img_g = stack[int(3 * position + 1), :, :]
        img_b = stack[int(3 * position + 2), :, :]
        rgb = np.zeros([img_r.shape[0], img_r.shape[1], 3])
        rgb[:, :, 0] = np.flipud(img_r)
        rgb[:, :, 1] = np.flipud(img_g)
        rgb[:, :, 2] = np.flipud(img_b)
        return rgb.astype(stack.dtype)


def set_color_index(Data, req_no, index_depth):
    """Set color index.

    The color index is a number to represent color. 1:R, 2:G, 3:B.

    """
    Data.info.copy_req(req_no, "column")
    index_names = Data.info.get_column_name("index")
    Data.info.delete_column(keeps=index_names[:index_depth])
    Data.info.add_column(None, "color", "int32", "no",
                         "Color number 1:R,2:G,3:B")
    Data.info.add_column(0, "intensity", "uint8",
                            "a.u.", "Pixel intensity")
    Data.info.index = Data.reqs[req_no].info.index.copy()
    dfs = []
    df_color = pd.DataFrame({"color": np.array([1, 2, 3])})
    if len(Data.info.index) == 0:
        Data.info.index = df_color
    else:
        for _, row in Data.info.index.iterrows():
            df_index = pd.DataFrame([row]).reset_index(drop=True)
            df = pd.concat([df_index, df_color], axis=1)
            dfs.append(df.fillna(method="ffill"))
        Data.info.index = pd.concat(dfs).astype(int)
    Data.info.set_index_file_no()
