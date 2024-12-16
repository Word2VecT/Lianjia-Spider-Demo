import json
import os

import pandas as pd

# 定义城市缩写到全称的映射
city_full_names = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 定义城市列表及对应的 JSON 文件名
cities = {
    "bj": "data/bj_rent_house_data.json",
    "sh": "data/sh_rent_house_data.json",
    "gz": "data/gz_rent_house_data.json",
    "sz": "data/sz_rent_house_data.json",
    "changde": "data/changde_rent_house_data.json",
}

# 创建输出目录（如果不存在）
output_dir = "data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 初始化一个字典用于存储所有城市的数据
city_data = {}

# 遍历每个城市的 JSON 文件并读取数据
for city_code, filename in cities.items():
    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在，跳过 {city_code} 城市。")
        continue

    with open(filename, encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"文件 {filename} 解析失败，跳过 {city_code} 城市。")
            continue

    # 提取区域和价格信息
    records = []
    for listing in data:
        des = listing.get("des", [])
        if len(des) < 1:
            # 如果 'des' 列表长度不足，跳过该记录
            continue
        district = des[0].strip()

        # 添加过滤条件：如果区域名称含有数字，跳过该记录
        if any(char.isdigit() for char in district):
            continue

        price_str = listing.get("price", "0元/月").replace("元/月", "").replace(",", "").strip()
        try:
            price = float(price_str)
        except ValueError:
            price = None

        if price is not None and price > 0:
            records.append({"区域": district, "价格（元/月）": price})

    if not records:
        print(f"{city_code} 城市没有有效的数据。")
        continue

    # 创建 DataFrame
    df_city = pd.DataFrame(records)

    # 计算每个区域的平均价格
    df_avg = df_city.groupby("区域")["价格（元/月）"].mean().reset_index()
    df_avg.rename(columns={"价格（元/月）": "平均价格（元/月）"}, inplace=True)

    # 保存到字典
    city_data[city_code] = df_avg

    # 导出为 CSV 文件
    output_filename = os.path.join(output_dir, f"{city_code}_region_price_data.csv")
    df_avg.to_csv(output_filename, index=False, encoding="utf-8-sig")
    print(f"{city_code} 城市的区域平均租金已成功保存到 {output_filename}")
