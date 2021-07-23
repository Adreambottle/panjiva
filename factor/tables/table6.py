import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

from toolkit.scale import mad





def cls_sic():
    sic_path = "/Users/meron/Desktop/01_Work/panjiva_data/return_data/gvkey_sic.csv"
    sic_data = pd.read_csv(sic_path)
    sic_data['year'] = pd.to_datetime(sic_data['fyear'], format="%Y").apply(lambda x: x.year)
    sic_data = sic_data.loc[:, ["gvkey", "year", "sic"]]

    sic_sub_data = {}

    sic_sub_data["Retailers"] = sic_data[(sic_data['sic'] > 5200) & (sic_data['sic'] < 5999)]
    sic_sub_data["Wholesalers"] = sic_data[(sic_data['sic'] > 5000) & (sic_data['sic'] < 5199)]
    sic_sub_data["Manufacturers"] = sic_data[(sic_data['sic'] > 2000) & (sic_data['sic'] < 3999)]

    return sic_sub_data


def Single_factor(factor, ret, groups, f_name="RS", wgt="vw"):
    """
     一次性测试多个因子
    :param factor: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param groups: 分成多少组来测
    :return: cumulative product return for stocks with different groups
    """
    # factor = GSS
    # f_name = "RS"
    # groups = 5
    # wgt = "vw"

    wgt = wgt + "r"
    ret = return_data.loc[:, [wgt, 'gvkey', 'year', 'month']]

    # f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="inner")
    # f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="right")

    year_list = factor['year'].unique()
    group_list = [1, 5]

    f_use = factor[['gvkey', 'year', f_name]]
    f_use = f_use.dropna(how='any')

    f_use['groups'] = f_use.groupby("year")[f_name].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))

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
            f_u_ttl["month"] = np.tile(range(1, 13), len(f_u_sub))
            f_u_ttl = pd.merge(f_u_ttl, ret, on=['year', 'month', 'gvkey'], how='left')
            f_u_ttl = f_u_ttl.dropna(how="any")
            # f_u_ttl.head()

            if not f_u_sub.empty:
                X_data = sm.add_constant(f_u_ttl[f_name], has_constant='add')
                y_data = f_u_ttl[wgt]
                try:
                    result = sm.OLS(y_data, X_data).fit()
                    para = result.params[0]
                except:
                    para = 0
                val_g_p[g] = para
            else:
                val_g_p[g] = None

        val_y_p[y] = val_g_p

    p_rslt = pd.DataFrame(val_y_p)
    p_rslt = p_rslt.iloc[::-1,:]
    p_rslt.index = list(p_rslt.index)[::-1]
    try:
        p_HL = p_rslt.iloc[-1, :] - p_rslt.iloc[0, :]
    except:
        p_HL = pd.Series([np.nan]*p_rslt.shape[1])
    p_HL = pd.DataFrame({"H-L":p_HL})
    p_rslt = pd.concat([p_rslt, p_HL.T])

    p_df = p_rslt.mean(axis=1)

    t_df = p_rslt.apply(lambda x: stats.ttest_1samp(x, 0.0, nan_policy='omit')[0], axis=1)

    # t_df = pd.DataFrame(val_y_t).mean(axis=1)

    result_df = pd.concat([p_df, t_df], axis=1).T

    print(result_df)
    return result_df




# region 载入数据
factor_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/factor_data.csv"
factor_data = pd.read_csv(factor_path)

GSS = factor_data.loc[:, ['gvkey', 'year', 'GL', 'SC', 'RS', 'LE']]

return_path = "/Users/meron/Desktop/01_Work/panjiva_data/v2/return_data.csv"
return_data = pd.read_csv(return_path)
# endregion



sic_data = cls_sic()

# 进行 SIC 分类的时候

for industry, data in sic_data.items():
    # ['Retailers', 'Wholesalers', 'Manufacturers']
    data = sic_data[industry]
    GSS_data = pd.merge(GSS, data, on=['gvkey', 'year'], how='inner').copy()
    GSS_data = GSS_data.dropna(how="any")

    rslt_list = []
    for f_name in ["GL", "SC", "LE", "RS"]:
        for wgt in ["vw", "ew"]:
            rslt = Single_factor(GSS_data, return_data, 5, f_name, wgt)
            rslt.iloc[0, :] = rslt.iloc[0, :] * 100
            rslt.iloc[0, :] = rslt.iloc[0, :].round(3)

            rslt.iloc[1, :] = rslt.iloc[1, :].round(2)
            rslt.iloc[1, :] = rslt.iloc[1, :].apply(lambda x: "(" + str(x) + ")")
            rslt_list.append(rslt)
            rslt_t = pd.concat(rslt_list, axis=0)

    rslt_t.to_excel(f"/Users/meron/Desktop/01_Work/panjiva/logger/Table_6_{industry}.xlsx")
