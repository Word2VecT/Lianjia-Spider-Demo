import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 定义城市缩写到全称的映射
city_full_names = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 定义城市列表及对应的文件名
cities = {
    "bj": "data/bj_room_price_data.csv",
    "sh": "data/sh_room_price_data.csv",
    "gz": "data/gz_room_price_data.csv",
    "sz": "data/sz_room_price_data.csv",
    "changde": "data/changde_room_price_data.csv",
}

# 初始化一个列表用于存储所有城市的数据
all_data = []

# 遍历每个城市的 CSV 文件并读取数据
for city_code, filename in cities.items():
    if not os.path.exists(filename):
        print(f"文件 {filename} 不存在，跳过 {city_full_names.get(city_code, city_code)} 城市。")
        continue

    try:
        df_city = pd.read_csv(filename, encoding="utf-8-sig")
    except Exception as e:
        print(f"读取文件 {filename} 失败，错误：{e}")
        continue

    # 添加城市名称
    df_city["城市"] = city_full_names.get(city_code, city_code)

    # 选择需要的列并确保房屋类型存在
    required_columns = [
        "房屋类型",
        "均价（元/月）",
        "标准差（元/月）",
        "最低价（元/月）",
        "中位数（元/月）",
        "25%分位数（元/月）",
        "75%分位数（元/月）",
    ]

    if not all(col in df_city.columns for col in required_columns):
        print(f"文件 {filename} 缺少必要列，跳过 {city_full_names.get(city_code, city_code)} 城市。")
        continue

    # 选择需要的列
    df_city = df_city[required_columns + ["城市"]]

    all_data.append(df_city)

# 检查是否有有效的数据
if not all_data:
    print("没有有效的租金数据可供处理。")
    exit(1)

# 合并所有城市的数据
df_all = pd.concat(all_data, ignore_index=True)

# 创建输出目录（如果不存在）
output_dir = "figure"
os.makedirs(output_dir, exist_ok=True)

# 设置绘图风格
sns.set_theme(style="whitegrid")

# 定义统计指标
metrics = [
    "均价（元/月）",
    "标准差（元/月）",
    "最低价（元/月）",
    "中位数（元/月）",
    "25%分位数（元/月）",
    "75%分位数（元/月）",
]

# 定义颜色调色板
common_palette = sns.color_palette("Set2", n_colors=len(metrics))

# 生成每个城市的折线图
for city_code, city_full_name in city_full_names.items():
    df_city = df_all[df_all["城市"] == city_full_name]

    if df_city.empty:
        print(f"城市 {city_full_name} 没有数据，跳过。")
        continue

    df_melt = df_city.melt(id_vars=["房屋类型"], value_vars=metrics, var_name="统计指标", value_name="数值")

    plt.figure(figsize=(16, 10))
    plt.rcParams["font.sans-serif"] = ["STHeiti"]
    plt.rcParams["axes.unicode_minus"] = False

    sns.lineplot(data=df_melt, x="房屋类型", y="数值", hue="统计指标", marker="o", palette=common_palette)

    for line in plt.gca().lines:
        for x, y in zip(line.get_xdata(), line.get_ydata(), strict=False):
            if pd.isna(y):
                continue
            label = f"{y:.2f}" if isinstance(y, float) and y < 1000 else f"{int(y)}"
            plt.text(x, y, label, ha="center", va="bottom" if y >= 0 else "top", fontsize=8, color="black")

    plt.title(f"{city_full_name}房屋类型租金统计信息对比", fontsize=18, fontweight="bold", pad=20)
    plt.xlabel("房屋类型", fontsize=14)
    plt.ylabel("金额（元/月）", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(title="统计指标", fontsize=10, title_fontsize=12, loc="upper right", bbox_to_anchor=(1, 1))

    output_filename = os.path.join(output_dir, f"{city_code}_room_price_line_chart.png")
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")

    print(f"{city_code} 的租金统计图已成功保存到 {output_filename}")
