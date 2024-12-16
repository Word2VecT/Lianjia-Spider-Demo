import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 定义城市缩写与全称的映射
city_mapping = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 定义每个城市对应的 CSV 文件路径
cities = {
    "bj": "data/bj_direction_unit_price_data.csv",
    "sh": "data/sh_direction_unit_price_data.csv",
    "gz": "data/gz_direction_unit_price_data.csv",
    "sz": "data/sz_direction_unit_price_data.csv",
    "changde": "data/changde_direction_unit_price_data.csv",
}

# 定义有效的朝向
valid_directions = ["东", "南", "西", "北", "南北"]

# 定义颜色列表（选择美观的调色板）
colors = sns.color_palette("Set3", n_colors=len(valid_directions))

# 创建输出目录（如果不存在）
output_dir = "figure"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 初始化一个空的 DataFrame 来存储各城市的单位面积租金平均值
average_unit_price = pd.DataFrame(columns=valid_directions, index=city_mapping.values())

# 遍历每个城市的 CSV 文件，计算每个朝向的单位面积租金平均值
for city_code, csv_path in cities.items():
    city_name = city_mapping.get(city_code, city_code)

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
    required_columns = ["朝向", "单位面积租金（元/月/㎡）"]
    if not all(col in df.columns for col in required_columns):
        print(f"文件 {csv_path} 缺少必要的列 {required_columns}，跳过 {city_name} 城市。")
        continue

    # 删除缺失值
    df = df.dropna(subset=required_columns)

    if df.empty:
        print(f"{city_name} 城市的数据为空，跳过。")
        continue

    # 筛选有效朝向
    df_valid = df[df["朝向"].isin(valid_directions)]

    if df_valid.empty:
        print(f"{city_name} 城市没有有效的朝向数据，跳过。")
        continue

    # 计算每个朝向的平均单位面积租金
    mean_prices = df_valid.groupby("朝向")["单位面积租金（元/月/㎡）"].mean()

    # 将计算结果添加到 DataFrame
    for direction in valid_directions:
        average_unit_price.at[city_name, direction] = mean_prices.get(direction, 0)

# 填充缺失值并显式转换数据类型
pd.set_option("future.no_silent_downcasting", True)
average_unit_price = average_unit_price.fillna(0).astype(float)

# 转换为长格式，适合绘制分组柱状图
df_long = average_unit_price.reset_index().melt(
    id_vars="index", value_vars=valid_directions, var_name="朝向", value_name="平均单位面积租金（元/月/㎡）"
)
df_long.rename(columns={"index": "城市"}, inplace=True)

# 设置绘图风格
sns.set_theme(style="whitegrid")

# 设置图形大小
plt.figure(figsize=(12, 8))
plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 适用于macOS和Windows
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 绘制分组柱状图
bar_plot = sns.barplot(data=df_long, x="城市", y="平均单位面积租金（元/月/㎡）", hue="朝向", palette=colors)

# 添加数据标签
for bar in bar_plot.patches:
    value = bar.get_height()
    if value > 0:  # 只显示正值
        bar_plot.annotate(
            f"{value:.1f}",
            (bar.get_x() + bar.get_width() / 2, value),
            ha="center",
            va="bottom",
            fontsize=10,
            color="black",
            xytext=(0, 5),  # 上移一点
            textcoords="offset points",
        )

# 设置标题和标签
plt.title("五个城市各朝向单位面积租金平均值对比", fontsize=16, fontweight="bold", pad=20)
plt.xlabel("城市", fontsize=14)
plt.ylabel("平均单位面积租金（元/月/㎡）", fontsize=14)

# 设置刻度标签字体大小
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# 调整图例位置到图像内部
plt.legend(title="朝向", title_fontsize=12, fontsize=10, loc="upper right", bbox_to_anchor=(0.95, 0.95))

# 调整布局以防止标签被截断
plt.tight_layout()

# 保存图表
output_filename = os.path.join(output_dir, "direction_unit_price_bar_chart.png")
plt.savefig(output_filename, dpi=300, bbox_inches="tight")
plt.close()

print(f"柱状图已成功保存到 {output_filename}")
