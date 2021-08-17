"""
第一版Group_Test
里面的函数可以直接调用
"""

import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from linearmodels import FamaMacBeth
import datetime
import statsmodels.api as sm
import statsmodels.formula.api as sml
import warnings

warnings.filterwarnings('ignore')

from c_toolkit.scale import mad


def getICSeries(factor, ret, method):
    """
    :param factor: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param method: 'pearson'，'spearman'，'kendal'
    :return: 包含所有 ic 的序列
    """
    ic_all = pd.DataFrame()

    # 将 return rate 和 factors merge 在一起
    f_all = pd.merge(factor, ret,
                     left_on=['year', 'gvkey'],
                     right_on=['year', 'gvkey'])
    # ic_all 得到所有 return 和 的相关系数
    ic_all = f_all.groupby('year').apply(lambda x: x.corr(method=method)['ret']).reset_index()
    ic_all = ic_all.drop(['ret'], axis=1).set_index('year')

    return ic_all


def Group_Test_All_Factors_mean(factor, ret, groups, how="both"):
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

    f_names = factor.columns  # 因子的名字
    f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="inner")

    Group_ret_dict = {}
    Group_ret_EW = []  # 用于储存多个 factor 在不同组别上的 return
    Group_ret_VW = []

    for f in f_names:  # f = f_names[2]

        # f 就是用于循环的各个 factor
        if ((f != 'gvkey') & (f != 'year')):
            # f = "RS"
            # 按照 股票 时间 收益 因子 做为本次测试的子集
            f_use = f_all[['gvkey', 'year', 'return_rate', 'adj_close', f]]
            f_use = f_use.dropna(how='any')

            # f_use['groups'] 是同一时间截面上 按照因子值分的组别
            f_use['groups'] = f_use.groupby("year")[f].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
            # f_use['groups'] = f_use[f].groupby(f_use.year).apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))

            # result 再次按照 时间 和 组别 将股票重新分组
            if (how == "both") or (how == "EW"):
                result_EW = f_use.groupby(['year', 'groups'])['return_rate'].mean()
                # result_EW = f_use.groupby(['year', 'groups']).apply(lambda x: x['return_rate'].mean())

                # 将按照【时间】 gb 后分组的 Series 重新拼接成 DataFrame
                result_EW = result_EW.unstack().reset_index()

                result_EW.insert(0, 'factor', f)

                Group_ret_EW.append(result_EW)

            if (how == "both") or (how == "VW"):
                f_use['wgt'] = f_use.groupby(['year', 'groups'])['adj_close'].transform(lambda x: x / x.sum())
                f_use['result'] = f_use['return_rate'] * f_use["wgt"]
                result_VW = f_use.groupby(['year', 'groups'])['result'].sum()

                result_VW = result_VW.unstack().reset_index()

                result_VW.insert(0, 'factor', f)

                Group_ret_VW.append(result_VW)

    if (how == "both") or (how == "EW"):
        Group_ret_EW = pd.concat(Group_ret_EW, axis=0).reset_index(drop=True)
        cum_EW = Group_ret_EW.iloc[:, 2:].groupby(Group_ret_EW['factor']).apply(np.mean)
        cum_EW = cum_EW.groupby('factor').apply(np.mean)
        # Group_cum_return = Group_ret.iloc[:, 2:].groupby(Group_ret.factor).apply(lambda x: (1 + x).cumprod())

        # 将 cumprod 之后的 return 添加 【time】【code】两个 index
        # cum_EW = pd.concat([Group_ret_EW[['year', 'factor']], cum_EW], axis=1)
        # cum_EW["H-L"] = cum_EW.iloc[:,2] - cum_EW.iloc[:,groups+1]

        Group_ret_dict["EW"] = cum_EW

    if (how == "both") or (how == "VW"):
        Group_ret_VW = pd.concat(Group_ret_VW, axis=0).reset_index(drop=True)
        cum_VW = Group_ret_VW.iloc[:, 2:].groupby(Group_ret_VW['factor']).apply(np.mean)
        cum_VW = cum_VW.groupby('factor').apply(np.mean)

        # cum_VW = pd.concat([Group_ret_VW[['year', 'factor']], cum_VW], axis=1)
        # cum_VW["H-L"] = cum_VW.iloc[:,2] - cum_VW.iloc[:,groups+1]


        Group_ret_dict["VW"] = cum_VW

    return Group_ret_dict


