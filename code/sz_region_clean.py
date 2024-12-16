import pandas as pd


def clean_data(df):
    # Delete rows where 区域 is 精选
    df = df[df["区域"] != "精选"]
    # Delete rows where 区域 is 精选
    df = df[df["区域"] != "大鹏新区"]
    return df


# 已从 URI 中加载变量“df”: /Users/tang/Course/Python 程序设计/data_capture/data/sz_region_price_data.csv
df = pd.read_csv(r"/Users/tang/Course/Python 程序设计/data_capture/data/sz_region_price_data.csv")

df_clean = clean_data(df.copy())
df_clean.head()
