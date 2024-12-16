import json
import os

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

# 初始化两个列表用于存储各城市的租金和单位面积统计信息
rent_data = []
unit_price_data = []

for city, filename in cities.items():
    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在，跳过 {city} 城市。")
        continue

    with open(filename, encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"文件 {filename} 解析失败，跳过 {city} 城市。")
            continue

    rent_prices = []
    rent_per_sqm = []

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
        area_str = ""
        for item in des:
            if "㎡" in item:
                area_str = item.replace("㎡", "").replace(",", "").strip()
                break
        try:
            area = float(area_str)
        except ValueError:
            continue

        price_sqm = price / area if area > 0 else 0.0

        rent_prices.append(price)
        rent_per_sqm.append(price_sqm)

    # 转换为 NumPy 数组以便计算
    rent_prices_np = np.array(rent_prices)
    rent_per_sqm_np = np.array(rent_per_sqm)

    if len(rent_prices_np) == 0:  # 如果所有数据被过滤，跳过该城市
        print(f"城市 {city} 的数据全部无效，跳过统计。")
        continue

    # 计算租金统计信息
    rent_stats = {
        "城市": city,
        "数据量": len(rent_prices_np),
        "均价（元/月）": np.round(np.mean(rent_prices_np), 2),
        "标准差（元/月）": np.round(np.std(rent_prices_np, ddof=1), 2),
        "最高价（元/月）": np.round(np.max(rent_prices_np), 2),
        "最低价（元/月）": np.round(np.min(rent_prices_np), 2),
        "中位数（元/月）": np.round(np.median(rent_prices_np), 2),
        "25%分位数（元/月）": np.round(np.percentile(rent_prices_np, 25), 2),
        "75%分位数（元/月）": np.round(np.percentile(rent_prices_np, 75), 2),
    }
    rent_data.append(rent_stats)

    # 计算单位面积租金统计信息
    unit_price_stats = {
        "城市": city,
        "数据量": len(rent_per_sqm_np),
        "均价（元/㎡）": np.round(np.mean(rent_per_sqm_np), 2),
        "标准差（元/㎡）": np.round(np.std(rent_per_sqm_np, ddof=1), 2),
        "最高价（元/㎡）": np.round(np.max(rent_per_sqm_np), 2),
        "最低价（元/㎡）": np.round(np.min(rent_per_sqm_np), 2),
        "中位数（元/㎡）": np.round(np.median(rent_per_sqm_np), 2),
        "25%分位数（元/㎡）": np.round(np.percentile(rent_per_sqm_np, 25), 2),
        "75%分位数（元/㎡）": np.round(np.percentile(rent_per_sqm_np, 75), 2),
    }
    unit_price_data.append(unit_price_stats)

# 创建 DataFrame
rent_df = pd.DataFrame(rent_data)
unit_price_df = pd.DataFrame(unit_price_data)

# 排序城市（可选）
rent_df = rent_df.set_index("城市")
unit_price_df = unit_price_df.set_index("城市")
rent_df = rent_df.loc[["bj", "sh", "gz", "sz", "changde"]].reset_index()
unit_price_df = unit_price_df.loc[["bj", "sh", "gz", "sz", "changde"]].reset_index()

# 导出为 CSV 文件
rent_output_filename = "data/price_data.csv"
unit_price_output_filename = "data/unit_price_data.csv"
rent_df.to_csv(rent_output_filename, index=False, encoding="utf-8-sig")
unit_price_df.to_csv(unit_price_output_filename, index=False, encoding="utf-8-sig")

print(f"租金统计信息已成功导出到 {rent_output_filename}")
print(f"单位面积租金统计信息已成功导出到 {unit_price_output_filename}")
