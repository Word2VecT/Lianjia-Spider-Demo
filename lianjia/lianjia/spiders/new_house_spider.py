import scrapy

from lianjia.items import NewHouseItem  # 导入 NewHouseItem


class NewHouseSpider(scrapy.Spider):
    name = "new_house"
    allowed_domains = ["lianjia.com"]
    start_page = 3
    start_urls = [f"https://bj.fang.lianjia.com/loupan/pg{start_page}/"]
    end_page = 10

    custom_settings = {
        "FEEDS": {
            "new_house_data.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            },
        },
    }

    def parse(self, response):
        # 选择所有楼盘信息的父容器
        for house in response.xpath('//div[@class="resblock-desc-wrapper"]'):
            item = NewHouseItem()  # 创建一个 NewHouseItem 实例
            item["name"] = house.xpath('.//div[@class="resblock-name"]/h2/a/text()').get()
            item["type"] = house.xpath('.//span[@class="resblock-type"]/text()').get()

            # 提取 location 信息
            location_parts = house.xpath('.//div[@class="resblock-location"]/span/text()').getall()
            location_extra = house.xpath('.//div[@class="resblock-location"]/a/text()').get()
            if location_extra:
                location_parts.append(location_extra)

            item["location"] = location_parts  # 保持为列表形式

            item["room"] = house.xpath('.//a[@class="resblock-room"]/span/text()').getall()
            item["area"] = house.xpath('.//div[@class="resblock-area"]/span/text()').get()
            item["unit_price"] = (
                f"{house.xpath('.//div[@class="resblock-price"]//span[@class="number"]/text()').get()}元/㎡(均价)"
            )
            item["total_price"] = house.xpath('.//div[@class="resblock-price"]//div[@class="second"]/text()').get()

            yield item  # 返回 Item

        # 模拟翻页，查找“下一页”的页码并生成新请求
        current_page = response.url.split("pg")[-1].split("/")[0] if "pg" in response.url else 1
        next_page = int(current_page) + 1  # 增加页码

        # 拼接新的 URL 并发送请求
        next_page_url = f"https://bj.fang.lianjia.com/loupan/pg{next_page}/"

        # 判断是否还有下一页
        if next_page <= self.end_page:
            yield scrapy.Request(next_page_url, callback=self.parse)
