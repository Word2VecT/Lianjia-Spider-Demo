import scrapy

from lianjia.items import SecondHandHouseItem


class SecondHandHouseSpider(scrapy.Spider):
    name = "second_hand_house"
    allowed_domains = ["lianjia.com"]
    start_page = 3
    start_urls = [f"https://bj.lianjia.com/ershoufang/pg{start_page}/"]
    end_page = 10  # 爬取的页数

    custom_settings = {
        "FEEDS": {
            "second_hand_house_data.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            },
        },
    }

    cookies = {"lianjia_token": "2.00128465a045545efc03294c91b85e60a0"}

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, cookies=self.cookies, callback=self.parse)

    def parse(self, response):
        # 选择所有楼盘信息的父容器
        for house in response.xpath('//div[@class="info clear"]'):
            item = SecondHandHouseItem()
            item["title"] = house.xpath('.//div[@class="title"]/a/text()').get()
            item["position_info"] = house.xpath('.//div[@class="flood"]//div[@class="positionInfo"]//a/text()').getall()
            item["house_info"] = house.xpath('.//div[@class="address"]//div[@class="houseInfo"]/text()').get()
            item["total_price"] = f"{house.xpath(
                './div[@class="priceInfo"]/div[@class="totalPrice totalPrice2"]/span/text()'
            ).get()}万"
            item["unit_price"] = house.xpath('./div[@class="priceInfo"]/div[@class="unitPrice"]/span/text()').get()

            yield item  # 返回 Item

        # 模拟翻页，查找“下一页”的页码并生成新请求
        current_page = response.url.split("pg")[-1].split("/")[0] if "pg" in response.url else 1
        next_page = int(current_page) + 1  # 增加页码

        # 拼接新的 URL 并发送请求
        next_page_url = f"https://bj.lianjia.com/ershoufang/pg{next_page}/"

        # 判断是否还有下一页
        if next_page <= self.end_page:
            yield scrapy.Request(next_page_url, cookies=self.cookies, callback=self.parse)
