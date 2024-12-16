import os

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import colors as mcolors

# 设置Matplotlib参数以支持中文显示
plt.rcParams["font.sans-serif"] = ["STHeiti"]  # 适用于macOS和Windows
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 定义城市列表及对应的文件名
cities = {
    "bj": {
        "csv": "data/bj_region_price_data.csv",
        "geojson": "data/bj.geojson",
        "name": "北京",
    },
    "sh": {
        "csv": "data/sh_region_price_data.csv",
        "geojson": "data/sh.geojson",
        "name": "上海",
    },
    "gz": {
        "csv": "data/gz_region_price_data.csv",
        "geojson": "data/gz.geojson",
        "name": "广州",
    },
    "sz": {
        "csv": "data/sz_region_price_data.csv",
        "geojson": "data/sz.geojson",
        "name": "深圳",
    },
    "changde": {
        "csv": "data/changde_region_price_data.csv",
        "geojson": "data/changde.geojson",
        "name": "常德",
    },
}

# 定义输出地图的目录
map_data_dir = "figure"
os.makedirs(map_data_dir, exist_ok=True)

for city_key, city_info in cities.items():
    csv_file = city_info["csv"]
    geojson_file = city_info["geojson"]
    city_name = city_info["name"]

    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"CSV 文件 {csv_file} 不存在，跳过 {city_name}。")
        continue
    if not os.path.exists(geojson_file):
        print(f"GeoJSON 文件 {geojson_file} 不存在，跳过 {city_name}。")
        continue

    # 读取租金数据
    df = pd.read_csv(csv_file)

    # 读取 GeoJSON 数据
    gdf = gpd.read_file(geojson_file)

    # 确保区域名称匹配
    # 假设 GeoJSON 文件中的区域名称字段为 'name'，根据实际情况调整
    if "name" in gdf.columns:
        gdf = gdf.rename(columns={"name": "区域"})
    elif "NAME_1" in gdf.columns:
        gdf = gdf.rename(columns={"NAME_1": "区域"})
    # 根据实际情况添加更多的重命名规则

    # 预处理区域名称：去除空格并统一大小写（根据需要）
    df["区域"] = df["区域"].str.strip()
    gdf["区域"] = gdf["区域"].str.strip()
    # 如果需要统一大小写，可以取消下一行注释
    # df['区域'] = df['区域'].str.upper()
    # gdf['区域'] = gdf['区域'].str.upper()

    # 合并数据
    merged = gdf.merge(df, on="区域")

    # 检查合并后的数据
    if merged.empty:
        print(f"{city_name} 的 GeoJSON 和 CSV 数据合并后为空，请检查区域名称是否匹配。")
        continue

    # 重新投影为投影坐标系（EPSG:3857）
    merged = merged.to_crs(epsg=3857)

    # 计算区域的中心点，用于标签定位
    merged["centroid"] = merged.geometry.centroid

    # 设置绘图风格
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))  # 增大图像尺寸

    # 定义颜色映射和规范化
    cmap = "OrRd"
    norm = mcolors.Normalize(vmin=merged["平均价格（元/月）"].min(), vmax=merged["平均价格（元/月）"].max())
    colormap = plt.get_cmap(cmap)

    # 绘制地图，按照 '平均价格（元/月）' 着色
    merged.plot(
        column="平均价格（元/月）",
        cmap=cmap,
        linewidth=0.8,
        ax=ax,
        edgecolor="0.8",
        legend=True,
        norm=norm,
        legend_kwds={
            "label": "平均价格（元/月）",
            "orientation": "horizontal",
            "shrink": 0.5,  # 缩小图例大小
            "pad": 0.05,  # 图例与图像的距离
            # 移除 'fontsize' 参数
        },
    )

    # 获取当前颜色图例（colorbar）并调整字体大小
    # 由于 GeoPandas 使用 Matplotlib 的 colorbar，需要通过 Axes 对象获取
    # 获取 colorbar 句柄
    if ax.get_legend() is not None:
        colorbar = ax.get_legend()
        for text in colorbar.texts:
            text.set_fontsize(10)  # 设置图例字体大小

    # 添加区域名称和租金价格标签
    for _, row in merged.iterrows():
        centroid = row["centroid"]
        if pd.notnull(centroid):
            # 获取对应租金的颜色
            rent = row["平均价格（元/月）"]
            rgba_color = colormap(norm(rent))  # RGBA颜色
            # 计算亮度（YIQ颜色空间公式）
            r, g, b, _ = rgba_color
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            # 根据亮度选择黑色或白色
            text_color = "black" if brightness > 0.5 else "white"

            plt.text(
                centroid.x,
                centroid.y,
                f"{row['区域']}\n{row['平均价格（元/月）']:.0f}",
                horizontalalignment="center",
                fontsize=8,
                color=text_color,
                weight="bold",
            )

    # 添加城市名称标题
    ax.set_title(f"{city_name}各区域平均租金分布", fontsize=20)

    # 去除坐标轴
    ax.set_axis_off()

    # 优化布局
    plt.tight_layout()

    # 保存地图
    map_file = os.path.join(map_data_dir, f"{city_key}_region_heat_map.png")
    plt.savefig(map_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"{city_name} 的租金热力图已保存到 {map_file}")
