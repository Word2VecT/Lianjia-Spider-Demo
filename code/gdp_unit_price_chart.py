import os

import matplotlib.pyplot as plt
import numpy as np  # 直接导入 numpy
import pandas as pd
import seaborn as sns
from scipy.stats import gaussian_kde

# 定义城市缩写与全称的映射
city_full_names = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 定义城市列表及对应的 CSV 文件名
cities = {
    "bj": "data/bj_unit_price_data.csv",
    "sh": "data/sh_unit_price_data.csv",
    "gz": "data/gz_unit_price_data.csv",
    "sz": "data/sz_unit_price_data.csv",
    "changde": "data/changde_unit_price_data.csv",
}

# 定义人均 GDP（单位：元）
gdp_data = {"北京": 200278, "上海": 190321, "广州": 161634, "深圳": 195231, "常德": 84342}

# 定义颜色列表（选择美观的调色板）
colors = sns.color_palette("Set2", n_colors=len(cities))  # 为每个城市分配不同颜色
city_colors = {city_full_names[code]: colors[idx] for idx, code in enumerate(cities.keys())}

# 创建输出目录（如果不存在）
output_dir = "figure"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 初始化 unit_price_data 为 None
unit_price_data = None

# 遍历每个城市的 CSV 文件并读取数据
for city_code, filename in cities.items():
    city_name = city_full_names.get(city_code, city_code)

    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在，跳过 {city_name} 城市。")
        continue

    try:
        df = pd.read_csv(filename, encoding="utf-8-sig")
    except Exception as e:
        print(f"读取文件 {filename} 失败，错误：{e}")
        continue

    if df.empty:
        print(f"{city_name} 城市的数据为空，跳过。")
        continue

    # 计算均值和标准差
    mean = df["单位面积租金（元/月/㎡）"].mean()
    std = df["单位面积租金（元/月/㎡）"].std()

    # 过滤掉超过均值 + 2*标准差的数据，并创建副本
    df_filtered = df[df["单位面积租金（元/月/㎡）"] <= (mean + 2 * std)].copy()

    if df_filtered.empty:
        print(f"{city_name} 城市在过滤后没有有效的数据。")
        continue

    # 添加城市名称，使用 .loc 避免 SettingWithCopyWarning
    df_filtered.loc[:, "城市"] = city_name

    # 确保 DataFrame 只有 ['城市', '单位面积租金（元/月/㎡）'] 两列
    df_filtered = df_filtered[["城市", "单位面积租金（元/月/㎡）"]]

    # 合并数据
    if unit_price_data is None:
        unit_price_data = df_filtered
    else:
        unit_price_data = pd.concat([unit_price_data, df_filtered], ignore_index=True)

# 检查是否有数据可绘图
if unit_price_data is None or unit_price_data.empty:
    print("所有城市的数据在过滤后均无有效记录，无法绘图。")
else:
    # 设置绘图风格
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 适用于macOS和Windows
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    # 创建两个子图：上为GDP柱状图， 下为租金分布
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 16))

    # --------------- 子图1: GDP柱状图 ---------------

    # 准备GDP数据
    cities_order = list(gdp_data.keys())
    gdp_values = [gdp_data[city] for city in cities_order]
    bar_positions = range(len(cities_order))

    # 绘制GDP柱状图
    bars = ax1.bar(
        bar_positions, gdp_values, color=[city_colors[city] for city in cities_order], alpha=0.8, label="人均 GDP（元）"
    )

    # 添加数据标注
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(
            f"{height}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 上移3点
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
            color="black",
        )

    # 设置x轴
    ax1.set_xticks(bar_positions)
    ax1.set_xticklabels(cities_order, fontsize=12)

    ax1.set_xlabel("城市", fontsize=14)
    ax1.set_ylabel("人均 GDP（元）", fontsize=14)
    ax1.set_title("五个城市人均 GDP", fontsize=16, fontweight="bold", pad=20)

    # --------------- 子图2: 单位面积租金分布曲线 ---------------

    # 绘制单位面积租金的概率密度曲线
    for city in cities_order:
        data = unit_price_data[unit_price_data["城市"] == city]["单位面积租金（元/月/㎡）"]
        if data.empty:
            continue
        kde = gaussian_kde(data)
        x_min, x_max = data.min(), data.max()
        x_grid = np.linspace(x_min, x_max, 1000)
        density = kde(x_grid)
        ax2.plot(x_grid, density, label=city, color=city_colors[city], linewidth=3, alpha=0.8)  # 加粗线条并设置透明度

    ax2.set_xlabel("单位面积租金（元/月/㎡）", fontsize=14)
    ax2.set_ylabel("概率密度", fontsize=14)
    ax2.set_title("五个城市单位面积租金分布", fontsize=16, fontweight="bold", pad=20)
    ax2.legend(title="城市", fontsize=10, title_fontsize=12)

    # 调整布局
    plt.tight_layout()

    # 保存图表
    bar_chart_filename = os.path.join(output_dir, "gdp_unit_price_chart.png")
    plt.savefig(bar_chart_filename, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"图表已成功保存到 {bar_chart_filename}")
