import psycopg2
import pandas as pd
from pandas import ExcelWriter
import re
import numpy as np
from scipy import stats


class controller():
    def __init__(self):
        self.year_list= [i for i in range(2007,2021)]
        
    def generate_query(self,year):
        query_base = "lcusimport"
        """
        copy(select 
                panjivarecordid,
                arrivaldate,
                conciqcompanyid,
                conultcompanyid,
                shpmtorigin,
                shpciqcompanyid,
                shpultcompanyid
                volumeteu,
                quantity_num,
                unit,
                weightkg,
                valueofgoodsusd,
                hscode
        from lcusimport{}
        )
        TO 'F:\lc\panjiva\src\yilindata{}.csv' DELIMITER ',' CSV HEADER
        """
        year_query = query_base.format(str(year),str(year))
        return year_query
    
    def excute_query2df(self, query):
        """
        执行 query
        """
        conn = psycopg2.connect(host="127.0.0.1", user="postgres", password="root", database="CIQ_Target")
        cur = conn.cursor()
        cur.execute(query)
    #         rows = cur.fetchall()
    #         df = pd.DataFrame(rows)
    #         df.columns = [desc[0] for desc in cur.description]
        cur.close()
    
    def get_all_data(self):
        for year in self.year_list:
            print(year)
            query= self.generate_query(year)
            self.excute_query2df(query)