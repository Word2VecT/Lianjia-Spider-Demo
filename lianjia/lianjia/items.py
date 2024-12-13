# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewHouseItem(scrapy.Item):
    # 新房字段
    name = scrapy.Field()  # 楼盘名称
    type = scrapy.Field()  # 楼盘类型
    location = scrapy.Field()  # 所在地点
    room = scrapy.Field()  # 房型
    area = scrapy.Field()  # 面积
    unit_price = scrapy.Field()  # 单价
    total_price = scrapy.Field()  # 总价


class SecondHandHouseItem(scrapy.Item):
    # 二手房字段
    title = scrapy.Field()  # 小区名称
    position_info = scrapy.Field()  # 地点
    house_info = scrapy.Field()  # 房型等信息
    unit_price = scrapy.Field()  # 单价
    total_price = scrapy.Field()  # 总价


class RentHouseItem(scrapy.Item):
    # 租房字段
    title = scrapy.Field()  # 标题
    des = scrapy.Field()  # 描述信息
    bottom = scrapy.Field()  # 底部信息
    brand = scrapy.Field()  # 品牌
    price = scrapy.Field()  # 价格
