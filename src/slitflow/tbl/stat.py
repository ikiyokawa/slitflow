
import numpy as np
import pandas as pd
from scipy import stats

import importlib  # for scikit_posthocs
import itertools

from .table import Table
from ..fun.misc import reduce_list as rl


class Mean(Table):
    """Averaged value of a specific column.

    Args:
        reqs[0] (Table): Target Table for averaging.
        param["calc_col"] (str): Column name for averaging.
        param["index_cols"] (list of str, optional): Column names to gather
            rows. If you set ["img_no"], average values are calculated for
            each image number.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Summarized Table containing average, std, sem and count columns

    Examples:
        Calculate the Ensemble-averaged MSD.

        .. code-block:: python

            # D3 is from the trj.msd.Each example
            D4 = sf.tbl.stat.Mean()
            D4.run([D3],{"calc_col": "msd", "index_cols": ["interval"],
                         "split_depth": 0})
            print(D4.data[0])
            #    interval       msd       std       sem  count       sum
            # 0       0.0  0.000000  0.000000  0.000000      6  0.000000
            # 1       0.1  0.034335  0.014093  0.005754      6  0.206012
            # 2       0.2  0.065532  0.023673  0.009665      6  0.393195
            # 3       0.3  0.116515  0.031346  0.012797      6  0.699089
            # 4       0.4  0.138391  0.066066  0.026971      6  0.830347
            # 5       0.5  0.153488  0.112978  0.046123      6  0.920926

    """

    def set_info(self, param={}):
        """Copy info from req[0] and add columns and params.
        """
        self.info.copy_req(0)

        if "index_cols" not in param:
            split_depth = self.reqs[0].info.split_depth()
            index_cols = self.reqs[0].info.get_column_name("index")
            param["index_cols"] = index_cols[:split_depth]
        self.info.delete_column(keeps=param["index_cols"])
        self.info.add_param(
            "index_cols", param["index_cols"], "list of str",
            "Index columns for groupby")

        calc_dict = self.reqs[0].info.get_column_dict(param["calc_col"])
        self.info.add_column(
            0, param["calc_col"], "float64", calc_dict["unit"],
            "Mean of " + calc_dict["description"])
        self.info.add_column(
            0, "std", "float64", calc_dict["unit"],
            "Standard deviation of " + calc_dict["description"])
        self.info.add_column(
            0, "sem", "float64", calc_dict["unit"],
            "Standard error of " + calc_dict["description"])
        self.info.add_column(
            0, "count", "int32", "num",
            "Sample number of " + calc_dict["description"])
        self.info.add_column(
            0, "sum", "float64", "num", "Sum of " + calc_dict["description"])
        self.info.add_param(
            "calc_col", param["calc_col"], "str",
            "Averaging calc column names")
        self.info.set_split_depth(param["split_depth"])
        self.info.sort_index()

    @staticmethod
    def process(reqs, param):
        """Averaged value of a specific column.

        Args:
            reqs[0] (pandas.DataFrame): Target table for averaging.
            param["calc_col"] (str): Column name for averaging.
            param["index_cols"] (list of str, optional): Column names to gather
                rows. If you set ["img_no"], average values are calculated for
                each image number.

        Returns:
            pandas.DataFrame: Summarized table containing average, std, sem
            and count columns
        """
        df = reqs[0].copy()
        col_names = df.columns
        if len(param["index_cols"]) > 0:
            col_names = param["index_cols"] + [param["calc_col"]]
            df = df.reindex(columns=col_names)
            df_new = df.groupby(
                rl(param["index_cols"]),
                as_index=False)[param["calc_col"]].agg({
                    param["calc_col"]: np.mean,
                    "std": lambda x: np.std(x, ddof=1),
                    "sem": lambda x: np.std(x, ddof=1)
                    / np.sqrt(len(x)),
                    "count": len,
                    "sum": np.sum})
        else:
            df = df.reindex(columns=col_names)
            df_new = df.agg({
                param["calc_col"]: ["mean", "std", "sem", "count", "sum"]}).T
            df_new.reset_index(inplace=True, drop=True)
            df_new.columns = [param["calc_col"], "std", "sem", "count", "sum"]
        return df_new