def Group_Test_All_Factors(factor, ret, groups, how="both"):
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

    f_names = factor.columns  # 因子的名字
    f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="inner")

    Group_ret_dict = {}
    Group_ret_EW = []  # 用于储存多个 factor 在不同组别上的 return
    Group_ret_VW = []

    for f in f_names:  # f = f_names[2]

        # f 就是用于循环的各个 factor
        if ((f != 'gvkey') & (f != 'year')):
            # f = "RS"
            # 按照 股票 时间 收益 因子 做为本次测试的子集
            f_use = f_all[['gvkey', 'year', 'return_rate', 'adj_close', f]]
            f_use = f_use.dropna(how='any')

            # f_use['groups'] 是同一时间截面上 按照因子值分的组别
            f_use['groups'] = f_use.groupby("year")[f].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
            # f_use['groups'] = f_use[f].groupby(f_use.year).apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))

            # result 再次按照 时间 和 组别 将股票重新分组
            if (how == "both") or (how == "EW"):
                result_EW = f_use.groupby(['year', 'groups'])['return_rate'].mean()
                # result_EW = f_use.groupby(['year', 'groups']).apply(lambda x: x['return_rate'].mean())

                # 将按照【时间】 gb 后分组的 Series 重新拼接成 DataFrame
                result_EW = result_EW.unstack().reset_index()

                result_EW.insert(0, 'factor', f)

                Group_ret_EW.append(result_EW)

            if (how == "both") or (how == "VW"):
                f_use['wgt'] = f_use.groupby(['year', 'groups'])['adj_close'].transform(lambda x: x / x.sum())
                f_use['result'] = f_use['return_rate'] * f_use["wgt"]
                result_VW = f_use.groupby(['year', 'groups'])['result'].sum()

                result_VW = result_VW.unstack().reset_index()

                result_VW.insert(0, 'factor', f)

                Group_ret_VW.append(result_VW)

    if (how == "both") or (how == "EW"):
        Group_ret_EW = pd.concat(Group_ret_EW, axis=0).reset_index(drop=True)
        cum_EW = Group_ret_EW.iloc[:, 2:].groupby(Group_ret_EW['factor']).apply(lambda x: (1 + x).cumprod())
        # Group_cum_return = Group_ret.iloc[:, 2:].groupby(Group_ret.factor).apply(lambda x: (1 + x).cumprod())

        # 将 cumprod 之后的 return 添加 【time】【code】两个 index
        cum_EW = pd.concat([Group_ret_EW[['year', 'factor']], cum_EW], axis=1)
        cum_EW["H-L"] = cum_EW.iloc[:, 2] - cum_EW.iloc[:, groups + 1]
        cum_EW = cum_EW.round(2)
        Group_ret_dict["EW"] = cum_EW

    if (how == "both") or (how == "VW"):
        Group_ret_VW = pd.concat(Group_ret_VW, axis=0).reset_index(drop=True)
        cum_VW = Group_ret_VW.iloc[:, 2:].groupby(Group_ret_VW['factor']).apply(lambda x: (1 + x).cumprod())

        cum_VW = pd.concat([Group_ret_VW[['year', 'factor']], cum_VW], axis=1)
        cum_VW["H-L"] = cum_VW.iloc[:, 2] - cum_VW.iloc[:, groups + 1]
        cum_VW = cum_VW.round(3)

        Group_ret_dict["VW"] = cum_VW

    return Group_ret_dict





