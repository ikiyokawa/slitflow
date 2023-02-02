import pandas as pd
import itertools

from ..tbl.table import Table


class Index(Table):
    """Dummy docstring
    """
    def set_info(self, param):
        if ("type", "trajectory") in param.items():
            self.info.add_column(
                1, "img_no", "int32", "num", "Image number")
            self.info.add_column(
                2, "trj_no", "int32", "num", "Trajectory number")
            self.info.add_param(
                "calc_cols", ["img_no", "trj_no"], "list of str",
                "Index calc column names")
        elif ("type", "image") in param.items():
            self.info.add_column(
                1, "img_no", "int32", "num", "Image number")
            self.info.add_param(
                "calc_cols", ["img_no"], "list of str",
                "Index calc column names")
        elif ("type", "movie") in param.items():
            self.info.add_column(
                1, "img_no", "int32", "num", "Image number")
            self.info.add_column(
                2, "frm_no", "int32", "num", "Trajectory number")
            self.info.add_param(
                "calc_cols", ["img_no", "frm_no"], "list of str",
                "Index calc column names")
            if "index_value" in param:
                self.info.add_param(
                    "index_value", param["index_value"], "num",
                    "Specific index value")
        else:
            for col_name in param["calc_cols"]:
                self.info.add_column(
                    None, col_name, "int32", "num", col_name + " index")
            self.info.add_param(
                "calc_cols", param["calc_cols"], "list of str",
                "Index calc column names")

        self.info.add_param(
            "index_counts", param["index_counts"], "num",
            "Total counts of each column")
        if "param" in param:
            for pp in param["param"]:
                self.info.add_param(*pp)
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        iters = []
        for i in param["index_counts"]:
            iters.append(tuple(range(1, i + 1)))
        df = pd.DataFrame(list(itertools.product(*iters)))
        df.columns = param["calc_cols"]
        if "index_value" in param:
            df[param["calc_cols"][0]] = param["index_value"]
        return df
