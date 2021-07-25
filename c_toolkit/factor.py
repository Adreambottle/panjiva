import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
from scipy import stats

warnings.filterwarnings('ignore')



def getICSeries(f_data, r_data, f_name, r_name, method='spearman'):
    """
    :param factor: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param method: 'pearson'，'spearman'，'kendal'
    :return: 包含所有 ic 的序列
    """
    # f_data = GSS
    # r_data = return_data
    # f_name = "RS"
    # r_name = "vwr"
    # method = "spearman"

    # 将 return rate 和 factors merge 在一起
    f_all = pd.merge(f_data[['year', 'month', 'gvkey', f_name]],
                     r_data[['year', 'month', 'gvkey', r_name]],
                     on=['year', 'month', 'gvkey'],
                     how='inner')
    f_all = f_all.dropna(how="any")
    # ic_all 得到所有 return 和 的相关系数
    ic_all = f_all.groupby(['year'])[f_name, r_name].apply(lambda x: x[f_name].corr(x[r_name], method=method))

    return ic_all

def add_month(factor:pd.DataFrame) -> pd.DataFrame:
    """
    向 data 中添加 month
    :param factor:
    :return:
    """
    f_add = pd.DataFrame(np.repeat(factor.values, 12, axis=0))
    f_add.columns = factor.columns
    f_add["month"] = np.tile(range(1, 13), len(factor))
    return f_add

def get_p_t(data):
    pass


def form_t_p(rslt):
    rslt.iloc[0, :] = rslt.iloc[0, :] * 100
    rslt.iloc[0, :] = rslt.iloc[0, :].round(3)

    rslt.iloc[1, :] = rslt.iloc[1, :].round(2)
    rslt.iloc[1, :] = rslt.iloc[1, :].apply(lambda x: "(" + str(x) + ")")
    return rslt