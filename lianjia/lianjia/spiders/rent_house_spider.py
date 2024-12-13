import re

import scrapy

from lianjia.items import RentHouseItem


class RentHouseSpider(scrapy.Spider):
    name = "rent_house"
    allowed_domains = ["lianjia.com"]
    city = "sz"  # bj | sh | gz | sz | changde
    base_url = f"https://{city}.lianjia.com"
    max_price_page = 8 if city == "sh" else 7

    custom_settings = {
        "FEEDS": {
            f"{city}_rent_house_data.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            },
        },
    }

    # cookies = {"lianjia_token": "2.001212d80645e41e6a03bff137c7ff980e"}

    def start_requests(self):
        url = f"{self.base_url}/zufang/"
        yield scrapy.Request(url=url, callback=self.parse_city)

    def parse_city(self, response):
        """Parse the city-level rental homepage to determine if further subdivision is needed."""
        self.logger.info(f"Parsing city page: {response.url}")
        total_page = self.get_total_page(response) or 0
        total_count = self.get_total_count(response) or 0
        if total_page == 100 or total_count > 3000:
            area_half_url_list = response.xpath(
                '//div[@class="filter"]/div[@class="filter__wrapper w1150"]/ul[@data-target="area"]//li/a/@href'
            ).getall()
            area_half_url_list = [url for url in area_half_url_list if url != "/zufang/"]
            for area_half_url in area_half_url_list:
                area_url = f"{self.base_url}{area_half_url}"
                yield scrapy.Request(url=area_url, callback=self.parse_area, dont_filter=True)
        else:
            yield from self.to_parse(response.url, total_page, total_count)

    def parse_area(self, response):
        """Parse an area category to determine if further subdivision by price is needed."""
        self.logger.info(f"Parsing area page: {response.url}")
        total_page = self.get_total_page(response)
        total_count = self.get_total_count(response)
        if total_page == 100 or total_count > 3000:
            for i in range(1, self.max_price_page + 1):
                price_url = f"{response.url}rp{i}/"
                yield scrapy.Request(url=price_url, callback=self.parse_price, dont_filter=True)
        else:
            yield from self.to_parse(response.url, total_page, total_count)

    def parse_price(self, response):
        """Parse a price range category to determine if further subdivision by room type is needed."""
        self.logger.info(f"Parsing price range page: {response.url}")
        total_page = self.get_total_page(response)
        total_count = self.get_total_count(response)

        price_pattern = re.compile(r"(rp[1-8])") if self.city == "sh" else re.compile(r"(rp[1-7])")
        rooms = [f"l{i}" for i in range(0, 4)]
        if total_page == 100 or total_count > 3000:
            match = price_pattern.search(response.url)
            if match:
                price = match.group(1)
                left, right = response.url.split(price, 1)
                for room in rooms:
                    room_url = f"{left}{room}{price}{right}"
                    yield scrapy.Request(url=room_url, callback=self.parse_room, dont_filter=True)
            else:
                self.logger.warning(f"No valid '{price}' identifier found in URL: {response.url}")
        else:
            yield from self.to_parse(response.url, total_page, total_count)

    def parse_room(self, response):
        """Parse a room type category to determine if further subdivision by direction is needed."""
        self.logger.info(f"Parsing room type page: {response.url}")
        total_page = self.get_total_page(response)
        total_count = self.get_total_count(response)

        room_pattern = re.compile(r"(l[0-3])")
        directions = ["f100500000001", "f100500000005", "f100500000003", "f100500000007", "f100500000009"]
        if total_page == 100 or total_count > 3000:
            match = room_pattern.search(response.url)
            if match:
                room = match.group(1)
                left, right = response.url.split(room, 1)
                for direction in directions:
                    direction_url = f"{left}{direction}{room}{right}"
                    yield scrapy.Request(url=direction_url, callback=self.parse_direction, dont_filter=True)
            else:
                self.logger.warning(f"No valid '{room}' identifier found in URL: {response.url}")
        else:
            yield from self.to_parse(response.url, total_page, total_count)

    def parse_direction(self, response):
        """Parse a direction category to determine if further subdivision by floor is needed."""
        self.logger.info(f"Parsing direction page: {response.url}")
        total_page = self.get_total_page(response)
        total_count = self.get_total_count(response)

        direction_pattern = re.compile(r"(f10050000000[1|5|3|7|9])")
        floors = ["lc200500000003", "lc200500000002", "lc200500000001"]
        if total_page == 100 or total_count > 3000:
            match = direction_pattern.search(response.url)
            if match:
                direction = match.group(1)
                left, right = response.url.split(direction, 1)
                for floor in floors:
                    floor_url = f"{left}{floor}{direction}{right}"
                    yield scrapy.Request(url=floor_url, callback=self.parse_floor, dont_filter=True)
            else:
                self.logger.warning(f"No valid '{direction}' identifier found in URL: {response.url}")
        else:
            yield from self.to_parse(response.url, total_page, total_count)

    def parse_floor(self, response):
        """Parse a floor category and handle pagination."""
        self.logger.info(f"Parsing floor page: {response.url}")
        total_page = self.get_total_page(response)
        total_count = self.get_total_count(response)

        if total_page == 100 or total_count > 3000:
            self.logger.warning(f"Too many houses in {response.url}. Consider further subdivision.")
        if total_page or total_count:
            yield from self.to_parse(response.url, total_page, total_count)
        else:
            self.logger.warning(f"No pagination data found for {response.url}")

    def get_total_page(self, response):
        """Retrieve the total number of pages from the response."""
        total_page_str = response.xpath('//div[@class="content__pg"]/@data-totalpage').get()
        if total_page_str:
            try:
                total_page = int(total_page_str)
                self.logger.debug(f"Total pages found: {total_page}")
                return total_page
            except ValueError:
                self.logger.warning(f"Invalid total_page value: {total_page_str}")
                return 0
        self.logger.warning("Page data not found")
        return 0

    def get_total_count(self, response):
        """Retrieve the total number of houses from the response."""
        total_count_str = response.xpath('//span[@class="content__title--hl"]/text()').get()
        if total_count_str:
            try:
                total_count = int(total_count_str)
                self.logger.debug(f"Total houses found: {total_count}")
                return total_count
            except ValueError:
                self.logger.warning(f"Invalid total_count value: {total_count_str}")
                return 0
        self.logger.warning("Total count data not found")
        return 0

    def to_parse(self, url, total_page, total_count):
        """Construct URLs for each page and send to `parse`."""
        if total_page:
            for i in range(1, total_page + 1):
                page_url = f"{url}pg{i}/"  # Use a new variable to prevent URL accumulation
                yield scrapy.Request(url=page_url, callback=self.parse, dont_filter=True)
        elif total_count:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)
        else:
            self.logger.warning(f"Cannot parse pages for URL: {url} due to missing total_page or total_count data")

    def parse(self, response):
        """Extract rental house information from the listing page."""
        self.logger.info(f"Extracting data from page: {response.url}")

        # Select all house listing containers
        for house in response.xpath(
            '//div[@class="content__article"]/div[@class="content__list"][1]//div[@class="content__list--item"]'
        ):
            item = RentHouseItem()

            # Extract and strip title, or set a default value if None
            title = house.xpath(
                './div[@class="content__list--item--main"]/p[@class="content__list--item--title"]/a[@class="twoline"]/text()'
            ).get()
            item["title"] = title.strip() if title else "N/A"

            # Extract description and clean it
            des = house.xpath(
                './div[@class="content__list--item--main"]/p[@class="content__list--item--des"]//text()'
            ).getall()
            item["des"] = ["".join(text.split()) for text in des if text.strip() and text.strip() not in ["-", "/"]]

            # Extract bottom info or set an empty list if None
            item["bottom"] = [
                text.strip()
                for text in house.xpath(
                    './div[@class="content__list--item--main"]/p[@class="content__list--item--bottom oneline"]//i/text()'
                ).getall()
                if text.strip()
            ] or []

            # Extract brand or set a default value
            brand = house.xpath(
                './div[@class="content__list--item--main"]/p[@class="content__list--item--brand oneline"]/span[@class="brand"]/text()'
            ).get()
            item["brand"] = brand.strip() if brand else "N/A"

            # Extract price or set a default value
            price = house.xpath(
                './div[@class="content__list--item--main"]/span[@class="content__list--item-price"]//text()'
            ).get()
            item["price"] = f"{price.strip()}元/月" if price else "N/A"

            yield item  # Return the populated item
