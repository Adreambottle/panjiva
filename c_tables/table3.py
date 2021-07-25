import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
from scipy import stats

warnings.filterwarnings('ignore')





def Single_factor(factor, ret, groups, f_name, wgt, all_c):

    # factor = GSS
    # f_name = "RS"
    # groups = 5
    # wgt = "vw"
    print("Start")
    wgt = wgt + "r"
    ret = ret.loc[:, [wgt, 'gvkey', 'year', 'month']]
    year_list = factor['year'].unique()

    # group_list = range(1, groups+1)
    group_list = [1, groups]

    f_use = factor[['gvkey', 'year', f_name]]
    f_use = f_use.dropna(how='any')
    f_use['groups'] = f_use.groupby("year")[f_name].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))

    val_y_p = {}
    for y in year_list:
        val_g_p = {}
        for g in group_list:
            print(y, g)

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
                result = sm.OLS(y_data, X_data).fit()
                para = result.params[0]
                val_g_p[g] = para
            else:
                val_g_p[g] = None

        val_y_p[y] = val_g_p

    p_rslt = pd.DataFrame(val_y_p)
    p_rslt = p_rslt.iloc[::-1,:]
    p_rslt.index = list(p_rslt.index)[::-1]
    p_HL = p_rslt.iloc[-1, :] - p_rslt.iloc[0, :]
    p_HL = pd.DataFrame({"H-L":p_HL})
    p_rslt = pd.concat([p_rslt, p_HL.T])

    p_df = p_rslt.mean(axis=1)
    t_df = p_rslt.apply(lambda x: stats.ttest_1samp(x, 0.0, nan_policy='omit')[0], axis=1)
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


rslt_list = []
for f_name in ["GL", "SC", "LE", "RS"]:
    for wgt in ["vw", "ew"]:


        rslt = Single_factor(GSS, return_data, 5, f_name, wgt, True)
        rslt.iloc[0,:] = rslt.iloc[0,:] * 100
        rslt.iloc[0, :] = rslt.iloc[0,:].round(3)

        rslt.iloc[1, :] = rslt.iloc[1, :].round(2)
        rslt.iloc[1, :] = rslt.iloc[1, :].apply(lambda x: "(" + str(x) + ")")
        rslt_list.append(rslt)
        rslt_t = pd.concat(rslt_list, axis=0)

rslt_t.to_excel("/Users/meron/Desktop/01_Work/panjiva/logger/Table_3.xlsx")



