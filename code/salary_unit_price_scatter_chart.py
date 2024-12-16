import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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

# 定义平均工资（单位：元）
salary_data = {"北京": 18193, "上海": 19111, "广州": 12873, "深圳": 14321, "常德": 7333}

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
    # 计算每个城市的单位面积租金平均值
    mean_rent = unit_price_data.groupby("城市")["单位面积租金（元/月/㎡）"].mean().reset_index()

    # 映射平均工资
    mean_rent["平均工资（元）"] = mean_rent["城市"].map(salary_data)

    # 计算性价比指数（CPI）：平均工资 / 单位面积租金
    mean_rent["性价比指数 (CPI)"] = mean_rent["平均工资（元）"] / mean_rent["单位面积租金（元/月/㎡）"]

    # 排序（可选）
    mean_rent_sorted = mean_rent.sort_values(by="性价比指数 (CPI)", ascending=False)

    # 设置绘图风格
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 适用于macOS和Windows
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    # 创建气泡图
    plt.figure(figsize=(14, 10))
    scatter = sns.scatterplot(
        data=mean_rent_sorted,
        x="单位面积租金（元/月/㎡）",  # 反转 X 轴为租金
        y="平均工资（元）",  # 纵轴为平均工资
        size="性价比指数 (CPI)",
        hue="城市",
        palette=city_colors,  # 使用字典形式的 palette
        alpha=0.7,
        edgecolor="w",
        sizes=(500, 1500),  # 增大气泡大小
        legend="brief",  # 只显示城市颜色的图例
    )

    # 添加虚线从原点到气泡
    for _, row in mean_rent_sorted.iterrows():
        plt.plot(
            [0, row["单位面积租金（元/月/㎡）"]],
            [0, row["平均工资（元）"]],
            linestyle="--",
            color=city_colors[row["城市"]],
            linewidth=1,
            alpha=0.5,
        )

    # 添加 CPI 标注在气泡旁边，并标注城市名称
    for _, row in mean_rent_sorted.iterrows():
        plt.text(
            row["单位面积租金（元/月/㎡）"] + (mean_rent_sorted["单位面积租金（元/月/㎡）"].max() * 0.01),
            row["平均工资（元）"],
            f"CPI: {row['性价比指数 (CPI)']:.1f}",
            color="black",
            ha="left",
            va="center",
            fontsize=10,
            bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", boxstyle="round,pad=0.2"),
        )

        plt.text(
            row["单位面积租金（元/月/㎡）"] - (mean_rent_sorted["单位面积租金（元/月/㎡）"].max() * 0.04),
            row["平均工资（元）"],
            f"{row['城市']}",
            color="black",
            ha="left",
            va="center",
            fontsize=10,
            bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", boxstyle="round,pad=0.2"),
        )

    # 设置标题和标签
    plt.xlabel("单位面积租金（元/月/㎡）", fontsize=14)
    plt.ylabel("平均工资（元）", fontsize=14)
    plt.title("五个城市单位面积租金与平均工资的关系及租房性价比 (CPI)", fontsize=16, fontweight="bold", pad=20)

    # 移除图例中的 CPI
    handles, labels = scatter.get_legend_handles_labels()
    # 只保留城市的图例，不包括 size (CPI)
    new_handles = handles[: len(cities)]
    new_labels = labels[: len(cities)]
    plt.legend(new_handles, new_labels, title="城市", bbox_to_anchor=(1.05, 1), loc="upper left")

    # 确保 (0,0) 在左下角
    plt.xlim(left=0)
    plt.ylim(bottom=0)

    # 添加注释说明
    plt.text(
        0.95,
        0.05,
        "CPI = 平均工资 / 单位面积租金",
        horizontalalignment="right",
        verticalalignment="bottom",
        transform=plt.gca().transAxes,
        fontsize=12,
        bbox=dict(facecolor="white", alpha=0.5),
    )

    # 优化布局
    plt.tight_layout()

    # 保存图表
    scatter_chart_filename = os.path.join(output_dir, "salary_unit_price_scatter_chart.png")
    plt.savefig(scatter_chart_filename, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"气泡图已成功保存到 {scatter_chart_filename}")
