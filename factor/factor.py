import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import datetime
from toolkit.scale import mad
import statsmodels.api as sm
import statsmodels.formula.api as sml
from linearmodels import FamaMacBeth

import warnings
warnings.filterwarnings('ignore')


def select_time(data, factor, ncut=5, year_list=range(2009, 2020)):
    # ncut = 5
    # year_list = range(2009, 2021)
    # data = bd.data
    # factor = "RS"
    year_list = [datetime.datetime.strptime(str(year), "%Y") for year in year_list]

    data = data.loc[:,["gvkey", "year", "return_rate", "adj_close", factor]]
    data = data.dropna(subset=[factor, "return_rate"])
    mean_return_years = []
    for i, year in enumerate(year_list):
        # i, year = 3, year_list[i]
        data_by_year = data[data["year"] == year]
        ser = data_by_year[factor]
        q = 1 / ncut
        l_q = []
        l_q.append(ser.min() - 1)
        for j in range(ncut):
            qan = ser.quantile(q * (j + 1))
            l_q.append(qan)

        data_by_fct_list = []
        for j in range(ncut):
            r = data_by_year[(ser > l_q[j]) & (ser <= l_q[j + 1])]
            data_by_fct_list.append(r)

        mean_return_one_year = []
        for j in range(ncut):
            # j 表示的按照因子的排序
            stocks_level_j = data_by_fct_list[j]
            # print(stocks_level_j)
            mean_return = mad(stocks_level_j["return_rate"].dropna(), 20).mean()

            mean_return_one_year.append(mean_return)
        mean_return_years.append(mean_return_one_year)
    # print(mean_return_years)

    origin_time = datetime.datetime.strptime(str(year_list[0].year-1), "%Y")
    origin_return = pd.DataFrame([1]*ncut).T
    origin_return.index = [origin_time]

    mean_return_df = pd.DataFrame(mean_return_years, index=year_list) + 1
    return_cumprod = mean_return_df.cumprod(axis=0)
    return_cumprod = pd.concat([origin_return, return_cumprod])
    return_cumprod.plot()
    plt.show()


select_time(data, "LE", 5, range(2009, 2020))

data_path = "/Users/meron/Desktop/01_Work/panjiva_data/saved_data.csv"
data = pd.read_csv(data_path, index_col=0)
data = data.loc[:, ['gvkey', 'year', 'return_rate', 'GL', 'SC', 'RS', 'LE']]


def getICSeries(data, method="spearman"):
    """
    用来得到所有factor 对应的 ic 序列
    """
    icall = pd.DataFrame()
    # icall 得到所有 return 和 所有 factor 的相关系数
    # 在 apply 之后只去 return_rate 这一列的值作为相关系数
    icall = data.groupby('year').apply(lambda x: x.corr(method=method)['return_rate']).reset_index()
    icall = icall.drop(['return_rate', 'gvkey'], axis=1).set_index('year')

    return icall


def ols_coef(x, y):
    x = x.astype('float64')
    y = y.astype('float64')

    return sm.OLS(y, sm.add_constant(x), missing='drop').fit().params

data['year'] = pd.to_datetime(data['year'], format='%Y-%m-%d')
fmdata = data.set_index(['gvkey','year'])
fm = FamaMacBeth(dependent = fmdata['return_rate'],
                 exog = sm.add_constant(fmdata[['GL','SC','RS','LE']]))
res_fm = fm.fit(debiased=False)
res_fm




def cut_data(data, ncut=5):
    '''
    根据分位数将数据分组
    input:
    data:pd.Series，index为股票代码，values为因子值
    ncut:分组的数量
    output:
    res:list,元素为分组值,series类型，从小到大排列
    '''
    ser = data["return_rate"]
    q = 1/ncut
    l_q = []
    l_q.append(ser.min()-1)
    for i in range(ncut):
        qan = ser.quantile(q*(i+1))
        l_q.append(qan)
    res = []
    for n in range(ncut):
        r = data[(ser>l_q[n])&(ser<=l_q[n+1])]
        res.append(r)
    return res





def cut_factor_plot(data, profit, ncut=5):
    '''
    分层因子收益率可视化
    input:
    data:pd.series,因子数据
    profit:dataframe，index为股票代码，columns为日期，values为收益率
    '''
    cut_res = cut_data(data, ncut=ncut)

    for i in range(len(cut_res)):
        stocks = cut_res[i].index
        profit_cut = profit.loc[stocks]
        profit_cut = profit_cut.mean()
        l.append(profit_cut)
    df = pd.concat(l, axis=1)
    df = df.cumsum()
    df.plot(figsize=(20, 10))
    plt.legend()


