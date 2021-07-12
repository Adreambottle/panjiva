import pandas as pd
import numpy as np

class Build_Data():

    def __init__(self):
        self.merge_data()


    def merge_data(self):
        # data_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\savings\variables_mk.csv"
        data_path = r"/Users/meron/Desktop/01_Work/panjiva_data/variables_mk.csv"
        data = pd.read_csv(data_path, index_col=0)
        data["year"] = pd.to_datetime(data["year"], format="%Y-%m-%d")

        # return_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\others\stock_return.csv"
        return_path = r"/Users/meron/Desktop/01_Work/panjiva_data/stock_return.csv"
        rtn_data = pd.read_csv(return_path, usecols=["gvkey", "fyear", "prcc_f", "adjex_f"])
        rtn_data["adj_close"] = rtn_data["prcc_f"] / rtn_data["adjex_f"]
        rtn_data["year"] = pd.to_datetime(rtn_data["fyear"], format="%Y")
        rtn_data["return_rate"] = rtn_data.groupby("gvkey")['adj_close'].pct_change()
        # rtn_data.set_index(["gvkey", "fyear"])

        data = pd.merge(data, rtn_data.loc[:, ["gvkey", "year", "return_rate", "adj_close"]],
                    on=["gvkey", "year"], how="left")
        self.data = data

    def read_saved_data(self, save_path=r"/Users/meron/Desktop/01_Work/panjiva_data/saved_data.csv"):
        self.data = pd.read_csv(save_path)

    def save_data(self, save_path=r"/Users/meron/Desktop/01_Work/panjiva_data/saved_data.csv"):

        self.data.to_csv(save_path)


# 重新构建因子
factor_path = r"/Users/meron/Desktop/01_Work/panjiva_data/variables_mk.csv"
factor = pd.read_csv(factor_path, index_col=0)
factor["year"] = pd.to_datetime(factor["year"], format="%Y-%m-%d")
factor.to_csv(r"/Users/meron/Desktop/01_Work/panjiva_data/factor.csv")

return_path = r"/Users/meron/Desktop/01_Work/panjiva_data/stock_return.csv"
rtn_data = pd.read_csv(return_path, usecols=["gvkey", "fyear", "prcc_f", "adjex_f"])
rtn_data["adj_close"] = rtn_data["prcc_f"] / rtn_data["adjex_f"]
rtn_data["year"] = pd.to_datetime(rtn_data["fyear"], format="%Y")
rtn_data["return_rate"] = rtn_data.groupby("gvkey")['adj_close'].pct_change()
rtn_data.to_csv(r"/Users/meron/Desktop/01_Work/panjiva_data/ret.csv")

