import pandas as pd
import numpy as np
import re

flight_path = "/Users/meron/Desktop/01_Work/data_syl/flight2019.xls"
gvkey_path = "/Users/meron/Desktop/01_Work/data_syl/name_gvkey.xlsx"


def drop_suffix(name):
    # suffix_set = ["INC", "CORP", "-CL A", "LTD", "FD", "NV"]
    suffix_set = r"\b(INC|CORP|LTD|\-CL A|FD|NV|CO|LLC|LP|HONGDINGS|CA|-NM|Company)\b"
    name.strip()
    name_list = re.split(suffix_set, name.upper())
    return name_list[0]


def split_proportion(name):
    pattern = r"(\(\d+%\))"
    word_splits = re.split(pattern, name)
    word_splits = [word.replace(";", "", ).strip() for word in word_splits if word != ""]
    return


def get_split_name(series):
    if pd.isna(series["PARENT COMPANIES"]):
        series["name"] = np.nan
        series["percent"] = np.nan
    else:
        items = series["PARENT COMPANIES"].upper().split("(")
        series["name"] = drop_suffix(items[0])
        if len(items) == 2:
            series["percent"] = items[1].split(")")[0]
        elif len(items) == 1:
            series["percent"] = np.nan
        print(series["index"])
    return series


gvkey_data = pd.read_excel(gvkey_path)
conm = gvkey_data["conm"]
gvkey_data["name_modified"] = conm.apply(drop_suffix)
gvkey_data = gvkey_data.drop(["conm"], axis=1)
gvkey_data.columns = ["gvkey", "name"]
gvkey_data["gvkey"] = gvkey_data["gvkey"].astype(str)

flight = pd.read_excel(flight_path)
flight["PARENT COMPANIES"] = flight["PARENT COMPANIES"].str.strip(";").str.strip()
flight = flight.drop('PARENT COMPANIES', axis=1).join(flight['PARENT COMPANIES'].str.split(';', expand=True).stack().reset_index(level=1, drop=True).rename('PARENT COMPANIES'))
flight["PARENT COMPANIES"] = flight["PARENT COMPANIES"].str.upper().str.strip().str.replace(",", "")
flight.index = range(flight.shape[0])


pc_name = flight["PARENT COMPANIES"].to_frame()
pc_name["index"] = pc_name.index
pc_name_modified = pc_name.apply(get_split_name, axis=1)
pc_name_modified = pc_name_modified.drop(['PARENT COMPANIES', 'index'], axis=1)
pc_name_modified = pd.merge(pc_name_modified, gvkey_data, on="name", how="left")
flight = pd.concat([flight, pc_name_modified], axis=1)
flight.to_excel("/Users/meron/Desktop/01_Work/data_syl/flight2019.xlsx", index=False)