def calculate_IC_IR_without_data_process(stocks, factors, start_date, end_date):
    '''
    计算因子的IC/IR值
    input:
    stocks:list,股票代码
    factors:list，计算的因子
    start_date:开始时间
    end_date:结束时间
    output:
    df_ic:dataframe,index为时间，columns为因子
    df_ir:dataframe,index为时间，columns为因子，CALCULATE_IR_PERIOD个向前计算数值，

    '''

    profit = get_day_profit_forward(stocks=stocks, start_date=start_date, end_date=end_date, pre_num=ADJUST_DAYS)
    date_list = profit.index
    l_ic = []
    for date in date_list:
        fund_data = get_fundamental_data(securities=stocks, factor_list=factors, ttm_factors=ttm_factors, date=date)
        l = []
        for factor in factors:
            ic, pvalue = st.spearmanr(fund_data[factor], profit.loc[date])
            l.append(ic)
        # df_day_ic = pd.DataFrame(l,index=factors)
        l_ic.append(l)
    df_ic = pd.DataFrame(l_ic, index=date_list, columns=factors)

    l_ir_all = []
    date_ir = list(df_ic.index)
    for fac in factors:
        if CALCULATE_IR_PERIOD <= len(date_ir):
            l_ir = []
            for date in date_ir[CALCULATE_IR_PERIOD:]:
                ind = date_ir.index(date)
                ic_cal = df_ic.loc[date_ir[ind - CALCULATE_IR_PERIOD]:date, fac]
                ir = ic_cal.mean() / ic_cal.std()
                l_ir.append(ir)
            l_ir_all.append(l_ir)
        else:
            print('CALCULATE_IR_PERIOD length is too large')
    df_ir = pd.DataFrame(l_ir_all, index=factors, columns=date_ir[CALCULATE_IR_PERIOD:])
    df_ir = df_ir.stack().unstack(0)
    return df_ic, df_ir

# ic,ir = calculate_IC_IR_without_data_process(all_stocks,factors=factor_list[:5],start_date=start_date,end_date=end_date)


# 获取各个因子对应的最大夏普比率是第几分组，基于此进行选股
factor_index = {}
for fac in res_df.columns:
    l = list(res_df[fac].values)
    index = l.index(max(l))
    factor_index[fac] = index

test_start_date = '2015-01-01'
test_end_date = '2016-01-01'
trade_days_all = (get_trade_days(start_date=test_start_date, end_date=test_end_date)).tolist()
trade_days = trade_days_all[:-20]
profit_list = []
for date in trade_days[::20]:
    index = trade_days.index(date)
    all_stocks = list(get_all_securities(date=date).index)
    fund_data = get_fundamental_data(factor_list=factor_list, ttm_factors=ttm_factors, date=date, securities=all_stocks)
    fillna_d = fillna_with_industry(fund_data, date=date)
    stocks_set = set(all_stocks)
    for factor in factor_list:
        cut_res = cut_data(fillna_d[factor])
        stocks_sel_series = cut_res[factor_index[factor]]  # 根据之前计算的因子分组选股
        stocks_set &= set(list(stocks_sel_series.index))  # 计算各个分组股票的交集
    profit_stocks = list(stocks_set)
    # 持仓一个月，计算一个月后的收益
    profit = get_day_profit_forward(stocks=profit_stocks, start_date=date, end_date=trade_days_all[index + 20],
                                    pre_num=20)
    profit_mean = profit.mean(axis=1)  # 每月收益的均值
    profit_list.append(profit_mean)
profit_df = pd.concat(profit_list)
profit_df = profit_df + 1
print(profit_df)

profit_res = profit_df.cumprod()  # 计算时间轴上的总收益
print(profit_res)
'''
因子选择时采用13年数据，测试时
使用14年数据，收益率为63%
使用15年数据，收益率为174%
使用16年数据，收益率为25%
使用14-18年数据，收益率为368%

'''


def Group_Test_All_Factors(factors, ret, groups):
    """
     一次性测试多个因子
    :param factors: 储存所有 factor 的 DataFrame, index = [code, time]
    :param ret: 储存股票收益率的 DataFrame, index = [code, time]
    :param groups: 分成多少组来测
    :return: cumulative product return for stocks with different groups
    """
    # factors = f1_norm[['tradedate','stockcode','pb']].copy()
    # ret = ret=.copy()
    # groups = 10

    fnames = data.columns  # 因子的名字
    f_all = pd.merge(factors, ret,  # 包括了 factor 和 return 的 total data
                    left_on=['gvkey', 'year'],
                    right_on=['gvkey', 'year'])

    Group_ret = []  # 用于储存多个 factor 在不同组别上的 return

    for f in fnames:  # f = fnames[2]

        # f 就是用于循环的各个 factor
        if ((f != 'gvkey') & (f != 'year')):

            # f = "RS"
            # 按照 股票 时间 收益 因子 做为本次测试的子集
            f_use = f_all[['gvkey', 'year', 'return_rate', f]]

            # f_use['groups'] 是同一时间截面上 按照因子值分的组别
            f_use['groups'] = f_use.groupby("year")[f].apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
            # f_use['groups'] = f_use[f].groupby(f_use.year).apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))

            # 再次按照 时间 和 组别 将股票重新分组
            result = f_use.groupby(['year', 'groups'])['return_rate'].mean()
            # result = f_use.groupby(['year', 'groups']).apply(lambda x: x['return_rate'].mean())

            # 将按照【时间】 gb 后分组的 Series 重新拼接成 DataFrame
            result = result.unstack().reset_index()
            result.insert(0, 'factor', f)
            Group_ret.append(result)

    Group_ret = pd.concat(Group_ret, axis=0).reset_index(drop=True)

    Group_cum_return = Group_ret.iloc[:, 2:].groupby(Group_ret.factor).apply(lambda x: (1 + x).cumprod())
    Group_cum_return = pd.concat([Group_cum_return[['year', 'factor']], Group_cum_return], axis=1)

    return Group_cum_return


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
