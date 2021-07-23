import pandas as pd
import numpy as np

factor_path = r"/Users/meron/Desktop/01_Work/panjiva_data/factor.csv"
factor = pd.read_csv(factor_path, index_col=0)
GSS = factor.loc[:, ['gvkey', 'year', 'GL', 'SC', 'RS', 'LE']]

factor_dna = factor.dropna(how="any")
gvkey = factor_dna['gvkey']
len(gvkey.unique())

f_use = factor.loc[:, ['gvkey', 'year', f1, f2]]

len(f_use[(f_use['GL_r'] == 3)])
len(f_use[(f_use['GL_r'] == 3) & (f_use['ccc_r'] == 3)])
