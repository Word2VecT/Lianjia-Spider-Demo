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
output_dir = "data"  # 使用单独的目录以避免与输入文件混淆
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 定义有效的朝向
valid_directions = {"东", "南", "西", "北", "南北"}

# 遍历每个城市的 JSON 文件并读取数据
for city_code, filename in cities.items():
    city_name = city_full_names.get(city_code, city_code)

    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在，跳过 {city_name} 城市。")
        continue

    with open(filename, encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"文件 {filename} 解析失败，跳过 {city_name} 城市。")
            continue

    # 提取朝向和单位面积租金信息
    records = []
    for listing in data:
        des = listing.get("des", [])

        # 提取朝向
        direction = ""
        for item in des:
            if item in valid_directions:
                direction = item
                break

        if not direction:
            continue

        # 提取面积
        area_str = ""
        for item in des:
            if "㎡" in item:
                area_str = item.replace("㎡", "").replace(",", "").strip()
                break

        if not area_str:
            continue

        try:
            area = float(area_str)
            if area <= 0:
                continue
        except ValueError:
            continue

        # 提取租金
        price_str = listing.get("price", "0元/月").replace("元/月", "").replace(",", "").strip()
        try:
            price = float(price_str)
            if price <= 0:
                continue
        except ValueError:
            continue

        # 计算单位面积租金（元/月/㎡）
        unit_rent = price / area

        records.append({"朝向": direction, "单位面积租金（元/月/㎡）": unit_rent})

    if not records:
        print(f"{city_name} 城市没有有效的数据。")
        continue

    # 创建 DataFrame
    df_city = pd.DataFrame(records)

    # 导出为 CSV 文件
    output_filename = os.path.join(output_dir, f"{city_code}_direction_unit_price_data.csv")
    df_city.to_csv(output_filename, index=False, encoding="utf-8-sig")
    print(f"{city_name} 城市的朝向单位面积租金已成功保存到 {output_filename}")
