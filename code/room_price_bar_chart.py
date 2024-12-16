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

# 定义房屋类型的中英文映射
room_type_mapping = {
    "一居": "room_1",
    "二居": "room_2",
    "三居": "room_3",
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
        "25%分位数（元/月）",
        "75%分位数（元/月）",
        "中位数（元/月）",
        "标准差（元/月）",
        "最高价（元/月）",
        "最低价（元/月）",
    ]

    missing_columns = [col for col in required_columns if col not in df_city.columns]
    if missing_columns:
        print(f"文件 {filename} 缺少列：{missing_columns}，跳过 {city_full_names.get(city_code, city_code)} 城市。")
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

# 定义房屋类型列表
room_types = ["一居", "二居", "三居"]

# 创建输出目录（如果不存在）
output_dir = "figure"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 设置绘图风格
sns.set_theme(style="whitegrid")

# 定义统计指标
metrics = [
    "均价（元/月）",
    "中位数（元/月）",
    "25%分位数（元/月）",
    "75%分位数（元/月）",
    "标准差（元/月）",
    "最高价（元/月）",
    "最低价（元/月）",
]

# 定义颜色调色板
common_palette = sns.color_palette("Set3", n_colors=len(metrics))

# 生成三张柱状图，分别为一居、二居、三居
for room_type in room_types:
    # 筛选当前房屋类型的数据
    df_room = df_all[df_all["房屋类型"] == room_type]

    if df_room.empty:
        print(f"房屋类型 {room_type} 没有数据，跳过。")
        continue

    # 将数据转换为长格式，以适应 seaborn 的绘图需求
    df_melt = df_room.melt(id_vars=["城市"], value_vars=metrics, var_name="统计指标", value_name="数值")

    # 创建柱状图
    plt.figure(figsize=(16, 10))
    plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 根据需要更换字体
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
    sns.barplot(data=df_melt, x="城市", y="数值", hue="统计指标", palette=common_palette)

    # 添加数据标签，去除小数，仅显示整数
    for p in plt.gca().patches:
        plt.gca().annotate(
            f"{int(p.get_height())}",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="center",
            fontsize=10,
            color="black",
            xytext=(0, 5),
            textcoords="offset points",
        )

    # 设置标题和标签
    plt.title(f"五个城市{room_type}租金统计信息对比", fontsize=18, fontweight="bold", pad=20)
    plt.xlabel("城市", fontsize=14)
    plt.ylabel("金额（元/月）", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # 将图例放置在图表内部的右上角
    plt.legend(title="统计指标", fontsize=10, title_fontsize=12, loc="upper right", bbox_to_anchor=(1, 1))

    # 获取英文文件名
    room_type = room_type_mapping.get(room_type, "unknown_room")
    output_filename = os.path.join(output_dir, f"{room_type}_price_bar_chart.png")
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")

    print(f"{room_type} rent comparison chart has been successfully saved to {output_filename}")
