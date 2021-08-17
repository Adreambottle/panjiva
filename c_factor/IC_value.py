"""
用于计算一个Factor 的 IC 值
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
from scipy import stats

warnings.filterwarnings('ignore')
from c_toolkit.scale import mad
from c_toolkit.factor import add_month, getICSeries, form_t_p
import matplotlib.pyplot as plt


def get_import_proportion():
    """
    获取进口金额的比例
    :return:
    """
    imp_value_path = r"/Users/meron/Desktop/01_Work/panjiva_data/import_value.csv"
    compustat_path = r"/Users/meron/Desktop/01_Work/panjiva_data/v1/compustat.csv"

    compustat_data = pd.read_csv(compustat_path, usecols=["gvkey", "fyear", "cogs"])
    compustat_data = compustat_data.rename(columns={"fyear": "year"})

    imp_data = pd.read_csv(imp_value_path, index_col=0)
    imp_data['imp_value'] = imp_data['imp_value'] / 1000
    imp_data = pd.merge(imp_data, compustat_data, on=["gvkey", "year"], how="left")
    imp_data['imp_value'] = mad(imp_data['imp_value'], 10)
    imp_data['cogs'] = mad(imp_data['cogs'], 10)

    imp_data = imp_data.dropna(how="any")
    imp_data = imp_data[(imp_data["cogs"] > 0) & (imp_data["imp_value"] > 0)]

    imp_data["import_rate"] = imp_data["imp_value"] / imp_data["cogs"]
    imp_data['import_rate'] = mad(imp_data['import_rate'], 10)

    firm_data = imp_data.groupby(['gvkey']).agg({'import_rate': 'mean'})
    firm_data['groups'] = firm_data.apply(lambda x: np.ceil(x.rank() / (len(x) / 3)))
    # 1 - 3 是由少到大分布的

    return firm_data


firm_data = get_import_proportion()

factor_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/factor_data.csv"
factor_data = pd.read_csv(factor_path)

GSS = factor_data.loc[:, ['gvkey', 'year', 'GL', 'SC', 'RS', 'LE']]
GSS = pd.merge(GSS, firm_data, on=['gvkey'], how='left')

return_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/return_data.csv"
return_data = pd.read_csv(return_path)


def cal_IC(GSS, return_data, name):
    fs = ["GL", "SC", "LE", "RS"]
    ICs = []
    for f in fs:
        IC = getICSeries(GSS, return_data, f, 'vwr')
        ICs.append(IC)
    IC_t = pd.concat(ICs, axis=1).T
    IC_pv = IC_t.mean(axis=1)
    IC_tv = IC_t.apply(lambda x: stats.ttest_1samp(x, 0.0, nan_policy='omit')[0], axis=1)

    stat = pd.concat([IC_pv, IC_tv], axis=1).T
    stat.columns = ["GL", "SC", "LE", "RS"]
    stat = form_t_p(stat)
    return stat

IC_data_l = []
for g in [1, 2, 3]:
    GSS_sub = GSS[GSS['groups']==g]
    GSS_sub = add_month(GSS_sub)
    IC_data = cal_IC(GSS_sub, return_data, g)
    IC_data_l.append(IC_data)
    IC_data["groups"] = g
IC_total = pd.concat(IC_data_l, axis=0)
IC_total.to_excel("/Users/meron/Desktop/01_Work/panjiva/logger/IC_total.xlsx")

