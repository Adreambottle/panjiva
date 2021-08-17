"""
单因子测试
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

from c_toolkit.scale import mad

def OLS_test(data):
    X = sm.add_constant(data.iloc[:, [2, 3]], has_constant='add')
    y = data.loc[:, "return_rate"]
    result = sm.OLS(y, X).fit()
    return result.params[0]



def Single_factor_EW(factor, ret, groups, f_name="RS"):
    """
     一次性测试多个因子
    :param factor: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param groups: 分成多少组来测
    :return: cumulative product return for stocks with different groups
    """
    # factor = GSS
    # f_name = "SC"
    # ret = ret_complex
    # groups = 5

    f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="inner")

    year_list = factor['year'].unique()
    group_list = range(1, groups+1)

    f_use = f_all[['gvkey', 'year', 'return_rate', 'adj_close', f_name]]
    f_use = f_use.dropna(how='any')

    f_use['groups'] = f_use.groupby("year")[f_name].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))

    val_y_p = {}
    val_y_t = {}

    for y in year_list:

        # y = year_list[0]
        val_g_p = {}
        val_g_t = {}

        for g in group_list:

            # g = group_list[0]
            f_u_sub = f_use[(f_use['year']==y) & (f_use['groups']==g)]
            if not f_u_sub.empty:
                X_data = sm.add_constant(f_u_sub[f_name], has_constant='add')
                y_data = f_u_sub["return_rate"]
                result = sm.OLS(y_data, X_data).fit()
                para = result.params[0]
                tval = result.tvalues[0]
                val_g_p[g] = para
                val_g_t[g] = tval
            else:
                val_g_p[g] = None
                val_g_t[g] = None

        val_y_p[y] = val_g_p
        val_y_t[y] = val_g_t
    p_df = pd.DataFrame(val_y_p).mean(axis=1)
    t_df = pd.DataFrame(val_y_t).mean(axis=1)

    result_df = pd.concat([p_df, t_df], axis=1)
    return result_df


def Single_factor_VW(factor, ret, groups, f_name="RS"):
    """
     一次性测试多个因子
    :param factor: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param groups: 分成多少组来测
    :return: cumulative product return for stocks with different groups
    """
    # factor = GSS
    # ret = ret_complex
    # groups = 5

    f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="inner")

    year_list = factor['year'].unique()
    group_list = range(1, groups + 1)

    f_use = f_all[['gvkey', 'year', 'return_rate', 'adj_close', f_name]]
    f_use = f_use.dropna(how='any')

    f_use['groups'] = f_use.groupby("year")[f_name].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))

    val_y_p = {}
    val_y_t = {}

    for y in year_list:

        # y = year_list[0]
        val_g_p = {}
        val_g_t = {}

        for g in group_list:
            # g = group_list[0]
            f_u_sub = f_use[(f_use['year'] == y) & (f_use['groups'] == g)]
            if not f_u_sub.empty:
                X_data = sm.add_constant(f_u_sub[f_name], has_constant='add')
                wgt = f_u_sub["adj_close"] / sum(f_u_sub["adj_close"])
                y_data = f_u_sub["return_rate"] * wgt
                result = sm.OLS(y_data, X_data).fit()
                para = result.params[0]
                tval = result.tvalues[0]
                val_g_p[g] = para
                val_g_t[g] = tval
            else:
                val_g_p[g] = None
                val_g_t[g] = None

        val_y_p[y] = val_g_p
        val_y_t[y] = val_g_t
    p_df = pd.DataFrame(val_y_p).mean(axis=1)
    t_df = pd.DataFrame(val_y_t).mean(axis=1)

    result_df = pd.concat([p_df, t_df], axis=1)
    return result_df


def Single_factor_EW_2(factor, ret, groups, f_name="RS"):
    """
     一次性测试多个因子
    :param factor: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param groups: 分成多少组来测
    :return: cumulative product return for stocks with different groups
    """
    # factor = GSS
    # ret = ret_complex
    # groups = 5

    f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="inner")

    year_list = factor['year'].unique()
    group_list = range(1, groups+1)

    f_use = f_all[['gvkey', 'year', 'return_rate', 'adj_close', f_name]]
    f_use = f_use.dropna(how='any')

    f_use['groups'] = f_use.groupby("year")[f_name].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))


    val_g_p = {}
    val_g_t = {}

    for g in group_list:

        # g = group_list[0]
        f_u_sub = f_use[f_use['groups']==g]

        X_data = sm.add_constant(f_u_sub[f_name], has_constant='add')
        y_data = f_u_sub["return_rate"]
        result = sm.OLS(y_data, X_data).fit()
        para = result.params[0]
        tval = result.tvalues[0]
        val_g_p[g] = para
        val_g_t[g] = tval
        print(val_g_p)

    p_df = pd.Series(val_g_p)
    t_df = pd.Series(val_g_t)

    result_df = pd.concat([p_df, t_df], axis=1)
    return result_df



# region 载入数据
factor_path = r"/Users/meron/Desktop/01_Work/panjiva_data/factor.csv"
factor_data = pd.read_csv(factor_path, index_col=0)
factor_data['year'] = pd.to_datetime(factor_data['year'], format="%Y-%m-%d")

GSS = factor_data.loc[:, ['gvkey', 'year', 'GL', 'SC', 'RS', 'LE']]

ret_path = r"/Users/meron/Desktop/01_Work/panjiva_data/ret.csv"
return_data = pd.read_csv(ret_path)
return_data['year'] = pd.to_datetime(return_data['year'], format="%Y-%m-%d")
return_data['return_rate'] = mad(return_data['return_rate'], 10)

ret_single = return_data.loc[:, ['gvkey', 'year', 'return_rate']]
ret_complex = return_data.loc[:, ['gvkey', 'year', 'return_rate', 'adj_close']]
# endregion

GSS.columns


def table3():
    f_names = ['GL', 'SC', 'RS', 'LE']

    for i, f in enumerate(f_names):

        VW = Single_factor_VW(GSS, ret_complex, 5, f).T
        VW.index = ['VW_alpha', 'VW_t_stat']
        EW = Single_factor_EW(GSS, ret_complex, 5, f).T
        EW.index = ['EW_alpha', 'EW_t_stat']
        data = pd.concat([VW, EW])
        data["factor"] = f
        data["H-L"] = data.loc[:, 5] - data.loc[:, 1]
        print(data)
        if i == 0:
            data_tl = data
        else:
            data_tl = pd.concat([data_tl, data])

    # data_tl.to_excel("/Users/meron/Desktop/01_Work/panjiva/logger/Table3.xlsx")





