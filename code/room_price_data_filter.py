import json
import os
import re

import numpy as np
import pandas as pd

# 定义城市列表及对应的文件名
cities = {
    "bj": "data/bj_rent_house_data.json",
    "sh": "data/sh_rent_house_data.json",
    "gz": "data/gz_rent_house_data.json",
    "sz": "data/sz_rent_house_data.json",
    "changde": "data/changde_rent_house_data.json",
}

# 定义城市缩写到全称的映射
city_full_names = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 初始化一个列表用于存储所有有效的数据
all_rent_data = []

# 遍历每个城市的 JSON 文件
for city, filename in cities.items():
    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在，跳过 {city_full_names.get(city, city)} 城市。")
        continue

    with open(filename, encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"文件 {filename} 解析失败，跳过 {city_full_names.get(city, city)} 城市。")
            continue

    for listing in data:
        # 提取租金
        price_str = listing.get("price", "0元/月")
        try:
            price = float(price_str.replace("元/月", "").replace(",", "").strip())
        except ValueError:
            price = 0.0

        if price <= 0:  # 跳过价格为 0 或负值的数据
            continue

        # 提取面积
        des = listing.get("des", [])

        room_type = ""
        for item in des:
            match = re.match(r"(\d+)室", item)
            if match:
                num = int(match.group(1))
                room_type_dict = {1: "一居", 2: "二居", 3: "三居"}
                room_type = room_type_dict.get(num, f"{num}居")

        if not room_type:
            continue  # 跳过无法识别的房屋类型

        # 记录有效的数据
        all_rent_data.append(
            {
                "城市": city,
                "房屋类型": room_type,
                "价格（元/月）": price,
            }
        )

# 如果没有有效的数据，退出程序
if not all_rent_data:
    print("没有有效的租金数据可供处理。")
    exit(1)

# 创建 DataFrame
df = pd.DataFrame(all_rent_data)

# 筛选一居、二居、三居的数据
df = df[df["房屋类型"].isin(["一居", "二居", "三居"])]

# 定义房屋类型的排序优先级
room_type_order = {"三居": 3, "二居": 2, "一居": 1}


# 计算统计指标（包含数据量）
def compute_statistics(group, price_col):
    return pd.Series(
        {
            "数据量": len(group),
            "均价（元/月）": np.round(group[price_col].mean(), 2),
            "标准差（元/月）": np.round(group[price_col].std(), 2),
            "最高价（元/月）": np.round(group[price_col].max(), 2),
            "最低价（元/月）": np.round(group[price_col].min(), 2),
            "中位数（元/月）": np.round(group[price_col].median(), 2),
            "25%分位数（元/月）": np.round(group[price_col].quantile(0.25), 2),
            "75%分位数（元/月）": np.round(group[price_col].quantile(0.75), 2),
        }
    )


# 按城市和房屋类型分组并计算统计指标
results = []
for (city, room_type), group in df.groupby(["城市", "房屋类型"]):
    stats = compute_statistics(group, "价格（元/月）")
    stats["城市"] = city
    stats["房屋类型"] = room_type
    results.append(stats)

rent_stats = pd.DataFrame(results)

# 添加排序优先级
rent_stats["排序优先级"] = rent_stats["房屋类型"].map(room_type_order)

# 导出为五个 CSV 文件，每个文件对应一个城市
output_dir = "data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for city in rent_stats["城市"].unique():
    city_data = rent_stats[rent_stats["城市"] == city]
    # 根据房屋类型排序
    city_data = city_data.sort_values("排序优先级").drop(columns=["排序优先级"])
    # 选择需要的列
    city_data = city_data[
        [
            "房屋类型",
            "数据量",
            "均价（元/月）",
            "标准差（元/月）",
            "最高价（元/月）",
            "最低价（元/月）",
            "中位数（元/月）",
            "25%分位数（元/月）",
            "75%分位数（元/月）",
        ]
    ]
    # 定义输出文件路径，使用城市首字母缩写
    output_file = os.path.join(output_dir, f"{city}_room_price_data.csv")
    # 导出为 CSV
    city_data.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"{city} 的租金统计信息已成功保存到 {output_file}")
