# begin.py
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

# 导入您的爬虫类。请根据您的项目结构调整导入路径。
from lianjia.spiders.new_house_spider import NewHouseSpider
from lianjia.spiders.second_hand_house_spider import SecondHandHouseSpider


def main():
    # 配置 Scrapy 日志（可选）
    configure_logging()

    # 创建一个 CrawlerProcess 实例，并传入自定义设置
    process = CrawlerProcess(
        settings={
            "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "DOWNLOAD_DELAY": 2,  # 设置下载延迟（秒）
            "CONCURRENT_REQUESTS": 2,  # 限制并发请求数
            "COOKIES_ENABLED": True,  # 启用 Cookie
        }
    )

    # 添加要运行的爬虫
    process.crawl(NewHouseSpider)
    process.crawl(SecondHandHouseSpider)

    # 启动爬虫（会阻塞直到所有爬虫完成）
    process.start()


if __name__ == "__main__":
    main()