def Group_Test_All_Factors(factor, ret, groups, how="both"):
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

    f_names = factor.columns  # 因子的名字
    f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="inner")

    Group_ret_dict = {}
    Group_ret_EW = []  # 用于储存多个 factor 在不同组别上的 return
    Group_ret_VW = []

    for f in f_names:  # f = f_names[2]

        # f 就是用于循环的各个 factor
        if ((f != 'gvkey') & (f != 'year')):
            # f = "RS"
            # 按照 股票 时间 收益 因子 做为本次测试的子集
            f_use = f_all[['gvkey', 'year', 'return_rate', 'adj_close', f]]
            f_use = f_use.dropna(how='any')

            # f_use['groups'] 是同一时间截面上 按照因子值分的组别
            f_use['groups'] = f_use.groupby("year")[f].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
            # f_use['groups'] = f_use[f].groupby(f_use.year).apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))

            # result 再次按照 时间 和 组别 将股票重新分组
            if (how == "both") or (how == "EW"):
                result_EW = f_use.groupby(['year', 'groups'])['return_rate'].mean()
                # result_EW = f_use.groupby(['year', 'groups']).apply(lambda x: x['return_rate'].mean())

                # 将按照【时间】 gb 后分组的 Series 重新拼接成 DataFrame
                result_EW = result_EW.unstack().reset_index()

                result_EW.insert(0, 'factor', f)

                Group_ret_EW.append(result_EW)

            if (how == "both") or (how == "VW"):
                f_use['wgt'] = f_use.groupby(['year', 'groups'])['adj_close'].transform(lambda x: x / x.sum())
                f_use['result'] = f_use['return_rate'] * f_use["wgt"]
                result_VW = f_use.groupby(['year', 'groups'])['result'].sum()

                result_VW = result_VW.unstack().reset_index()

                result_VW.insert(0, 'factor', f)

                Group_ret_VW.append(result_VW)

    if (how == "both") or (how == "EW"):
        Group_ret_EW = pd.concat(Group_ret_EW, axis=0).reset_index(drop=True)
        cum_EW = Group_ret_EW.iloc[:, 2:].groupby(Group_ret_EW['factor']).apply(lambda x: (1 + x).cumprod())
        # Group_cum_return = Group_ret.iloc[:, 2:].groupby(Group_ret.factor).apply(lambda x: (1 + x).cumprod())

        # 将 cumprod 之后的 return 添加 【time】【code】两个 index
        cum_EW = pd.concat([Group_ret_EW[['year', 'factor']], cum_EW], axis=1)
        cum_EW["H-L"] = cum_EW.iloc[:, 2] - cum_EW.iloc[:, groups + 1]
        cum_EW = cum_EW.round(2)
        Group_ret_dict["EW"] = cum_EW

    if (how == "both") or (how == "VW"):
        Group_ret_VW = pd.concat(Group_ret_VW, axis=0).reset_index(drop=True)
        cum_VW = Group_ret_VW.iloc[:, 2:].groupby(Group_ret_VW['factor']).apply(lambda x: (1 + x).cumprod())

        cum_VW = pd.concat([Group_ret_VW[['year', 'factor']], cum_VW], axis=1)
        cum_VW["H-L"] = cum_VW.iloc[:, 2] - cum_VW.iloc[:, groups + 1]
        cum_VW = cum_VW.round(3)

        Group_ret_dict["VW"] = cum_VW

    return Group_ret_dict





def plotnav(Group_cum_return):
    """
    GroupTest作图
    """
    for f in Group_cum_return["factor"].unique():  # f = Groupnav.factor.unique()[0]
        fnav = Group_cum_return.loc[Group_cum_return["factor"] == f, :].set_index('year').iloc[:, 1:]
        groups = fnav.shape[1]
        lwd = [2] * groups
        ls = ['-'] * groups

        plt.figure(figsize=(10, 5))
        for i in range(groups):
            plt.plot(fnav.iloc[:, i], linewidth=lwd[i], linestyle=ls[i])
        plt.legend(list(range(groups)))
        plt.title('factor group test: ' + f, fontsize=20)
        plt.show()


def build_ccc():
    ccc_path = r"/Users/meron/Desktop/01_Work/panjiva_data/ccc.csv"
    ccc = pd.read_csv(ccc_path)
    ccc["artfs"] = ccc["artfs"].fillna(0)
    ccc['year'] = pd.to_datetime(ccc['fyear'], format="%Y")

    ccc["ccc"] = ccc.invt / ccc.cogs + ccc.artfs / ccc.revt - ccc.ap / ccc.cogs
    ccc["ccc"] = mad(ccc["ccc"], 10)
    return ccc.loc[:, ["gvkey", "year", "ccc"]]


