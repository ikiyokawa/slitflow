import sys
import os
sys.path.append(os.path.join(os.path.abspath('.'), 'src'))

import slitflow as sf

D = sf.tbl.create.Index()
D.run([],{"type": "trajectory", "index_counts": [1,2], "split_depth":0})
print(D.data[0])