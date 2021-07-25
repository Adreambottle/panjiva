import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')


ret_path = r"/Users/meron/Desktop/01_Work/panjiva_data/return_data/return_cusip.csv"
brg_path = "/Users/meron/Desktop/01_Work/panjiva_data/return_data/gvkey_sic.csv"

brg_data = pd.read_csv(brg_path).loc[:,["gvkey", "cusip"]]
brg_data = brg_data.drop_duplicates(subset=['cusip']) # 用的是9位cusip
brg_data = brg_data.reset_index().drop(['index'], axis=1)
brg_data.to_csv("/Users/meron/Desktop/01_Work/panjiva_data/return_data/gvkey_cusip.csv")

brg_data.cusip
ret_data = pd.read_csv(ret_path).loc[:,['PERMNO', 'date', 'CUSIP', 'vwretd','ewretd']]
brg_data.columns = ["gvkey", "cusip9"]



ret_data.columns = ['permno', 'date', 'cusip8', 'vwr', 'ewr']

# ret_data = pd.merge(ret_data, cusip, on=['cusip8'], how="left")
ret_data = pd.merge(ret_data, brg_data, on=['cusip9'], how="left")

cusip = ret_data.CUSIP
cusip = pd.Series(cusip.unique())
cusip.to_csv("/Users/meron/Desktop/cusip.txt", sep="\t", index=False)
cusip9 = pd.read_csv("/Users/meron/Desktop/01_Work/panjiva_data/return_data/cusip9.csv")
cusip = pd.concat([cusip, cusip9], axis=1)
cusip.columns = ["cusip8", "cusip9"]

brg = ret_data.loc[:,["permno", "cusip8", "cusip9", "gvkey"]].drop_duplicates()
brg.to_csv("/Users/meron/Desktop/01_Work/panjiva_data/return_data/bridge.csv", index=False)
ret_data.to_csv("/Users/meron/Desktop/01_Work/panjiva_data/return_data/return_gvkey.csv", index=False)
ret_data.columns
ret_data = ret_data.loc[:, ['date', 'vwr', 'ewr', 'gvkey']]


LE = pd.read_csv("/Users/meron/Desktop/01_Work/panjiva_data/LE.csv")
LE['year'] = pd.to_datetime(LE['year'], format="%Y-%m-%d")
LE['year'] = LE['year'].apply(lambda x:x.year)



factor_path = r"/Users/meron/Desktop/01_Work/panjiva_data/factor.csv"
factor_data = pd.read_csv(factor_path, index_col=0)
factor_data['date'] = pd.to_datetime(factor_data['year'], format="%Y-%m-%d")
factor_data['year'] = factor_data['date'].apply(lambda x: x.year)
factor_data = factor_data.drop(["SC"], axis=1)
factor_data = pd.merge(factor_data, SC, on=["gvkey", "year"], how="inner")
factor_data = factor_data.dropna(how="any")


GSS_dt = pd.read_csv(r"/Users/meron/Desktop/01_Work/panjiva_data/GSS_dt.csv")
# GSS_dt["year"] = GSS_dt.year.apply(lambda x: x.year)
ccc_d = GSS_dt[["gvkey", "year", "ccc"]]
factor_data = pd.merge(factor_data, ccc_d, on=["gvkey", "year"])
factor_data.columns
factor_data

factor_data = factor_data[['gvkey', 'year', 'GL', 'SC', 'LE', 'RS', 'Size', 'BM', 'GPM',
       'Leverage', 'Accruals', 'InvI', 'InvT', 'GMROI', 'CAPEXI', 'RDI',
       'ccc', 'date',]]
factor_data.to_csv("/Users/meron/Desktop/01_Work/panjiva_data/v2/factor_data.csv", index=False)

ret_path = r"/Users/meron/Desktop/01_Work/panjiva_data/return_data/return_gvkey.csv"
return_data = pd.read_csv(ret_path)
return_data['date'] = pd.to_datetime(return_data['date'], format="%Y%m%d")
return_data['year'] = return_data['date'].apply(lambda x: x.year)
return_data['month'] = return_data['date'].apply(lambda x: x.month)
return_data = return_data.dropna(how='any')
return_data.to_csv("/Users/meron/Desktop/01_Work/panjiva_data/v2/return_data.csv", index=False)

factor_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/factor_data.csv"
factor_data = pd.read_csv(factor_path)
factor_data = factor_data.drop(["LE"], axis=1)
factor_data = pd.merge(factor_data, LE, on=["gvkey", "year"], how="left")