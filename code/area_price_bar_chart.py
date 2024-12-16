import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 定义城市缩写到全称的映射
city_full_names = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 定义城市列表及对应的 CSV 文件名
cities = {
    "bj": "data/bj_area_price_data.csv",
    "sh": "data/sh_area_price_data.csv",
    "gz": "data/gz_area_price_data.csv",
    "sz": "data/sz_area_price_data.csv",
    "changde": "data/changde_area_price_data.csv",
}

# 创建输出目录（如果不存在）
output_dir = "figure"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 设置绘图风格
sns.set_theme(style="whitegrid")

# 遍历每个城市的 CSV 文件并绘制条形图
for city_code, csv_path in cities.items():
    city_name = city_full_names.get(city_code, city_code)

    if not os.path.exists(csv_path):
        print(f"文件 {csv_path} 不存在，跳过 {city_name} 城市。")
        continue

    # 读取 CSV 文件
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except Exception as e:
        print(f"读取文件 {csv_path} 失败，错误：{e}")
        continue

    # 检查必要的列是否存在
    if "板块" not in df.columns or "平均价格（元/月）" not in df.columns:
        print(f"文件 {csv_path} 缺少必要的列，跳过 {city_name} 城市。")
        continue

    # 删除缺失值
    df = df.dropna(subset=["板块", "平均价格（元/月）"])

    # 按平均价格从低到高排序
    df_sorted = df.sort_values(by="平均价格（元/月）", ascending=True)

    # 设置图形大小
    plt.figure(figsize=(12, 8))
    plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 适用于macOS和Windows
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    # 绘制条形图
    bar_plot = sns.barplot(data=df_sorted, x="板块", y="平均价格（元/月）", hue="板块", palette="viridis", legend=False)

    # 设置标题和标签
    plt.title(f"{city_name}各板块平均租金对比", fontsize=16, fontweight="bold")
    plt.xlabel("板块", fontsize=14)
    plt.ylabel("平均租金（元/月）", fontsize=14)

    # 旋转 x 轴标签以避免重叠
    plt.xticks(rotation=45, ha="right", fontsize=300 / len(df_sorted["板块"].unique()) + 1.5)
    plt.yticks(fontsize=12)

    # 调整布局以防止标签被截断
    plt.tight_layout()

    # 保存图表，文件名使用英文首字母缩写
    output_filename = os.path.join(output_dir, f"{city_code}_area_price_bar_chart.png")
    plt.savefig(output_filename, dpi=1200, bbox_inches="tight")
    plt.close()

    print(f"{city_name} 城市的条形图已成功保存到 {output_filename}")
