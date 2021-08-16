"""
用于从数据中制造 panjiva data 的相关变量
"""


import pandas as pd
import warnings
import re
import numpy as np
import datetime
from c_toolkit.scale import mad
warnings.filterwarnings('ignore')


class FA():
    """
    用于制造 panjiva data 的相关变量
    """

    def __init__(self):

        self.sample = False
        self.set_attribute()
        self.read_data()
        self.calculate()

    def set_attribute(self):
        self.year_list = []
        self.data_list = []
        self.column_name = ['index', 'panjivarecordid', 'arrivaldate', 'conciqcompanyid',
                            'gv_conprt', 'shpmtorigin', 'shpciqcompanyid', 'shpultcompanyid',
                            'quantity_num', 'unit', 'weightkg', 'valueofgoodsusd', 'hscode',
                            'gv_con', 'gv_conprt', 'gv_shp', 'gv_shpprt']
        self.drop_na_col = ["gv_conprt",
                            "shpciqcompanyid",
                            "hscode",
                            "valueofgoodsusd",
                            "gv_conprt"]
        self.GSS = {}
        self.save_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\savings"

    def calculate(self):
        """
        执行计算语句
        """
        GSS = self.GSS
        self.get_GL()
        self.get_SC()
        self.get_RS()
        self.get_LE()

        fdmk_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\others\fundamental_mk.csv"
        fdmk = pd.read_csv(fdmk_path)
        fdmk["year"] = pd.to_datetime(fdmk["year"], format="%Y")


        output = pd.merge(GSS["GL"], GSS["SC"], on=["year", "gvkey"], how="left")
        output = pd.merge(output, GSS["RS"], on=["year", "gvkey"], how="left")
        output = pd.merge(output, GSS["LE"], on=["year", "gvkey"], how="left")
        output = output.apply(mad, axis=0, args=(20, ))
        output = pd.merge(output, fdmk, on=["year", "gvkey"], how="left")

        # GSS = pd.DataFrame(self.GSS)
        self.output = output
        output.to_csv(self.save_path + r"\variables_mk.csv")
        return output

    def form_hscode(self, hscode):
        """
        因为 hscode 有很多种编码模式
        将 hscode 改成六位数
        """
        hscode = re.split(':', str(hscode))[-1][:6]
        return hscode

    def form_data(self, data):
        """
        重新整理数据
        将 hscode 改成六位数编码的
        将 shpmtorigin 货物发出地改成全部是小写的
        """
        data = data.dropna(subset=self.drop_na_col)
        data["hscode"] = data["hscode"].apply(self.form_hscode)
        data['shpmtorigin'] = data['shpmtorigin'].str.lower()
        return data

    def read_data(self):

        """
        读取数据，分成两种读取方式，因为数据量过大，调试的时候会选用 Sample Data
        如果 self.sample 是 True，代表选用测试数据
        如果 self.sample 是 False，代表选用真实的数据
        :return: 将生成的数据添加到 self.data_list 中
        """
        gv_pj_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\others\gvkey_panjiva.csv"

        if self.sample == True:
            # 读取 Sample data，只是用 2018 和 2019 年两年的数据
            # Sample data 是从元数据中随机抽样来的
            self.year_list = [2018, 2019]
            self.data_paths = [r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\sample\2018.csv",
                               r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\sample\2019.csv"]
            for i, data_path in enumerate(self.data_paths):
                data = pd.read_csv(data_path)
                print(f"No.{i}, and reading data of year {self.year_list[i]} \n")
                data = self.form_data(data)
                self.data_list.append(data)

        else:
            # 读取真实数据
            self.year_list = [i for i in range(2008, 2020)]
            self.dir_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data"
            self.data_paths = [self.dir_path + r"\test" + str(i) + "new.csv" for i in self.year_list]
            for i, data_path in enumerate(self.data_paths):
                data = pd.read_csv(data_path, index_col=0)
                print(f"No.{i}, and reading data of year {self.year_list[i]} \n")
                data = self.form_data(data)
                self.data_list.append(data)

    def get_SC(self):
        """
        构建 SC 变量
        在 groupby 的时候
        按照按照母公司还是本公司需要考虑
        hscode 需要改成只选用前两位
        否则会出现大量的数据都是 1 的情况
        """
        print("Calculating SC\n")
        SC_list = []
        for i, year in enumerate(self.year_list):
            print(f"Processing data on year {year}\n")
            data = self.data_list[i]
            IVj = data.groupby([
                'gv_conprt',
                'hscode',
                'shpciqcompanyid']).agg({'valueofgoodsusd': 'sum'})

            IV = data.groupby([
                'gv_conprt',
                'hscode']).agg({'valueofgoodsusd': 'sum'})
            HI = IVj / IV
            HI = HI * HI
            HI = HI.sum(level=[0, 1])
            numerator = HI * IV
            numerator = numerator.sum(level=0)
            denominator = IV.sum(level=0)
            SC = numerator / denominator
            SC["year"] = datetime.datetime.strptime(str(year), "%Y")

            if i == 0:
                SC_total = SC
            else:
                SC_total = pd.concat([SC_total, SC], axis=0)

        SC_total = SC_total.reset_index(level=0)
        SC_total.columns = ["gvkey", "SC", "year"]
        SC_total.set_index(["gvkey", "year"])
        print("SC\n", SC_total["SC"].describe())
        self.GSS["SC"] = SC_total


    def get_RS(self):
        """
        构建 RS 变量
        """
        print("Calculating RS\n")
        for i, year in enumerate(self.year_list):
            print(f"Processing data on year {year}\n")
            data = self.data_list[i]
            data["arrivaldate"] = pd.to_datetime(data["arrivaldate"])
            data["arrivalmonth"] = data["arrivaldate"].dt.month
            gb_supplier = data.groupby(['gv_conprt',
                                        'hscode',
                                        'shpciqcompanyid']).agg({'arrivalmonth': 'count'})

            gb_no_supplier = data.groupby(['gv_conprt',
                                           'hscode']).agg({'arrivalmonth': 'sum'})
            IV = data.groupby(['gv_conprt',
                               'hscode']).agg({'valueofgoodsusd': 'sum'})
            RBI = gb_supplier / gb_no_supplier
            RBI = RBI.mean(level=[0, 1])
            RBI.columns = ["value"]
            IV.columns = ["value"]
            numernator = RBI * IV
            numernator = numernator.sum(level=0)
            denominator = IV.sum(level=0)
            RS = numernator / denominator
            RS["year"] = datetime.datetime.strptime(str(year), "%Y")

            if i == 0:
                RS_total = RS
            else:
                RS_total = pd.concat([RS_total, RS], axis=0)

        RS_total = RS_total.reset_index(level=0)
        RS_total.columns = ["gvkey", "RS", "year"]
        RS_total.set_index(["gvkey", "year"])

        print("RS\n", RS_total["RS"].describe())
        self.GSS["RS"] = RS_total

    def get_GL(self):
        """
        构建 GL 变量
        因为没有 shipping time 的数据 所以是用 shipment 替代数据
        """
        COGS_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\others\compustat.csv"
        COGS = pd.read_csv(COGS_path,
                           usecols=["gvkey", "fyear", "cogs"])
        COGS["year"] = pd.Series(COGS["fyear"], dtype=int)
        COGS = COGS.drop(["fyear"], axis=1)

        shipment_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\others\Shiptime.xlsx"
        shipment = pd.read_excel(shipment_path).loc[:, ["Country", "Shiptime"]]
        shipment["Country"] = shipment["Country"].str.lower()
        shipment.columns = ['shpmtorigin', "Shiptime"]

        print(f"Calculating GL\n")
        for i, year in enumerate(self.year_list):
            print(f"Processing data on year {year}\n")

            data = self.data_list[i]
            IVj = data.groupby(['gv_conprt',
                                'shpmtorigin']).agg({'valueofgoodsusd': 'sum'})
            IVj_index = IVj.index
            IVj = pd.merge(IVj, shipment, on="shpmtorigin", how="left")
            IVj.index = IVj_index
            IVj["value"] = IVj["valueofgoodsusd"] * IVj["Shiptime"]
            numerator = IVj.loc[:, ["value"]].sum(level=0)

            denominator = IVj.loc[:, ["Shiptime"]].sum(level=0)
            denominator.columns = ["value"]
            GL = numerator / denominator
            GL["year"] = year

            GL = GL.reset_index(level=0)
            GL.columns = ["gvkey", "GL", "year"]
            GL.set_index(["gvkey", "year"])
            GL = pd.merge(GL, COGS, on=["gvkey", "year"], how="left")
            GL["GL"] = GL["GL"] / GL["cogs"] / 100
            GL = GL.drop("cogs", axis=1)

            if i == 0:
                GL_total = GL
            else:
                GL_total = pd.concat([GL_total, GL], axis=0)
        GL_total["year"] = pd.to_datetime(GL_total["year"], format="%Y")
        GL_total.set_index(["gvkey", "year"])
        print("GL\n", GL_total["GL"].describe())
        self.GSS["GL"] = GL_total

    def get_LE(self):
        """
        获取 LE 变量
        用到了来自 world bank 的数据
        """
        LPI_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\others\LPI.xlsx"
        LPI_2018 = pd.read_excel(LPI_path, sheet_name="2018", header=2, usecols=[0, 2])
        LPI_2016 = pd.read_excel(LPI_path, sheet_name="2016", header=2, usecols=[0, 2])
        LPI_2014 = pd.read_excel(LPI_path, sheet_name="2014", header=2, usecols=[0, 2])
        LPI_2012 = pd.read_excel(LPI_path, sheet_name="2012", header=2, usecols=[0, 2])
        LPI_2010 = pd.read_excel(LPI_path, sheet_name="2010", header=2, usecols=[0, 2])
        LPI_2007 = pd.read_excel(LPI_path, sheet_name="2007", header=2, usecols=[0, 2])
        LPI_08_19 = [LPI_2007, LPI_2007,
                     LPI_2010, LPI_2010,
                     LPI_2012, LPI_2012,
                     LPI_2014, LPI_2014,
                     LPI_2016, LPI_2016,
                     LPI_2018, LPI_2018]

        for i, year in enumerate(self.year_list):
            print(f"Processing {i} on year {year}\n")
            LPI = LPI_08_19[i]
            LPI.columns = ['Country', 'score']
            LPI["Country"] = LPI["Country"].str.lower()
            LPI.columns = ["shpmtorigin", "score"]

            data = self.data_list[i]
            IVj = data.groupby(['gv_conprt',
                                'hscode',
                                'shpmtorigin']).agg({'valueofgoodsusd': 'sum'})
            IVj_m = pd.merge(IVj, LPI, on='shpmtorigin', how='left')
            IVj_m.index = IVj.index
            IVj_m["value"] = IVj_m["valueofgoodsusd"] * IVj_m["score"]
            LEc_numer = IVj_m["value"].sum(level=[0, 1]).to_frame()
            LEc_denom = IVj.sum(level=[0, 1])
            LEc_denom.columns = ["value"]
            LEc = LEc_numer / LEc_denom
            IV = data.groupby(['gv_conprt',
                               'hscode']).agg({'valueofgoodsusd': 'sum'})
            IV.columns = ["value"]
            numerator = IV * LEc
            numerator = numerator.sum(level=0)
            denominator = IV.sum(level=0)
            LE = numerator / denominator
            LE["year"] = datetime.datetime.strptime(str(year), "%Y")

            if i == 0:
                LE_total = LE
            else:
                LE_total = pd.concat([LE_total, LE], axis=0)
        LE_total = LE_total.reset_index(level=0)
        LE_total.columns = ["gvkey", "LE", "year"]
        LE_total.set_index(["gvkey", "year"])
        print("LE\n", LE_total["LE"].describe())
        self.GSS["LE"] = LE_total

fa = FA()
