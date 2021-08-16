import os
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns


from linearmodels import FamaMacBeth
import datetime
import statsmodels.api as sm
import statsmodels.formula.api as sml


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


def getICSeries(factors, ret, method):
    # method = 'spearman';factors = fall.copy();

    icall = pd.DataFrame()
    fall = pd.merge(factors, ret, left_on=['tradedate', 'stockcode'], right_on=['tradedate', 'stockcode'])
    icall = fall.groupby('tradedate').apply(lambda x: x.corr(method=method)['ret']).reset_index()
    icall = icall.drop(['ret'], axis=1).set_index('tradedate')

    return icall


def ifst(x):
    if pd.isnull(x.entry_dt):
        return 0
    elif (x.tradedate < x.entry_dt) | (x.tradedate > x.remove_dt):
        return 0
    else:
        return 1


def GroupTestAllFactors(factors, ret, groups):
    # factors = f1_norm[['tradedate','stockcode','pb']].copy()
    # ret = ret=.copy()
    # groups = 10
    """
    一次性测试多个因子
    """
    fnames = factors.columns            # 因子的名字
    fall = pd.merge(factors, ret,       # 包括了 factor 和 return 的 total data
                    left_on=['stockcode', 'tradedate'],
                    right_on=['stockcode', 'tradedate'])
    Groupret = []

    for f in fnames:                # f = fnames[2]

        # f 就是用于循环的各个 factor
        if ((f != 'stockcode') & (f != 'tradedate')):

            fuse = fall[['stockcode', 'tradedate', 'ret', f]]
            # fuse['groups'] = pd.qcut(fuse[f],q = groups,labels = False)
            fuse['groups'] = fuse[f].groupby(fuse.tradedate).apply(lambda x: np.ceil(x.rank() / (len(x) / groups)))
            result = fuse.groupby(['tradedate', 'groups']).apply(lambda x: x.ret.mean())
            result = result.unstack().reset_index()
            result.insert(0, 'factor', f)
            Groupret.append(result)

    Groupret = pd.concat(Groupret, axis=0).reset_index(drop=True)

    Groupnav = Groupret.iloc[:, 2:].groupby(Groupret.factor).apply(lambda x: (1 + x).cumprod())
    Groupnav = pd.concat([Groupret[['tradedate', 'factor']], Groupnav], axis=1)

    return Groupnav


def plotnav(Groupnav):
    """
    GroupTest作图
    """
    for f in Groupnav.factor.unique():  # f = Groupnav.factor.unique()[0]
        fnav = Groupnav.loc[Groupnav.factor == f, :].set_index('tradedate').iloc[:, 1:]
        groups = fnav.shape[1]
        lwd = [2] * groups
        ls = ['-'] * groups

        plt.figure(figsize=(10, 5))
        for i in range(groups):
            plt.plot(fnav.iloc[:, i], linewidth=lwd[i], linestyle=ls[i])
        plt.legend(list(range(groups)))
        plt.title('factor group test: ' + f, fontsize=20)



mktcap = pd.read_excel('mktcap.xlsx', encoding='gbk')
pb = pd.read_excel('PB_monthly.xlsx', encoding='gbk')
price = pd.read_excel('price.xlsx', encoding='gbk')
ST = pd.read_excel('ST.xlsx', encoding='gbk')

startdate = datetime.date(2010, 12, 31)
enddate = datetime.date(2018, 12, 31)

pb = pb.fillna(0)
price = price.loc[(price.tradedate >= startdate) & (price.tradedate <= enddate)].reset_index(drop=True)
pb = pb.loc[(pb.tradedate >= startdate) & (pb.tradedate <= enddate)].reset_index(drop=True)
mktcap = mktcap.loc[(mktcap.tradedate >= startdate) & (mktcap.tradedate <= enddate)].reset_index(drop=True)

ret_m = getRet(price, freq='m', if_shift=True)

fall = pd.merge(mktcap, pb, left_on=['tradedate', 'stockcode'], right_on=['tradedate', 'stockcode'])

# 剔ST
fall = pd.merge(fall, ST, left_on='stockcode', right_on='stockcode', how='left')
fall['if_st'] = fall.apply(ifst, axis=1)
fall = fall.loc[fall.if_st == 0].reset_index(drop=True)
fall = fall.drop(['if_st', 'entry_dt', 'remove_dt'], axis=1)

# 计算IC
ics = getICSeries(fall, ret_m, 'spearman')
ics.cumsum().plot(title='cum IC', figsize=(8, 4))
ics.mean()
ics.mean() / ics.std() * np.sqrt(12)

