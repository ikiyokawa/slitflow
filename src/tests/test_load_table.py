import pytest
import pandas as pd

import slitflow as sf


def test_SingleFile_SplitFile(tmpdir):

    path = tmpdir + "test_table.csv"
    df = pd.DataFrame({"img_no": [1, 1, 2, 2], "frm_no": [1, 2, 1, 2]})
    df.to_csv(path, index=False)

    D = sf.load.table.SingleCsv()
    D.run([], {"path": str(path), "col_info":
               [[1, "img_no", "int32", "num", "Image number"],
                [2, "frm_no", "int32", "num", "Frame number"]],
               "split_depth": 0})
    assert D.data[0].equals(df)