def double_sort(factor, ret, groups, f1, f2):
    """
    # 先按f1分组，再按f2分组 double_sorts
    :param factor: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param groups: 要分成几组
    :param f1: 需要排序的第一个因子的名称
    :param f2: 需要排序的第二个因子的名称
    :return:
    """

    # ret = ret
    # factor = GSS_dt
    # f1 = 'RS'
    # f2 = 'InvT'
    # groups = 3

    f = factor[['year', 'gvkey', f1, f2]].copy()
    f.dropna(how="any", inplace=True)

    f[f1] = f[f1].groupby(f.year).apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
    f[f2] = f[f2].groupby([f.year, f[f1]]).apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
    f = pd.merge(f, ret, left_on=['year', 'gvkey'], right_on=['year', 'gvkey'])

    f['groups'] = f.apply(lambda x: str(int(x[f1])) + '-' + str(int(x[f2])), axis=1)

    res = f.groupby(['year', 'groups']).apply(lambda x: x.return_rate.mean())
    res = res.unstack().reset_index()

    res.iloc[:, 1:].cumsum().plot(figsize=(8, 6))

    ret_mean = res.iloc[:, 1:].mean()
    ret_mean = ret_mean.reset_index()
    ret_mean.columns = ['groups', 'ret']
    ret_mean[f1] = ret_mean.groups.apply(lambda x: x[0])
    ret_mean[f2] = ret_mean.groups.apply(lambda x: x[2])
    ret_mean = ret_mean.pivot(index=f1, columns=f2, values='ret')
    ret_mean["H-L"] = ret_mean.iloc[:, 0] - ret_mean.iloc[:, groups - 1]
    ret_mean.loc["avg", :] = ret_mean.apply(np.mean, axis=0)

    ret_std = res.iloc[:, 1:].std()
    ret_std = ret_std.reset_index()
    ret_std.columns = ['groups', 'ret']
    ret_std[f1] = ret_std.groups.apply(lambda x: x[0])
    ret_std[f2] = ret_std.groups.apply(lambda x: x[2])
    ret_std = ret_std.pivot(index=f1, columns=f2, values='ret')
    ret_std["H-L"] = ret_std.iloc[:, 0] - ret_std.iloc[:, groups - 1]
    ret_std.loc["avg", :] = ret_std.apply(np.mean, axis=0)

    # plt.figure(figsize=(8, 8))
    # sns.heatmap(ret_mean, cmap='YlGnBu', annot=True, square=True)
    # sns.heatmap(ret_std, cmap='YlGnBu', annot=True, square=True)
    # plt.show()

    return (ret_mean, ret_std)


def cls_mktcap():
    mktcap_path = "/Users/meron/Desktop/01_Work/panjiva_data/mktcap.csv"
    mktcap_data = pd.read_csv(mktcap_path)
    mktcap_data['year'] = pd.to_datetime(mktcap_data['fyear'], format="%Y")
    mktcap_data = mktcap_data.loc[:, ["gvkey", "year", "mkvalt"]]
    return mktcap_data


def cls_sic():
    sic_path = "/Users/meron/Desktop/01_Work/panjiva_data/gvkey_sic.csv"
    sic_data = pd.read_csv(sic_path)
    sic_data['year'] = pd.to_datetime(sic_data['fyear'], format="%Y")
    sic_data = sic_data.loc[:, ["gvkey", "year", "sic"]]

    sic_sub_data = {}

    sic_sub_data["Retailers"] = sic_data[(sic_data['sic'] > 5200) & (sic_data['sic'] < 5999)]
    sic_sub_data["Wholesalers"] = sic_data[(sic_data['sic'] > 5000) & (sic_data['sic'] < 5199)]
    sic_sub_data["Manufacturers"] = sic_data[(sic_data['sic'] > 2000) & (sic_data['sic'] < 3999)]

    return sic_sub_data


def ols_coef(x, y):
    x = x.astype('float64')
    y = y.astype('float64')

    return sm.OLS(y, sm.add_constant(x), missing='drop').fit().params


def fama_macbeth(factor, ret=None):
    # fama_macbath
    if ret != None:
        f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="inner")

    else:
        f_all = factor.set_index(['gvkey', 'year'])

        fm = FamaMacBeth(dependent=f_all['return_rate'],
                         exog=sm.add_constant(f_all[[]]))
        res_fm = fm.fit(debiased=False)


def OLS_test(data):
    X = sm.add_constant(data.iloc[:, [2, 3]], has_constant='add')
    y = data.loc[:, "return_rate"]
    model = sm.OLS(y, X).fit()
    return model.params[0]


