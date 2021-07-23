import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')


factor_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/factor_data.csv"
factor_data = pd.read_csv(factor_path)

GSS = factor_data[["GL", "SC", "LE", "RS"]]
GSS["GL"] = GSS["GL"].apply(lambda x: x * 0.06)
table2a = GSS.describe().T
table2a.to_excel("/Users/meron/Desktop/01_Work/panjiva/logger/Table_2A.xlsx")

table2b = factor_data.corr(method="spearman")
table2b.to_excel("/Users/meron/Desktop/01_Work/panjiva/logger/Table_2B.xlsx")