class Test(Table):
    """Statistics test suite.

    Args:
        reqs[0] (Table): Sample Table.
        param["sample_col"] (str): Sample column name.
        param["replicate_col"] (str): Replicate column name.
        param["calc_col"] (str): Column name to values for test.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Test result Table
    """

    def set_info(self, param={}):
        self.info.copy_req_columns(
            0, [param["sample_col"]])
        self.info.add_column(0, "que_sample_no", "int32",
                                "no", "Query sample number")

        self.info.add_column(0, "shapiro", "float64",
                                "none", "P-value of shapiro")
        self.info.add_column(0, "jarque_bera", "float64",
                                "none", "P-value of jarque_bera")
        self.info.add_column(0, "kstest", "float64",
                                "none", "P-value of kstest")
        self.info.add_column(0, "bartlett", "float64",
                                "none", "P-value of bartlett")
        self.info.add_column(0, "levene", "float64",
                                "none", "P-value of levene")
        self.info.add_column(0, "brownforsythe", "float64",
                                "none", "P-value of brownforsythe")
        self.info.add_column(0, "fligner", "float64",
                                "none", "P-value of fligner")
        self.info.add_column(0, "anova", "float64",
                                "none", "P-value of ANOVA")
        self.info.add_column(0, "kruskal", "float64",
                                "none", "P-value of Krusukal-Wallis")
        self.info.add_column(0, "ftest", "float64",
                                "none", "P-value of ftest")
        self.info.add_column(0, "ttest", "float64",
                                "none", "P-value of ttest")
        self.info.add_column(0, "pairedttest", "float64",
                                "none", "P-value of paired ttest")
        self.info.add_column(0, "welch", "float64",
                                "none", "P-value of welch")
        self.info.add_column(0, "mannwhitneyu", "float64",
                                "none", "P-value of Mann-Whitney U test")

        self.info.add_column(0, "ph_ttest", "float64",
                                "none", "P-value of ph_ttest")
        self.info.add_column(0, "tukey", "float64",
                                "none", "P-value of tukey")
        self.info.add_column(0, "dunn", "float64",
                                "none", "P-value of dunn")
        self.info.add_column(0, "dscf", "float64",
                                "none", "P-value of dscf")
        self.info.add_column(0, "conover", "float64",
                                "none", "P-value of conover")

        self.info.add_param("sample_col", param["sample_col"],
                            "str", "Sample column name")
        self.info.add_param("replicate_col", param["replicate_col"],
                            "str", "Replicate number column")
        self.info.add_param("calc_col", param["calc_col"],
                            "str", "Calculation column")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Statistics test suite.

        Args:
            reqs[0] (pandas.DataFrame): Sample table.
            param["sample_col"] (str): Sample column name.
            param["replicate_col"] (str): Replicate column name.
            param["calc_col"] (str): Column name to values for test.

        Returns:
            pandas.DataFrame: Test result table
        """
        sp = importlib.import_module("scikit_posthocs")
        df = reqs[0].copy()
        df = df[[param["sample_col"], param["replicate_col"], param["calc_col"]]]
        grouped = df.groupby(param["sample_col"])
        dfs = list(list(zip(*grouped))[1])
        vals = []
        df_selfs = []
        for df_self in dfs:
            df_selfs.append(df_self[param["sample_col"]].drop_duplicates()
                            .reset_index(drop=True))
            vals.append(df_self[param["calc_col"]].values)

        # Normality
        shapiro = [stats.shapiro(val).pvalue for val in vals]
        jarque_bera = [stats.jarque_bera(val).pvalue for val in vals]
        kstest = [stats.kstest(val, stats.norm(loc=np.mean(val),
                                               scale=np.std(val)).cdf).pvalue
                  for val in vals]
        df_self = pd.concat(df_selfs)
        df_que = df_self.copy().rename("que_" + param["sample_col"])
        df_self = pd.concat([df_self.reset_index(drop=True),
                             df_que.reset_index(drop=True)], axis=1)
        df_self["shapiro"] = shapiro
        df_self["jarque_bera"] = jarque_bera
        df_self["kstest"] = kstest

        # Homoscedasticity
        bartlett = stats.bartlett(*vals).pvalue
        bartlett = np.pad([bartlett], [0, len(vals) - 1], mode="constant",
                          constant_values=np.nan)
        df_self["bartlett"] = bartlett
        levene = stats.levene(*vals, center="mean").pvalue
        levene = np.pad([levene], [0, len(vals) - 1], mode="constant",
                        constant_values=np.nan)
        df_self["levene"] = levene
        brownforsythe = stats.levene(*vals, center="median").pvalue
        brownforsythe = np.pad([brownforsythe], [0, len(vals) - 1],
                               mode="constant", constant_values=np.nan)
        df_self["brownforsythe"] = brownforsythe
        fligner = stats.fligner(*vals).pvalue
        fligner = np.pad([fligner], [0, len(vals) - 1],
                         mode="constant", constant_values=np.nan)
        df_self["fligner"] = fligner

        # anova
        anova = stats.f_oneway(*vals).pvalue
        anova = np.pad([anova], [0, len(vals) - 1], mode="constant",
                       constant_values=np.nan)
        df_self["anova"] = anova
        kruskal = stats.kruskal(*vals).pvalue
        kruskal = np.pad([kruskal], [0, len(vals) - 1], mode="constant",
                         constant_values=np.nan)
        df_self["kruskal"] = kruskal

        # two-pairs
        val_combs = list(itertools.combinations(vals, 2))
        df_combs = list(itertools.combinations(df_selfs, 2))
        dfs_cross = []
        ftests = []
        bartletts = []
        levenes = []
        brownforsythes = []
        fligners = []
        anovas = []
        kruskals = []
        ttests = []
        pairedttests = []
        welchs = []
        mannwhitneyus = []
        for val_comb, df_comb in zip(val_combs, df_combs):
            df_sub = df_comb[0]
            df_que = df_comb[1]
            df_que = df_que.rename("que_" + param["sample_col"])
            df_cross = pd.concat([df_sub.reset_index(drop=True),
                                  df_que.reset_index(drop=True)], axis=1)
            dfs_cross.append(df_cross)

            ftests.append(ftest(val_comb[0], val_comb[1]))
            bartletts.append(stats.bartlett(*val_comb).pvalue)
            levenes.append(stats.levene(*val_comb, center="mean").pvalue)
            brownforsythes.append(stats.levene(
                *val_comb, center="median").pvalue)
            fligners.append(stats.fligner(*val_comb).pvalue)
            ttests.append(stats.ttest_ind(val_comb[0], val_comb[1]).pvalue)
            pairedttests.append(stats.ttest_rel(
                val_comb[0], val_comb[1]).pvalue)
            anovas.append(np.nan)
            kruskals.append(np.nan)
            welchs.append(stats.ttest_ind(
                val_comb[0], val_comb[1], equal_var=False).pvalue)
            mannwhitneyus.append(stats.mannwhitneyu(
                val_comb[0], val_comb[1]).pvalue)
        df_cross = pd.concat(dfs_cross)
        df_cross["ftest"] = ftests
        df_cross["bartlett"] = bartletts
        df_cross["levene"] = levenes
        df_cross["brownforsythe"] = brownforsythes
        df_cross["fligner"] = fligners
        df_cross["anova"] = anovas
        df_cross["kruskal"] = kruskals
        df_cross["ttest"] = ttests
        df_cross["pairedttest"] = pairedttests
        df_cross["welch"] = welchs
        df_cross["mannwhitneyu"] = mannwhitneyus

        # multiple comparison procedure
        ph_ttests = []
        tukeys = []
        dunns = []
        dscfs = []
        conovers = []

        p_values = sp.posthoc_ttest(vals, p_adjust="holm").values
        to_sel = np.triu(np.ones(p_values.shape), k=1) > 0
        p_values = p_values.ravel()
        ph_ttests = p_values[to_sel.ravel()]

        p_values = sp.posthoc_tukey(vals).values.ravel()
        tukeys = p_values[to_sel.ravel()]

        p_values = sp.posthoc_dunn(vals, p_adjust="holm").values.ravel()
        dunns = p_values[to_sel.ravel()]
        p_values = sp.posthoc_dscf(vals).values.ravel()
        dscfs = p_values[to_sel.ravel()]
        p_values = sp.posthoc_conover(vals, p_adjust="holm").values.ravel()
        conovers = p_values[to_sel.ravel()]

        df_cross["ph_ttest"] = ph_ttests
        df_cross["tukey"] = tukeys
        df_cross["dunn"] = dunns
        df_cross["dscf"] = dscfs
        df_cross["conover"] = conovers
        return pd.concat([df_self, df_cross])


def ftest(x1, x2):
    v1 = np.var(x1, ddof=1)
    v2 = np.var(x2, ddof=1)

    f_frozen = stats.f.freeze(dfn=len(x1) - 1, dfd=len(x2) - 1)
    p1 = f_frozen.sf(v1 / v2)
    p2 = f_frozen.cdf(v1 / v2)
    return min(p1, p2) * 2