# def cross_sectional_test(factor, ret, groups):
#     # factor = factor_data.copy()
#     # ret = ret_single.copy()
#     # groups = 4
#
#
#     f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="left")
#     ccc = build_ccc()
#     f_all = pd.merge(f_all, ccc, on=['gvkey', 'year'], how='left')
#     f_all = f_all.dropna(how="any")
#     fu_names = ['Size', 'BM',
#        'GPM', 'Leverage', 'Accruals', 'InvI', 'InvT', 'GMROI', 'CAPEXI',
#        'RDI', 'ccc']
#     ft_names = ['GL', 'RS', 'LE']
#
#     ft_dict = {}
#     for ft in ft_names:
#
#         fu_dict = {}
#         for fu in fu_names:
#             # ft = "GL"
#             # fu = "Size"
#             print(ft, fu)
#             f_use = f_all.loc[:, ["year", "gvkey", ft, fu, "return_rate"]]
#             f_use['groups'] = f_use.groupby("year")[ft].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
#             f_alphas = []
#             for level in range(1, groups+1):
#                 # level = 1
#                 f_sub = f_use[f_use['groups'] == level]
#                 alpha = OLS_test(f_sub)
#                 f_alphas.append(alpha)
#                 fu_dict[fu] = f_alphas
#             fu_df = pd.DataFrame(fu_dict).T
#             # fu_df.columns = [1, 2, 3, 4]
#             fu_df["H-L"] = fu_df.iloc[:,0] - fu_df.iloc[:,3]
#         ft_dict[ft] = fu_df
#     return ft_dict


def cross_sectional_test(factor, ret, groups):

    # factor = factor_data.copy()
    # ret = ret_single.copy()
    # groups = 4

    f_all = pd.merge(factor, ret, on=['gvkey', 'year'], how="left")
    ccc = build_ccc()
    f_all = pd.merge(f_all, ccc, on=['gvkey', 'year'], how='left')
    f_all = f_all.dropna(how="any")
    fu_names = ['Size', 'BM',
                'GPM', 'Leverage', 'Accruals', 'InvI', 'InvT', 'GMROI', 'CAPEXI',
                'RDI', 'ccc']
    ft_names = ['GL', 'RS', 'LE']

    ft_dict = {}
    for ft in ft_names:

        fu_dict = {}
        for fu in fu_names:
            # ft = "GL"
            # fu = "Size"
            print(ft, fu)
            f_use = f_all.loc[:, ["year", "gvkey", ft, fu, "return_rate"]]

            fama_macbeth(f_use)
            f_use['groups'] = f_use.groupby("year")[ft].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
            f_alphas = []
            for level in range(1, groups + 1):
                # level = 1
                f_sub = f_use[f_use['groups'] == level]
                alpha = OLS_test(f_sub)
                f_alphas.append(alpha)
                fu_dict[fu] = f_alphas
            fu_df = pd.DataFrame(fu_dict).T
            # fu_df.columns = [1, 2, 3, 4]
            fu_df["H-L"] = fu_df.iloc[:, 0] - fu_df.iloc[:, groups - 1]
        ft_dict[ft] = fu_df
    return ft_dict


