import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
from scipy import stats

warnings.filterwarnings('ignore')
from c_toolkit.scale import mad
from c_toolkit.factor import add_month, getICSeries, form_t_p
import matplotlib.pyplot as plt
# from c_tables.table3 import Single_factor


def get_import_proportion():
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

    firm_data = imp_data.groupby(['gvkey']).agg({'import_rate':'mean'})
    firm_data['groups'] = firm_data.apply(lambda x: np.ceil(x.rank() / (len(x) / 2)))
    # 1 - 3 是由少到大分布的

    return firm_data

firm_data = get_import_proportion()

factor_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/factor_data.csv"
factor_data = pd.read_csv(factor_path)

GSS = factor_data.loc[:, ['gvkey', 'year', 'GL', 'SC', 'RS', 'LE']]
GSS = pd.merge(GSS, firm_data, on=['gvkey'], how='left')

return_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/return_data.csv"
return_data = pd.read_csv(return_path)


rslt_ll = []
for g in [1, 2, 3]:
    rslt_list = []
    GSS_sub = GSS[GSS['groups']==g]
    for f_name in ["GL", "SC", "LE", "RS"]:
        rslt = Single_factor(factor=GSS_sub, ret=return_data, group_list=[1, 2, 3],
                             groups=3, f_name=f_name, wgt="vw")
        try:
            rslt = form_t_p(rslt)
        except:
            rslt = rslt
        rslt_list.append(rslt)
    rslt_t = pd.concat(rslt_list, axis=0)
    rslt_t["imp_rate"] = g
    rslt_ll.append(rslt_t)
rslt_total = pd.concat(rslt_ll, axis=1)
rslt_total.to_excel("/Users/meron/Desktop/01_Work/panjiva/logger/imp_fct_2.xlsx")
