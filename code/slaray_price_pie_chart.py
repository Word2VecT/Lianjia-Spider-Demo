import os

import matplotlib.pyplot as plt
import pandas as pd

# 定义城市缩写与全称的映射
city_full_names = {"bj": "北京", "sh": "上海", "gz": "广州", "sz": "深圳", "changde": "常德"}

# 定义平均工资（单位：元）
salary_data = {"北京": 18193, "上海": 19111, "广州": 12873, "深圳": 14321, "常德": 7333}

# 创建输出目录（如果不存在）
output_dir = "figure"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 读取租金数据
price_data_file = "data/price_data.csv"

if not os.path.exists(price_data_file):
    print(f"文件 {price_data_file} 不存在，请确保文件路径正确。")
else:
    try:
        df = pd.read_csv(price_data_file, encoding="utf-8-sig")
    except Exception as e:
        print(f"读取文件 {price_data_file} 失败，错误：{e}")
        df = pd.DataFrame()

    if df.empty:
        print("租金数据为空，无法绘图。")
    else:
        # 过滤必要的列并映射城市名称
        df = df[["城市", "均价（元/月）"]].copy()
        df["城市"] = df["城市"].map(city_full_names)

        # 添加平均工资数据
        df["平均工资（元）"] = df["城市"].map(salary_data)

        # 计算性价比指数（CPI）：租金 / 平均工资
        df["占比"] = df["均价（元/月）"] / df["平均工资（元）"]

        # 创建饼图和柱状图
        num_cities = df.shape[0]
        cols = 3  # 每行最多3个子图
        rows = 2  # 两行：第一行3个饼图，第二行2个饼图 + 1柱状图

        fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 6))
        plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 适用于macOS和Windows
        plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

        # 设置颜色列表（选择美观的调色板）
        colors = plt.cm.Set2.colors  # 使用 Set2 调色板
        city_colors = {city: colors[idx % len(colors)] for idx, city in enumerate(df["城市"].unique())}

        # 绘制饼图
        for idx, row in df.iterrows():
            row_idx = idx // cols
            col_idx = idx % cols
            ax = axes[row_idx, col_idx]

            labels = ["租金", "剩余工资"]
            sizes = [row["均价（元/月）"], row["平均工资（元）"] - row["均价（元/月）"]]
            pie_colors = [city_colors[row["城市"]], "#d3d3d3"]  # 租金用城市颜色，剩余工资用灰色
            explode = (0.05, 0)  # 突出显示租金部分

            wedges, texts, autotexts = ax.pie(
                sizes,
                explode=explode,
                labels=labels,
                colors=pie_colors,
                autopct="%1.1f%%",
                startangle=140,
                textprops={"fontsize": 10},
            )

            # 确保饼图是圆形
            ax.axis("equal")

            # 添加标题
            ax.set_title(f"{row['城市']}\n租金占工资比例", fontsize=12, fontweight="bold")

        # 移除多余的饼图子图（如果有）
        for j in range(num_cities, rows * cols - 1):  # Reserve last subplot for bar chart
            fig.delaxes(axes.flatten()[j])

        # ------------------- 绘制柱状图 -------------------
        # 计算 CPI 排序
        df_sorted = df.sort_values(by="占比", ascending=False)

        ax_bar = axes[1, 2]  # 将柱状图放在第二行的最后一个子图
        bar_colors = [city_colors[city] for city in df_sorted["城市"]]

        bars = ax_bar.bar(df_sorted["城市"], df_sorted["占比"], color=bar_colors, alpha=0.8)

        # 添加数据标注
        for bar, cpi in zip(bars, df_sorted["占比"], strict=False):
            height = bar.get_height()
            ax_bar.annotate(
                f"{cpi:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 上移3点
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                color="black",
            )

        # 设置标题和标签
        ax_bar.set_xlabel("城市", fontsize=12)
        ax_bar.set_ylabel("占比", fontsize=12)
        ax_bar.set_title("五个城市租金占平均工资比例", fontsize=14, fontweight="bold")

        # 添加注释说明
        fig.text(0.5, 0.02, "占比 = 租金 / 平均工资", ha="center", fontsize=12, bbox=dict(facecolor="white", alpha=0.5))

        # 调整子图之间的间距
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        # 保存图表
        pie_bar_chart_filename = os.path.join(output_dir, "salary_price_pie_chart.png")
        plt.savefig(pie_bar_chart_filename, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"租金占工资比例的饼图和 CPI 柱状图已成功保存到 {pie_bar_chart_filename}")
