import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 定义城市缩写到全称的映射
city_full_names = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

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
price_df["城市"] = price_df["城市"].map(city_full_names)
unit_price_df["城市"] = unit_price_df["城市"].map(city_full_names)

# 设置 '城市' 为索引
price_df.set_index("城市", inplace=True)
unit_price_df.set_index("城市", inplace=True)

# 定义需要可视化的统计指标
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

# 确保所选指标存在于数据中
price_metrics = [metric for metric in price_metrics if metric in price_df.columns]
unit_price_metrics = [metric for metric in unit_price_metrics if metric in unit_price_df.columns]

# 转换为长格式，以适应 seaborn 的绘图需求
price_long = (
    price_df[price_metrics]
    .reset_index()
    .melt(id_vars="城市", value_vars=price_metrics, var_name="统计指标", value_name="金额（元/月）")
)

unit_price_long = (
    unit_price_df[unit_price_metrics]
    .reset_index()
    .melt(id_vars="城市", value_vars=unit_price_metrics, var_name="统计指标", value_name="金额（元/㎡）")
)

# 设置绘图风格
sns.set_theme(style="whitegrid")

# 设置中文字体以确保中文显示正确
plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 根据需要更换字体
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 定义颜色调色板，使用相同且不太浅的 Set1 调色板
common_palette = sns.color_palette("Set3", n_colors=max(len(price_metrics), len(unit_price_metrics)))

# 创建输出目录（如果不存在）
output_dir = "figure"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- 绘制租金统计柱状图（向上） ---
plt.figure(figsize=(20, 12))
sns.barplot(data=price_long, x="城市", y="金额（元/月）", hue="统计指标", palette=common_palette)

# 添加数据标签，去除小数，仅显示整数，并防止重叠
for p in plt.gca().patches:
    height = p.get_height()
    if height > 0:
        label = f"{height:.2f}" if height < 1 else f"{int(height)}"
        plt.gca().annotate(
            label,
            (p.get_x() + p.get_width() / 2.0, height),
            ha="center",
            va="bottom",
            fontsize=10,
            color="black",
            xytext=(0, 3),  # 稍微上移
            textcoords="offset points",
        )

# 设置标题和标签
plt.title("五个城市租金统计信息对比", fontsize=20, fontweight="bold", pad=20)
plt.xlabel("城市", fontsize=14)
plt.ylabel("金额（元/月）", fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
# 将图例放置在图表内部的右上角
plt.legend(title="统计指标", fontsize=12, title_fontsize=14, loc="upper right", bbox_to_anchor=(1, 1))

# 保存图表
price_output_filename = os.path.join(output_dir, "price_bar_chart.png")
plt.tight_layout()
plt.savefig(price_output_filename, dpi=300, bbox_inches="tight")

print(f"租金统计图已成功保存到 {price_output_filename}")

# --- 绘制单位面积租金统计柱状图（向上） ---
plt.figure(figsize=(20, 12))
sns.barplot(data=unit_price_long, x="城市", y="金额（元/㎡）", hue="统计指标", palette=common_palette)

# 添加数据标签，去除小数，仅显示整数，并防止重叠
for p in plt.gca().patches:
    height = p.get_height()
    if height > 0:
        plt.gca().annotate(
            f"{int(height)}",
            (p.get_x() + p.get_width() / 2.0, height),
            ha="center",
            va="bottom",
            fontsize=10,
            color="black",
            xytext=(0, 3),  # 稍微上移
            textcoords="offset points",
        )

# 设置标题和标签
plt.title("五个城市单位面积租金统计信息对比", fontsize=20, fontweight="bold", pad=20)
plt.xlabel("城市", fontsize=14)
plt.ylabel("金额（元/㎡）", fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
# 将图例放置在图表内部的右上角
plt.legend(title="统计指标", fontsize=12, title_fontsize=14, loc="upper left", bbox_to_anchor=(0, 1))

# 保存图表
unit_price_output_filename = os.path.join(output_dir, "unit_price_bar_chart.png")
plt.tight_layout()
plt.savefig(unit_price_output_filename, dpi=300, bbox_inches="tight")

print(f"单位面积租金统计图已成功保存到 {unit_price_output_filename}")
