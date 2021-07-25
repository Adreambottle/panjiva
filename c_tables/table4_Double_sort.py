import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
from scipy import stats

warnings.filterwarnings('ignore')


def Double_factor(factor, ret, groups, f1="ccc", f2="RS", wgt="vw"):
    """
     一次性测试多个因子
    :param factor: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param groups: 分成多少组来测
    :return: cumulative product return for stocks with different groups
    """
    # factor = GSS_dt
    # f1 = "GL"
    # f2 = "InvT"
    # groups = 3
    # wgt = "vw"

    wgt = wgt + "r"
    ret = return_data.loc[:, [wgt, 'gvkey', 'year', 'month']]

    f_use = factor.loc[:, ['gvkey', 'year', f1, f2]]
    f_use[f1 + "_r"] = f_use[f1].groupby(f_use.year).apply(
        lambda x: groups + 1 - (np.ceil(x.rank() / (len(x) / groups))))
    f_use[f2 + "_r"] = f_use[f2].groupby([f_use.year,
                                          f_use[f1 + "_r"]]).apply(
        lambda x: groups + 1 - (np.ceil(x.rank() / (len(x) / groups))))
    f_use['groups'] = f_use.apply(lambda x: str(int(x[f1 + "_r"])) + '-' + str(int(x[f2 + "_r"])), axis=1)
    f_use = f_use.drop([f1 + "_r", f2 + "_r"], axis=1)

    year_list = factor['year'].unique()
    group_list = []
    for i in range(1, groups + 1):
        for j in range(1, groups + 1):
            group_list.append(str(i) + "-" + str(j))

    val_y_p = {}

    # y = 2009
    # g = '2-2'
    # group_list = ["2-2"]
    for y in year_list:

        val_g_p = {}
        print(y)
        for g in group_list:
            print(g)

            f_u_sub = f_use[(f_use['year'] == y) & (f_use['groups'] == g)]
            f_u_ttl = pd.DataFrame(np.repeat(f_u_sub.values, 12, axis=0))
            f_u_ttl.columns = f_u_sub.columns
            f_u_ttl["month"] = np.tile(range(1, 13), len(f_u_sub))
            f_u_ttl = pd.merge(f_u_ttl, ret, on=['year', 'month', 'gvkey'], how='left')
            f_u_ttl = f_u_ttl.dropna(how="any")
            # f_u_ttl.head()

            if not f_u_sub.empty:
                X_data = sm.add_constant(f_u_ttl.loc[:, [f1, f2]], has_constant='add')
                y_data = f_u_ttl[wgt]

                try:
                    result = sm.OLS(y_data, X_data.astype(float)).fit()
                    para = result.params[0]
                except:
                    para = None
                val_g_p[g] = para
            else:
                val_g_p[g] = None

        val_y_p[y] = val_g_p
    p_rslt = pd.DataFrame(val_y_p)

    p_rslt.loc["HL1"] = p_rslt.loc["3-1"] - p_rslt.loc["1-1"]
    p_rslt.loc["HL2"] = p_rslt.loc["3-2"] - p_rslt.loc["1-2"]
    p_rslt.loc["HL3"] = p_rslt.loc["3-3"] - p_rslt.loc["1-3"]

    p_df = p_rslt.mean(axis=1)
    t_df = p_rslt.apply(lambda x: stats.ttest_1samp(x, 0.0, nan_policy='omit')[0], axis=1)

    result_df = pd.concat([p_df, t_df], axis=1)
    result_df = result_df.loc[["1-1", "2-1", "3-1", "HL1",
                               "1-2", "2-2", "3-2", "HL2",
                               "1-3", "2-3", "3-3", "HL3"]]
    return result_df


# region 载入数据
factor_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/factor_data.csv"
factor_data = pd.read_csv(factor_path)

GSS_dt = factor_data.loc[:, ['gvkey', 'year', 'GL', 'SC', 'RS', 'LE', 'InvT', 'ccc']]

return_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/return_data.csv"
return_data = pd.read_csv(return_path)

# endregion

# Table 4 & 5
for f_t in ["InvT", "ccc"]:
    rslt_list = []
    for f_name in ["GL", 'SC', "LE", "RS"]:
        rslt = Double_factor(GSS_dt, return_data, 3, "ccc", f_name, "vw").T
        rslt.iloc[0, :] = rslt.iloc[0, :] * 100
        rslt.iloc[0, :] = rslt.iloc[0, :].round(3)

        rslt.iloc[1, :] = rslt.iloc[1, :].round(2)
        rslt.iloc[1, :] = rslt.iloc[1, :].apply(lambda x: "(" + str(x) + ")")
        # rslt["wgt"] = wgt
        rslt["factor"] = f_name
        rslt_list.append(rslt)

    rslt_t = pd.concat(rslt_list, axis=0)
    rslt_t.to_excel(f"/Users/meron/Desktop/01_Work/panjiva/logger/Table_{f_t}.xlsx")
