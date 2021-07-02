import pandas as pd
import warnings
import re
import numpy as np

warnings.filterwarnings('ignore')





class FA():
    """
    用于制造 panjiva data 的相关变量
    """

    def __init__(self):

        self.sample = True
        self.set_attribute()

    def set_attribute(self):
        self.year_list = []
        self.data_list = []
        self.column_name = ['index', 'panjivarecordid', 'arrivaldate', 'conciqcompanyid',
                            'conultcompanyid', 'shpmtorigin', 'shpciqcompanyid', 'shpultcompanyid',
                            'quantity_num', 'unit', 'weightkg', 'valueofgoodsusd', 'hscode',
                            'gv_con', 'gv_conprt', 'gv_shp', 'gv_shpprt']
        self.drop_na_col = ["conultcompanyid",
                            "shpciqcompanyid",
                            "hscode",
                            "valueofgoodsusd",
                            "gv_conprt"]

    def form_hscode(self, hscode):
        hscode = re.split(':', str(hscode))[-1][:6]
        return hscode

    def form_data(self, data):
        data = data.dropna(subset=self.drop_na_col)
        data["hscode"] = data["hscode"].apply(self.form_hscode)
        data['shpmtorigin'] = data['shpmtorigin'].str.lower()
        return data

    def read_data(self):
        if self.sample == True:
            self.year_list = [2018, 2019]
            self.data_paths = [r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\sample\2018.csv",
                               r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\sample\2019.csv"]
            for i, data_path in enumerate(self.data_paths):
                data = pd.read_csv(data_path)
                print(f"No.{i}, and reading data of year {self.year_list[i]} \n")
                data = self.form_data(data)
                self.data_list.append(data)

        else:
            self.year_list = [i for i in range(2008, 2020)]
            self.dir_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data"
            self.data_paths = [self.dir_path + r"\test" + str(i) + "new.csv" for i in self.year_list]
            for i, data_path in enumerate(self.data_paths):
                data = pd.read_csv(data_path, index_col=0)
                print(f"No.{i}, and reading data of year {self.year_list[i]} \n")
                data = self.form_data(data)
                self.data_list.append(data)


    def get_SC(self):
        print("Calculating SC\n")
        SC_list = []
        for i, year in enumerate(self.year_list):
            print(f"Processing data on year {year}\n")
            data = self.data_list[i]
            IVj = data.groupby(['conultcompanyid',
                                'hscode',
                                'shpciqcompanyid']).agg({'valueofgoodsusd': 'sum'})

            IV = data.groupby(['conultcompanyid',
                               'hscode']).agg({'valueofgoodsusd': 'sum'})
            HI = IVj / IV
            HI = HI * HI
            HI = HI.sum(level=[0, 1])
            numerator = HI * IV
            numerator = numerator.sum(level=0)
            denominator = IV.sum(level=0)
            SC = numerator / denominator

            if i == 0:
                SC_total = SC
            else:
                SC_total = pd.concat([SC_total, SC], axis=0)

        print("SC\n", SC_total.describe())

    def get_RS(self):

        print("Calculating RS\n")
        for i, year in enumerate(self.year_list):
            print(f"Processing data on year {year}\n")
            data = self.data_list[i]
            data["arrivaldate"] = pd.to_datetime(data["arrivaldate"])
            data["arrivalmonth"] = data["arrivaldate"].dt.month
            gb_supplier = data.groupby(['conultcompanyid',
                                        'hscode',
                                        'shpciqcompanyid']).agg({'arrivalmonth': 'count'})

            gb_no_supplier = data.groupby(['conultcompanyid',
                                           'hscode']).agg({'arrivalmonth': 'sum'})
            IV = data.groupby(['conultcompanyid',
                               'hscode']).agg({'valueofgoodsusd': 'sum'})
            RBI = gb_supplier / gb_no_supplier
            RBI = RBI.mean(level=[0, 1])
            RBI.columns = ["value"]
            IV.columns = ["value"]
            numernator = RBI * IV
            numernator = numernator.sum(level=0)
            denominator = IV.sum(level=0)
            RS = numernator / denominator

            if i == 0:
                RS_total = RS
            else:
                RS_total = pd.concat([RS_total, RS], axis=0)

        print("RS\n", RS_total.describe())

    def get_GL(self):

        print(f"Calculating GL\n")
        for i, year in enumerate(self.year_list):
            print(f"Processing data on year {year}\n")

            shipment_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\others\Shiptime.xlsx"
            shipment = pd.read_excel(shipment_path).loc[:, ["Country", "Shiptime"]]
            shipment["Country"] = shipment["Country"].str.lower()
            shipment.columns = ['shpmtorigin', "Shiptime"]


            data = self.data_list[i]
            IVj = data.groupby(['conultcompanyid',
                                'shpmtorigin']).agg({'valueofgoodsusd': 'sum'})
            IVj_index = IVj.index
            IVj = pd.merge(IVj, shipment, on="shpmtorigin", how="left")
            IVj.index = IVj_index
            IVj["value"] = IVj["valueofgoodsusd"] * IVj["Shiptime"]
            numerator = IVj.loc[:, ["value"]].sum(level=0)

            denominator = IVj.loc[:, ["Shiptime"]].sum(level=0)
            denominator.columns = ["value"]
            GL = numerator / denominator
            COGS = data.groupby('conultcompanyid').agg({'valueofgoodsusd': 'sum'})
            COGS.columns = ["value"]
            GL = 100 * GL / COGS

            if i == 0:
                GL_total = GL
            else:
                GL_total = pd.concat([GL_total, GL], axis=0)

        print("GL\n", GL_total.describe())

    def get_LE(self):

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
            IVj = data.groupby(['conultcompanyid',
                                'hscode',
                                'shpmtorigin']).agg({'valueofgoodsusd': 'sum'})
            IVj_m = pd.merge(IVj, LPI, on='shpmtorigin', how='left')
            IVj_m.index = IVj.index
            IVj_m["value"] = IVj_m["valueofgoodsusd"] * IVj_m["score"]
            LEc_numer = IVj_m["value"].sum(level=[0, 1]).to_frame()
            LEc_denom = IVj.sum(level=[0, 1])
            LEc_denom.columns = ["value"]
            LEc = LEc_numer / LEc_denom
            IV = data.groupby(['conultcompanyid',
                               'hscode']).agg({'valueofgoodsusd': 'sum'})
            IV.columns = ["value"]
            numerator = IV * LEc
            numerator = numerator.sum(level=0)
            denominator = IV.sum(level=0)
            LE = numerator / denominator

            if i == 0:
                LE_total = LE
            else:
                LE_total = pd.concat([LE_total, LE], axis=0)

        print("LE\n", LE_total.describe())
