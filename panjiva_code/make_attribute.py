import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="whitegrid")
import warnings
warnings.filterwarnings("ignore")
from scipy.stats.mstats import winsorize
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)

data_path = r"/Users/meron/Desktop/01_Work/panjiva_data/compustat.csv"
# data = pd.read_csv(data_path, index_col=["gvkey", "datadate"])

from sklearn.preprocessing import MinMaxScaler

def plot(ser):
    # plt.hist(ser)

    ser = np.array(ser)
    sns.boxplot(ser)
    # sns.barplot(ser)
    plt.show()




class Get_Attribute():

    def __init__(self):
        self.data_path = r"/Users/meron/Desktop/01_Work/panjiva_data/compustat.csv"


    def read_data(self):
        self.data = pd.read_csv(data_path, index_col=["gvkey", "datadate"])
        # sample = data.sample(1000)

    def get_attribute(self):
        data = self.data

        Size = data["prcc_f"] * data["csho"]

        # Book to Market ratio

        # BM = data["ceq"] + data["txdc"] - data["pstk"] / Size

        BM_new = (data["at"] - data["lt"]) / Size
        GPM = (data["sale"] - data["cogs"]) / data["sale"]
        Leverage = data["lt"] / (data["at"] - data["lt"])
        Accruals = (data["act"].diff() - data["che"].diff()
                    - data["lct"].diff() - data["dlc"].diff()
                    - data["txp"].diff() - data["dp"]) / data["at"]
        InvI = data["invt"] / data["at"]
        InvT = (data["cogs"] - data["lifr"].diff()) / (data["invt"] + data["lifr"])
        GMROI = (data["sale"] - data["cogs"] + data["lifr"].diff()) / (data["invt"] + data["lifr"])
        CAPEXI = data["capx"] / data["at"]
        RDI = data["xrd"] / data["at"]

        attribute = pd.DataFrame({"Size": Size,
                                  "BM": BM_new,
                                  "GPM": GPM,
                                  "Leverage": Leverage,
                                  "Accruals": Accruals,
                                  "InvI": InvI,
                                  "InvT": InvT,
                                  "GMROI": GMROI,
                                  "CAPEXI": CAPEXI,
                                  "RDI": RDI})
        self.attribute = attribute


def three_sigma(series, n:int):
    mean = series.mean()
    std = series.std()
    max_range = mean + n * std
    min_range = mean - n * std
    return np.clip(series, min_range, max_range)

def percentile(series, min= 0.025, max= 0.975):
    series = series.sort_values()
    q = series.quantile([min, max])
    return np.clip(series, q.iloc[0], q.iloc[-1])

def mad(series, n=3):
    median = series.quantile(0.5)
    diff_median = ((series - median).abs()).quantile(0.5)
    max_range = median + n * diff_median
    min_range = median - n * diff_median
    return np.clip(series, min_range, max_range)


gt = Get_Attribute()
gt.read_data()
gt.get_attribute()
attr = gt.attribute
attr = attr.replace([np.inf, -np.inf], np.nan)
attr = attr.dropna(how='any', axis=0).apply(mad, axis=0, args=(20,))
attr_desc = attr.describe()

attr = attr.apply(three_sigma, axis=0, args=(3, ))
attr_scale = attr.apply(percentile, axis=0, args=(0.1, 0.9))
attr = winsorize(attr, limits=[0.1, 0.2])

