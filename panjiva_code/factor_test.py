import pandas as pd
import numpy as np

data_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\savings\variables_mk.csv"
data = pd.read_csv(data_path, index_col=0)
data["year"] = pd.to_datetime(data["year"], format="%Y-%m-%d")

return_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\others\stock_return.csv"
rtn_data = pd.read_csv(return_path, usecols=["gvkey", "fyear", "prcc_f", "adjex_f"])
rtn_data["adj_close"] = rtn_data["prcc_f"] / rtn_data["adjex_f"]
rtn_data["year"] = pd.to_datetime(rtn_data["fyear"], format="%Y")
rtn_data["return_rate"] = rtn_data.groupby("gvkey")['adj_close'].pct_change()
# rtn_data.set_index(["gvkey", "fyear"])
data = pd.merge(data, rtn_data.loc[:, ["gvkey", "year", "return_rate"]],
                on=["gvkey", "year"], how="left")


class Factor_Test():
    def __init__(self):
        self.data = None

    def set_data(self, data):
        self.data = data

    def read_data(self, data_path):
        self.data = pd.read(data_path)


    def K_class_factor_test(self):
        data = self.data
        R = data.iloc[:,["gvkey", "year", "return_rate"]]
        
