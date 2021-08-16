from linearmodels import FamaMacBeth
import numpy as np
import pandas as pd

import datetime

import statsmodels.api as sm
import statsmodels.formula.api as sml


def getICSeries(factors, ret, method):
    """
    用来得到 ic 序列吗
    """
    icall = pd.DataFrame()

    # 将 return rate 和 factors merge 在一起
    fall = pd.merge(factors, ret,
                    left_on=['tradedate', 'stockcode'],
                    right_on=['tradedate', 'stockcode'])
    # icall 得到所有 return 和 的相关系数
    icall = fall.groupby('tradedate').apply(lambda x: x.corr(method=method)['ret']).reset_index()
    icall = icall.drop(['ret'], axis=1).set_index('tradedate')

    return icall



factors = pd.read_csv("/Users/meron/Desktop/01_Work/panjiva_data/variables_mk.csv", index_col=0)
factors.columns
ret = pd.read_csv("/Users/meron/Desktop/01_Work/panjiva_data/stock_return.csv")
ret.columns

def ifst(x):
    if pd.isnull(x.entry_dt):
        return 0
    elif (x.tradedate < x.entry_dt) | (x.tradedate > x.remove_dt):
        return 0
    else:
        return 1



def getRet(price, freq='d', if_shift=True):
    """
    如何得到 return rate
    """
    price = price.copy()

    if freq == 'w':
        price['weeks'] = price['tradedate'].apply(lambda x: x.isocalendar()[0] * 100 + x.isocalendar()[1])
        ret = price.groupby(['weeks', 'stockcode']).last().reset_index()
        del ret['weeks']

    elif freq == 'm':
        price['ym'] = price.tradedate.apply(lambda x: x.year * 100 + x.month)
        ret = price.groupby(['ym', 'stockcode']).last().reset_index()
        del ret['ym']

    ret = ret[['tradedate', 'stockcode', 'price']]
    if if_shift:
        ret = ret.groupby('stockcode').apply(lambda x: x.set_index('tradedate').price.pct_change(1).shift(-1))
    else:
        ret = ret.groupby('stockcode').apply(lambda x: x.set_index('tradedate').price.pct_change(1))

    ret = ret.reset_index()
    ret = ret.rename(columns={ret.columns[2]: 'ret'})
    return ret

def getdate(x):
    if type(x) == str:
        return pd.Timestamp(x).date()
    else:
        return datetime.date(int(str(x)[:4]), int(str(x)[4:6]), int(str(x)[6:]))




def ols_coef1(x, formula):
    return sml.ols(formula, data=x).fit(missing='drop').params


price = pd.read_csv('price.csv', index_col=0)
pb = pd.read_csv('pb.csv', index_col=0)
roe = pd.read_csv('roe.csv', index_col=0)
mkt = pd.read_csv('mkt.csv', index_col=0)
ST = pd.read_excel('ST.xlsx')

'''
收益率计算
'''

price['tradedate'] = price.tradedate.apply(getdate)
ret_m = getRet(price, freq='m', if_shift=True)
mom1 = getRet(price, freq='m', if_shift=False)
mom1 = mom1.rename(columns={'ret': 'mom1'})

fall = pd.merge(pb, roe, left_on=['tradedate', 'stockcode'], right_on=['tradedate', 'stockcode'])
fall = pd.merge(fall, mkt, left_on=['tradedate', 'stockcode'], right_on=['tradedate', 'stockcode'])
fall['tradedate'] = fall.tradedate.apply(getdate)
fall = pd.merge(fall, mom1, left_on=['tradedate', 'stockcode'], right_on=['tradedate', 'stockcode'])
del fall['rptdate']

fall = pd.merge(fall, ST, left_on='stockcode', right_on='stockcode', how='left')
fall['if_st'] = fall.apply(ifst, axis=1)
fall = fall.loc[fall.if_st == 0].reset_index(drop=True)
fall = fall.drop(['if_st', 'entry_dt', 'remove_dt'], axis=1)

alldata = pd.merge(fall, ret_m, left_on=['tradedate', 'stockcode'], right_on=['tradedate', 'stockcode'])
alldata['mktcap'] = np.log(alldata.mktcap)

ics = getICSeries(fall,ret_m,'spearman')
icir = ics.mean()/ics.std()*np.sqrt(12)
ics.cumsum().plot()


fmdata = alldata.set_index(['stockcode','tradedate'])
fm = FamaMacBeth(dependent = fmdata['ret'],
                 exog = sm.add_constant(fmdata[['pb','mktcap','mom1','roe_ttm']]))
res_fm = fm.fit(debiased=False)
res_fm