def main():
    """
    factor: 包含了所有的因子信息
    :return:
    """
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

    # group_test 单因子
    Group_cum_return = Group_Test_All_Factors_mean(factor=GSS, ret=ret_complex, groups=5, how='both')

    logging_path = r"./logger/"
    for k, v in Group_cum_return.items():
        v.to_csv(logging_path + f"Group_test_mean_{k}.csv")

    # double sort 测试因子的部分
    GSS_dt = factor_data.loc[:, ['gvkey', 'year', 'GL', 'SC', 'RS', 'LE', 'InvT']]
    ccc = build_ccc()
    GSS_dt = pd.merge(GSS_dt, ccc, on=['gvkey', 'year'], how='left')

    logging_path = r"./logger/double_test.txt"
    for f1 in ["InvT", "ccc"]:
        for f2 in ['GL', 'SC', 'RS', 'LE']:
            # 在这里调用 double_sort 函数
            ds_mean, ds_std = double_sort(factor=GSS_dt, ret=ret_single, groups=3, f1=f1, f2=f2)
            with open(logging_path, 'a+') as logging:
                print(f"\n\n\nFactor 1 is {f1}, Factor 2 is {f2}", file=logging)
                print("\nmean\n", ds_mean, file=logging)
                print("\nstandard error\n", ds_std, file=logging)

    # 进行 SIC 分类的时候
    sic_data = cls_sic()
    for industry, data in sic_data.items():
        # industry = 'Retailers'
        # data = sic_data[industry]
        GSS_data = pd.merge(GSS, data, on=['gvkey', 'year'], how='inner').copy()
        cum_return = Group_Test_All_Factors(factor=GSS_data, ret=ret_complex, groups=5, how='both')
        logging_path = r"./logger/"
        for k, v in cum_return.items():
            v.to_csv(logging_path + f"SIC_test_on_{industry}_{k}.csv")

    # 进行 mktcap 分类的时候
    mktcap_data = cls_mktcap()
    GSS_data = pd.merge(GSS, mktcap_data, on=['gvkey', 'year'], how='left').copy()
    GSS_data = GSS_data.dropna(subset=["mkvalt"])
    GSS_data["mkvalt"] = GSS_data["mkvalt"].groupby(GSS_data.year).apply(lambda x: np.ceil(x.rank() / (len(x) / 2)))
    GSS_data_s = GSS_data[GSS_data["mkvalt"] == 1]
    cum_return_s = Group_Test_All_Factors(factor=GSS_data_s, ret=ret_complex, groups=3, how='both')
    logging_path = r"./logger/"
    for k, v in cum_return_s.items():
        v.to_csv(logging_path + f"Diff_MktCap_Small_{k}.csv")

    GSS_data_l = GSS_data[GSS_data["mkvalt"] == 2]
    cum_return_l = Group_Test_All_Factors(factor=GSS_data_l, ret=ret_complex, groups=3, how='both')
    for k, v in cum_return_l.items():
        v.to_csv(logging_path + f"Diff_MktCap_Large_{k}.csv")

    # cross_sectional test
    logging_path = r"./logger/"
    cs_dict = cross_sectional_test(factor=factor_data, ret=ret_single, groups=4)
    for k, v in cs_dict.items():
        v.to_csv(logging_path + f"cross_sectional_{k}.csv")

    paths = ["/Users/meron/Desktop/01_Work/panjiva/logger/Diff_MktCap_Small_EW.csv",
            "/Users/meron/Desktop/01_Work/panjiva/logger/Diff_MktCap_Small_VW.csv",
            "/Users/meron/Desktop/01_Work/panjiva/logger/Diff_MktCap_Large_EW.csv",
            "/Users/meron/Desktop/01_Work/panjiva/logger/Diff_MktCap_Large_VW.csv"]

    i = 0
    for SL in ["Small", "Large"]:
        for EV in ["EW", "VW"]:
            path = f"/Users/meron/Desktop/01_Work/panjiva/logger/Diff_MktCap_{SL}_{EV}.csv"
            data = pd.read_csv(path, index_col=0)
            result = data.groupby('factor').apply(np.mean)
            result["Small/Lage"] = SL
            result["EW/VW"] = EV
            if i == 0:
                result_total = result
            else:
                result_total = pd.concat([result_total, result])
            i += 1

    result_total = result_total.reset_index().sort_values(['factor', 'EW/VW', 'Small/Lage']).set_index(['factor', 'EW/VW', 'Small/Lage'])
    result_total.to_csv("/Users/meron/Desktop/01_Work/panjiva/logger/Diff_MktCap.csv")


    data.to_csv("/Users/meron/Desktop/01_Work/panjiva/logger/Table_3.csv")

    GSS = GSS.dropna()
    GSS_u = GSS.loc[:, ["GL", "SC", "LE", "RS"]]
    GSS_u["GL"] = GSS_u["GL"]/10
    GSS_u["RS"] = GSS_u["RS"]*2

    result = GSS_u.describe()
    result.T.to_csv("/Users/meron/Desktop/01_Work/panjiva/logger/Table_1A.csv")
    GSS_u.corr('spearman')

    corr = factor_data.corr('spearman')
    corr.to_csv("/Users/meron/Desktop/01_Work/panjiva/logger/Table_1B.csv")

    factor_data.columns
    f_u = factor_data.loc[:, ['Size', 'BM',
       'GPM', 'Leverage', 'Accruals', 'InvI', 'InvT', 'GMROI', 'CAPEXI',
       'RDI']]

    result = f_u.describe()
    result.to_csv("/Users/meron/Desktop/01_Work/panjiva/logger/Table_1.csv")
