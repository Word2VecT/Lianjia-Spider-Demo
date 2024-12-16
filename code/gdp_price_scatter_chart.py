import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 定义城市缩写与全称的映射
city_full_names = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 定义人均 GDP（单位：元）
gdp_data = {"北京": 200278, "上海": 190321, "广州": 161634, "深圳": 195231, "常德": 84342}

# 读取价格数据
price_data_file = "data/price_data.csv"
if not os.path.exists(price_data_file):
    print(f"文件 {price_data_file} 不存在。")
    exit()

try:
    price_df = pd.read_csv(price_data_file, encoding="utf-8-sig")
except Exception as e:
    print(f"读取文件 {price_data_file} 失败，错误：{e}")
    exit()

if price_df.empty:
    print("价格数据文件为空，无法绘图。")
    exit()

# 映射城市缩写到全称
price_df["城市全称"] = price_df["城市"].map(city_full_names)

# 检查是否有未映射的城市
if price_df["城市全称"].isnull().any():
    missing_cities = price_df[price_df["城市全称"].isnull()]["城市"].unique()
    print(f"未找到以下城市的全称映射: {missing_cities}")
    exit()

# 提取必要的列并重命名
price_df = price_df[["城市全称", "均价（元/月）"]].rename(columns={"城市全称": "城市"})

# 计算 CPI
price_df["人均 GDP（元）"] = price_df["城市"].map(gdp_data)

# 检查是否有 NaN 的人均 GDP
if price_df["人均 GDP（元）"].isnull().any():
    missing_gdp_cities = price_df[price_df["人均 GDP（元）"].isnull()]["城市"].unique()
    print(f"未找到以下城市的人均 GDP 数据: {missing_gdp_cities}")
    exit()

price_df["CPI"] = price_df["人均 GDP（元）"] / price_df["均价（元/月）"]

# 检查 CPI 是否有无穷大或 NaN
if price_df["CPI"].replace([float("inf"), -float("inf")], pd.NA).dropna().shape[0] != price_df.shape[0]:
    print("CPI 计算结果包含无穷大或 NaN，请检查数据。")
    exit()

# 排序 CPI 从大到小
price_df_sorted = price_df.sort_values(by="CPI", ascending=False).reset_index(drop=True)

# 定义颜色列表（选择美观的调色板）
colors = sns.color_palette("Set2", n_colors=len(price_df_sorted))
city_colors = {city: colors[idx] for idx, city in enumerate(price_df_sorted["城市"])}

# 创建输出目录（如果不存在）
output_dir = "figure"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 设置绘图风格
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 适用于macOS和Windows
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 创建气泡图
plt.figure(figsize=(14, 10))
scatter = sns.scatterplot(
    data=price_df_sorted,
    x="均价（元/月）",
    y="人均 GDP（元）",
    size="CPI",
    hue="城市",
    palette=colors,
    alpha=0.7,
    edgecolor="w",
    sizes=(500, 1500),  # 增大气泡大小
    legend="brief",  # 只显示城市颜色的图例
)

# 添加虚线从原点到气泡
for _, row in price_df_sorted.iterrows():
    plt.plot(
        [0, row["均价（元/月）"]],
        [0, row["人均 GDP（元）"]],
        linestyle="--",
        color=city_colors[row["城市"]],
        linewidth=1,
        alpha=0.5,
    )

# 添加 CPI 标注在气泡旁边，并标注城市名称
for _, row in price_df_sorted.iterrows():
    plt.text(
        row["均价（元/月）"] + (price_df_sorted["均价（元/月）"].max() * 0.01),
        row["人均 GDP（元）"],
        f"CPI: {row['CPI']:.1f}",
        color="black",
        ha="left",
        va="center",
        fontsize=10,
        bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", boxstyle="round,pad=0.2"),
    )

    plt.text(
        row["均价（元/月）"] - (price_df_sorted["均价（元/月）"].max() * 0.04),
        row["人均 GDP（元）"],
        f"{row['城市']}",
        color="black",
        ha="left",
        va="center",
        fontsize=10,
        bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", boxstyle="round,pad=0.2"),
    )

# 设置标题和标签
plt.xlabel("均价（元/月）", fontsize=14)
plt.ylabel("人均 GDP（元）", fontsize=14)
plt.title("五个城市均价与人均 GDP 的关系及租房性价比 (CPI)", fontsize=16, fontweight="bold", pad=20)

# 移除图例中的 CPI
handles, labels = scatter.get_legend_handles_labels()
# 只保留城市的图例，不包括 size (CPI)
new_handles = handles[: len(price_df_sorted)]
new_labels = labels[: len(price_df_sorted)]
plt.legend(new_handles, new_labels, title="城市", bbox_to_anchor=(1.05, 1), loc="upper left")

# 确保 (0,0) 在左下角
plt.xlim(left=0)
plt.ylim(bottom=0)

# 添加注释说明
plt.text(
    0.95,
    0.05,
    "CPI = 人均 GDP / 均价",
    horizontalalignment="right",
    verticalalignment="bottom",
    transform=plt.gca().transAxes,
    fontsize=12,
    bbox=dict(facecolor="white", alpha=0.5),
)

# 优化布局
plt.tight_layout()

# 保存图表
scatter_chart_filename = os.path.join(output_dir, "gdp_price_scatter_chart.png")
plt.savefig(scatter_chart_filename, dpi=300, bbox_inches="tight")
plt.close()

print(f"根据 CPI 从大到小排序后的气泡图已成功保存到 {scatter_chart_filename}")