# 分层测试
groups = 5
Groupnav = GroupTestAllFactors(fall,ret_m,groups)
plotnav(Groupnav)


# 独立排序

f1 = 'mktcap'
f2 = 'pb'


f = fall[['tradedate','stockcode',f1,f2]].copy()

f[f1] = f[f.columns[2]].groupby(f.tradedate).apply(lambda x:np.ceil(x.rank()/(len(x)/groups)))
f[f2] = f[f.columns[3]].groupby(f.tradedate).apply(lambda x:np.ceil(x.rank()/(len(x)/groups)))


res = f.groupby([f1,f2]).count()
res = res.iloc[:,1].reset_index()
res = res.pivot(index = f1,columns = f2,values = 'stockcode')
res = res/f.shape[0]




# 基本独立，均匀分布
plt.figure(figsize = (8,8))
sns.heatmap(res,cmap = 'YlGnBu', annot=True,square = True)
plt.show()


f = pd.merge(f,ret_m,left_on = ['tradedate','stockcode'],right_on = ['tradedate','stockcode'])

f['groups'] = f.apply(lambda x:str(int(x[f1])) + '-' + str(int(x[f2])),axis = 1)

res = f.groupby(['tradedate','groups']).apply(lambda x:x.ret.mean())
res = res.unstack().reset_index()

res.set_index('tradedate').cumsum().plot(figsize = (8,6))


yret = res.iloc[:,1:].mean()
yret = yret.reset_index()
yret.columns = ['groups','ret']
yret[f1] = yret.groups.apply(lambda x:x[0])
yret[f2] = yret.groups.apply(lambda x:x[2])


plt.figure(figsize = (8,8))
sns.heatmap(yret.pivot(index = f1,columns = f2,values = 'ret'),cmap = 'YlGnBu',annot = True,square = True)
plt.show()





# 先按f1分组，再按f2分组 doublesorts


f1 = 'mktcap'
f2 = 'pb'


f = fall[['tradedate','stockcode',f1,f2]].copy()

f[f1] = f[f.columns[2]].groupby(f.tradedate).apply(lambda x:np.ceil(x.rank()/(len(x)/groups)))
f[f2] = f[f.columns[3]].groupby([f.tradedate,f[f1]]).apply(lambda x:np.ceil(x.rank()/(len(x)/groups)))
f = pd.merge(f,ret_m,left_on = ['tradedate','stockcode'],right_on = ['tradedate','stockcode'])

f['groups'] = f.apply(lambda x:str(int(x[f1])) + '-' + str(int(x[f2])),axis = 1)

res = f.groupby(['tradedate','groups']).apply(lambda x:x.ret.mean())
res = res.unstack().reset_index()

res.iloc[:,1:].cumsum().plot(figsize = (8,6))


yret = res.iloc[:,1:].mean()
yret = yret.reset_index()
yret.columns = ['groups','ret']
yret[f1] = yret.groups.apply(lambda x:x[0])
yret[f2] = yret.groups.apply(lambda x:x[2])

plt.figure(figsize = (8,8))
sns.heatmap(yret.pivot(index = f1,columns = f2,values = 'ret'),cmap = 'YlGnBu',annot = True,square = True)
plt.show()
f1 = 'pb'
f2 = 'mktcap'

f = fall[['tradedate','stockcode',f1,f2]].copy()

f[f1] = f[f.columns[2]].groupby(f.tradedate).apply(lambda x:np.ceil(x.rank()/(len(x)/groups)))
f[f2] = f[f.columns[3]].groupby([f.tradedate,f[f1]]).apply(lambda x:np.ceil(x.rank()/(len(x)/groups)))
f = pd.merge(f,ret_m,left_on = ['tradedate','stockcode'],right_on = ['tradedate','stockcode'])

f['groups'] = f.apply(lambda x:str(int(x[f1])) + '-' + str(int(x[f2])),axis = 1)

res = f.groupby(['tradedate','groups']).apply(lambda x:x.ret.mean())
res = res.unstack().reset_index()

res.iloc[:,1:].cumsum().plot(figsize = (8,6))


yret = res.iloc[:,1:].mean()
yret = yret.reset_index()
yret.columns = ['groups','ret']
yret[f1] = yret.groups.apply(lambda x:x[0])
yret[f2] = yret.groups.apply(lambda x:x[2])

plt.figure(figsize = (8,8))
sns.heatmap(yret.pivot(index = f1,columns = f2,values = 'ret'),cmap = 'YlGnBu',annot = True,square = True)
plt.show()


