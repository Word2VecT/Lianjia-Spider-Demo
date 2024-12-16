import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import zscore

# 设置中文字体以确保中文显示正确
plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 适用于macOS和Windows
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 定义城市缩写与全称的映射
city_mapping = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 定义输入文件路径
price_stats_filepath = "data/price_data.csv"
unit_price_stats_filepath = "data/unit_price_data.csv"

# 检查文件是否存在
if not os.path.exists(price_stats_filepath):
    print(f"文件 {price_stats_filepath} 不存在，请检查路径是否正确。")
    exit(1)

if not os.path.exists(unit_price_stats_filepath):
    print(f"文件 {unit_price_stats_filepath} 不存在，请检查路径是否正确。")
    exit(1)

# 读取 CSV 文件
price_df = pd.read_csv(price_stats_filepath)
unit_price_df = pd.read_csv(unit_price_stats_filepath)

# 将城市缩写替换为全称
price_df["城市"] = price_df["城市"].map(city_mapping)
unit_price_df["城市"] = unit_price_df["城市"].map(city_mapping)

# 设置 '城市' 为索引
price_df.set_index("城市", inplace=True)
unit_price_df.set_index("城市", inplace=True)


# 定义雷达图绘制函数
def plot_radar_chart(df, metrics, title, filename, colors):
    """
    绘制雷达图并保存，包含具体数据标签。

    参数：
    - df: DataFrame，包含城市为索引和需要绘制的指标列。
    - metrics: List[str]，需要绘制的指标名称。
    - title: str，图表标题。
    - filename: str，保存的文件路径。
    - colors: List[str]，城市对应的颜色列表。
    """
    # 数据标准化（Z-score）
    normalized_data = df[metrics].apply(zscore)

    # 获取指标名称
    categories = list(metrics)
    N = len(categories)

    # 计算角度
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # 完成环形

    # 初始化图形
    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, polar=True)

    # 设置起始角度和方向
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # 设置类别标签
    plt.xticks(angles[:-1], categories, color="grey", size=12)

    # 设置 y 轴刻度
    ax.set_rlabel_position(0)
    plt.yticks([-2, -1, 0, 1, 2], ["-2", "-1", "0", "1", "2"], color="grey", size=10)
    plt.ylim(-2, 2)

    # 绘制每个城市的数据
    for idx, (city, row) in enumerate(normalized_data.iterrows()):
        values = row.tolist()
        values += values[:1]  # 完成环形
        ax.plot(angles, values, linewidth=2, linestyle="solid", label=city, color=colors[idx % len(colors)])
        ax.fill(angles, values, alpha=0.25, color=colors[idx % len(colors)])

    # 添加图例
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=12)

    # 添加标题
    plt.title(title, size=20, y=1.1, fontweight="bold")

    # 保存图表
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"雷达图已成功保存到 {filename}")


# 定义需要绘制的指标
price_metrics = [
    "均价（元/月）",
    "中位数（元/月）",
    "25%分位数（元/月）",
    "75%分位数（元/月）",
    "标准差（元/月）",
    "最高价（元/月）",
    "最低价（元/月）",
]

unit_price_metrics = [
    "均价（元/㎡）",
    "中位数（元/㎡）",
    "25%分位数（元/㎡）",
    "75%分位数（元/㎡）",
    "标准差（元/㎡）",
    "最高价（元/㎡）",
    "最低价（元/㎡）",
]

# 定义颜色列表（为每个城市分配不同颜色）
colors = ["b", "g", "r", "c", "m"]  # 可以根据需要扩展

# 确保目标目录存在
output_dir = "figure"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 绘制租金统计雷达图
plot_radar_chart(
    df=price_df,
    metrics=price_metrics,
    title="五个城市租金统计信息雷达图对比",
    filename=os.path.join(output_dir, "price_radar_chart.png"),
    colors=colors,
)

# 绘制单位面积租金统计雷达图
plot_radar_chart(
    df=unit_price_df,
    metrics=unit_price_metrics,
    title="五个城市单位面积租金统计信息雷达图对比",
    filename=os.path.join(output_dir, "unit_price_radar_chart.png"),
    colors=colors,
)
