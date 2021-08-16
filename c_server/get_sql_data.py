import psycopg2
import pandas as pd
import time
import os
from pandas import ExcelWriter
import re
import numpy as np
from scipy import stats

def GetRunTime(func):
    def call_func(*args, **kwargs):
        begin_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        Run_time = end_time - begin_time
        print(str(func.__name__)+" function time is "+str(Run_time))
        return ret
    return call_func



year_list= [i for i in range(2007,2021)]
Query_Path = ".\panjiva_code\Query01.sql"
column_name = pd.read_csv(r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\column_name.csv")



def generate_query(Query_Path, year):
    """
    Using for generating SQL query
    :return: the return words
    """
    with open(Query_Path, 'r') as sql:
        base_query = sql.read()
    year_query = base_query.format(str(year), str(year))
    return year_query

@GetRunTime
def excute_query2df(query, year):
    conn = psycopg2.connect(host="127.0.0.1", user="postgres", password="root", database="CIQ_Target")
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    df = pd.DataFrame(rows)

    df.to_csv(r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\test{}.csv".format(str(year)))
    df.columns = [desc[0] for desc in cur.description]
    cur.close()


for year in year_list:
    # year = 2007
    Query = generate_query(Query_Path, year)
    excute_query2df(Query, year)

Column_Name = [
    "index",
    "panjivarecordid",
    "arrivaldate",
    "conciqcompanyid",
    "conultcompanyid",
    "shpmtorigin",
    "shpciqcompanyid",
    "shpultcompanyid",
    "quantity_num",
    "unit",
    "weightkg",
    "valueofgoodsusd",
    "hscode"]

data_paths = [r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\test" + str(i) + ".csv" for i in range(2007, 2021)]
gvkey_path = r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\gvkey_panjiva.csv"

@GetRunTime
def merge_data(data_path, gvkey_path):
    # data_path = data_paths[0]
    pj_data = pd.read_csv(data_path)
    pj_data.columns = Column_Name
    # pj_data = pj_data.drop('PARENT COMPANIES', axis=1).join(
    #     pj_data['PARENT COMPANIES'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename(
    #         'PARENT COMPANIES'))
    gv_data = pd.read_csv(gvkey_path).drop("Unnamed: 0", axis=1).drop_duplicates('panjivaid')


    for col in ["conciqcompanyid", "conultcompanyid", "shpciqcompanyid", "shpultcompanyid"]:
        # col = "conciqcompanyid"
        pj_data = pd.merge(pj_data, gv_data,
                           left_on=col, right_on="panjivaid",
                           how="left", validate='m:1')

        pj_data = pj_data.drop("panjivaid", axis=1).rename({"gvkey":"g_"+col})
    tempt_col_name = list(pj_data.columns)
    tempt_col_name[-4] = "gv_con"
    tempt_col_name[-3] = "gv_conprt"
    tempt_col_name[-2] = "gv_shp"
    tempt_col_name[-1] = "gv_shpprt"
    pj_data.columns = tempt_col_name

    name, ext = os.path.splitext(data_path)
    pj_data.to_csv(name + "new" + ext)

for data_path in data_paths:
    merge_data(data_path, gvkey_path)

data_paths = [r"C:\Users\Wu Jing\Documents\GitHub\panjiva_data\test" + str(i) + "new.csv" for i in range(2007, 2021)]



