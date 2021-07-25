import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
from scipy import stats

warnings.filterwarnings('ignore')


def Single_factor(factor, ret, groups, f_u, wgt="vw"):
    """
     一次性测试多个因子
    :param factor: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param groups: 分成多少组来测
    :return: cumulative product return for stocks with different groups
    """
    # factor = factor_data
    # f_u = "GL"
    # f_t = "ccc"
    # groups = 5
    # ret = return_data
    # wgt = "vw"


    wgt = wgt + "r"

    # f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="inner")
    # f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="right")

    year_list = factor['year'].unique()
    group_list = range(1, groups + 1)




    # f_t 是基本面因子
    f_t_names = ['Size', 'BM', 'GPM',
                 'Accruals', 'InvI', 'ccc',
                 wgt + '_1', wgt + '_12',
                 'Leverage', 'CAPEXI', 'RDI',
                 ]
    # f_t_names = ["Size", wgt + '_1']
    f_t_data = []
    for f_t in f_t_names:
        print(f_u, f_t)
        if (f_t != wgt + '_1') and (f_t != wgt + '_12'):
            f_use = factor[['gvkey', 'year', f_u, f_t]]

        else:
            f_use = factor[['gvkey', 'year', f_u]]

        f_use = f_use.dropna(how='any')

        f_use['groups'] = f_use.groupby("year")[f_u].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))

        val_y_p = {}

        # y = year_list[0]
        # g = group_list[0]
        for y in year_list:

            val_g_p = {}
            # val_g_t = {}
            print(y)
            for g in group_list:
                print(g)

                # g = group_list[0]

                f_u_sub = f_use[(f_use['year'] == y) & (f_use['groups'] == g)]
                f_u_ttl = pd.DataFrame(np.repeat(f_u_sub.values, 12, axis=0))
                f_u_ttl.columns = f_u_sub.columns
                f_u_ttl["month"] = np.tile(range(1, 13), len(f_u_sub))  # 添加月份

                if (f_t != wgt + '_1') and (f_t != wgt + '_12'):
                    f_u_ttl = pd.merge(f_u_ttl[['gvkey', 'year', 'month', f_u, f_t]],
                                       ret[['gvkey', 'year', 'month', wgt]],
                                       on=['year', 'month', 'gvkey'], how='left')
                    f_u_ttl = f_u_ttl.dropna(how="any")
                    # f_u_ttl.head()
                else:
                    f_u_ttl = pd.merge(f_u_ttl[['gvkey', 'year', 'month', f_u]],
                                       ret[['gvkey', 'year', 'month', wgt, f_t]],
                                       on=['year', 'month', 'gvkey'], how='left')
                    f_u_ttl = f_u_ttl.dropna(how="any")

                if not f_u_sub.empty:
                    X_data = sm.add_constant(f_u_ttl[[f_u, f_t]], has_constant='add')
                    y_data = f_u_ttl[wgt]
                    result = sm.OLS(y_data, X_data).fit()
                    para = result.params[0]
                    val_g_p[g] = para
                else:
                    val_g_p[g] = None

            val_y_p[y] = val_g_p

        p_rslt = pd.DataFrame(val_y_p)
        p_rslt = p_rslt.iloc[::-1, :]
        p_rslt.index = list(p_rslt.index)[::-1]

        p_df = p_rslt.mean(axis=1)
        t_df = p_rslt.apply(lambda x: stats.ttest_1samp(x, 0.0, nan_policy='omit')[0], axis=1)

        # t_df = pd.DataFrame(val_y_t).mean(axis=1)
        rslt = pd.concat([p_df, t_df], axis=1).T
        rslt.iloc[0, :] = rslt.iloc[0, :] * 100
        rslt.iloc[0, :] = rslt.iloc[0, :].round(3)
        rslt.iloc[1, :] = rslt.iloc[1, :].round(2)
        rslt.iloc[1, :] = rslt.iloc[1, :].apply(lambda x: "(" + str(x) + ")")

        rslt["factor"] = f_t
        print(rslt)
        f_t_data.append(rslt)
    result_df = pd.concat(f_t_data, axis=0)

    return result_df


# region 载入数据
factor_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/factor_data.csv"
factor_data = pd.read_csv(factor_path)
factor_data = factor_data[[
    'gvkey', 'year', 'GL', 'SC', 'RS', 'LE',
    'Size', 'BM', 'GPM',
    'Accruals', 'InvI', 'ccc',
    'Leverage', 'CAPEXI', 'RDI']]

GSS = factor_data.loc[:, ['gvkey', 'year', 'GL', 'SC', 'RS', 'LE']]

return_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/return_data.csv"
return_data = pd.read_csv(return_path)
return_data["vwr_1"] = return_data.groupby(['gvkey']).vwr.diff()
return_data["vwr_12"] = return_data.groupby(['gvkey']).vwr.shift(12) - \
                        return_data.groupby(['gvkey']).vwr.shift(2)

return_data["ewr_1"] = return_data.groupby(['gvkey']).ewr.diff()
return_data["ewr_12"] = return_data.groupby(['gvkey']).ewr.shift(12) - \
                        return_data.groupby(['gvkey']).ewr.shift(2)

# endregion



for f_u in ["GL", "SC", "LE", "RS"]:
    rslt = Single_factor(factor_data, return_data, 4, f_u, "vw")
    rslt.to_excel(f"/Users/meron/Desktop/01_Work/panjiva/logger/Table7{f_u}.xlsx")

