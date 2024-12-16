import pandas as pd


def clean_data(df):
    # Remove specified rows
    df = df[~df["区域"].isin(["亦庄开发区", "北京经济技术开发区", "精选"])]
    # Append '区' to all text in '区域' column
    df["区域"] = df["区域"] + "区"
    return df


# 已从 URI 中加载变量“df”: /Users/tang/Course/Python 程序设计/data_capture/data/bj_region_price_data.csv
df = pd.read_csv(r"/Users/tang/Course/Python 程序设计/data_capture/data/bj_region_price_data.csv")

df_clean = clean_data(df.copy())
df_clean.head()
