import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 定义城市缩写到全称的映射
city_full_names = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 定义城市列表及对应的 CSV 文件名
cities = {
    "bj": "data/bj_direction_unit_price_data.csv",
    "sh": "data/sh_direction_unit_price_data.csv",
    "gz": "data/gz_direction_unit_price_data.csv",
    "sz": "data/sz_direction_unit_price_data.csv",
    "changde": "data/changde_direction_unit_price_data.csv",
}

# 创建输出目录（如果不存在）
output_dir = "figure"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 设置绘图风格
sns.set_theme(style="whitegrid")

# 定义有效的朝向和对应的颜色
valid_directions = ["东", "南", "西", "北", "南北"]
# 选择一个高对比度的调色板，例如 "Set2" 或 "Dark2"
palette = sns.color_palette("Dark2", n_colors=len(valid_directions))  # 不包括“其他”类别

# 创建一个颜色映射字典
# 注意：'strict' 参数在 Python 3.10+ 中有效。如果使用较早版本的 Python，请移除 'strict=False'
try:
    direction_colors = {direction: color for direction, color in zip(valid_directions, palette, strict=False)}
except TypeError:
    # 如果 Python 版本不支持 'strict' 参数
    direction_colors = {direction: color for direction, color in zip(valid_directions, palette, strict=False)}


# 定义阈值计算方法：平均值加2标准差
def calculate_threshold(df, column, multiplier=2):
    mean = df[column].mean()
    std = df[column].std()
    threshold = mean + multiplier * std
    return threshold


# 遍历每个城市的 CSV 文件并绘制概率分布曲线
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
    if "朝向" not in df.columns or "单位面积租金（元/月/㎡）" not in df.columns:
        print(f"文件 {csv_path} 缺少必要的列，跳过 {city_name} 城市。")
        continue

    # 删除缺失值
    df = df.dropna(subset=["朝向", "单位面积租金（元/月/㎡）"])

    if df.empty:
        print(f"{city_name} 城市没有有效的数据。")
        continue

    # 筛选有效朝向
    df_valid = df[df["朝向"].isin(valid_directions)]

    if df_valid.empty:
        print(f"{city_name} 城市没有有效的朝向数据。")
        continue

    # 计算单位面积租金的阈值（平均值 + 2 * 标准差）
    threshold = calculate_threshold(df_valid, "单位面积租金（元/月/㎡）", multiplier=2)

    # 计算被排除的数据数量和比例
    total_records = len(df)
    excluded_records = len(df[df["单位面积租金（元/月/㎡）"] > threshold])
    excluded_percentage = (excluded_records / total_records) * 100

    # 仅保留不超过阈值的数据
    df_filtered = df_valid[df_valid["单位面积租金（元/月/㎡）"] <= threshold]

    if df_filtered.empty:
        print(f"{city_name} 城市没有低于阈值的数据，跳过绘图。")
        continue

    # 设置图形大小
    plt.figure(figsize=(14, 10))

    # 设置中文字体和解决负号显示问题
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 黑体，适用于大多数中文系统
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    # 绘制分布曲线
    for direction in valid_directions:
        direction_data = df_filtered[df_filtered["朝向"] == direction]["单位面积租金（元/月/㎡）"]
        if direction_data.empty:
            continue
        sns.kdeplot(
            direction_data,
            label=direction,
            color=direction_colors.get(direction, "gray"),
            linewidth=4,  # 增加线条宽度
            linestyle="-",  # 使用实线
            alpha=0.6,  # 设置线条半透明
        )

    # 设置标题和标签
    plt.title(f"{city_name}各朝向单位面积租金分布", fontsize=20, fontweight="bold")
    plt.xlabel("单位面积租金（元/月/㎡）", fontsize=16)
    plt.ylabel("概率密度", fontsize=16)

    # 设置图例，放置在图表外部
    plt.legend(title="朝向", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=12, title_fontsize=14)

    # 添加注释说明被排除的数据
    plt.text(
        0.95,
        0.95,
        f"已排除单位面积租金超过平均值+2标准差的数据\n共排除 {excluded_records} 条记录，占比 {excluded_percentage:.2f}%",
        horizontalalignment="right",
        verticalalignment="bottom",
        transform=plt.gca().transAxes,
        fontsize=12,
        bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"),
    )

    # 调整布局以防止标签被截断
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # 为图例留出空间

    # 保存图表，文件名使用英文首字母缩写
    output_filename = os.path.join(output_dir, f"{city_code}_direction_unit_price_distribution.png")
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"{city_name} 城市的单位面积租金分布图已成功保存到 {output_filename}")
