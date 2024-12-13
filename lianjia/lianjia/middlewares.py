# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface

# useful for handling different item types with a single interface
import random

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message


class RedirectRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        # 检查是否是重定向
        if response.status in [301, 302]:
            spider.logger.warning(f"Redirect detected for {request.url} to {response.headers.get('Location')}")

            # 获取当前重试次数
            retry_count = request.meta.get("retry_count", 0)

            # 如果重试次数超过最大重试限制，直接返回
            if retry_count >= self.max_retry_times:
                spider.logger.error(f"Max retries reached for {request.url}. Giving up.")
                return response

            # 增加重试计数并重新发起请求
            retry_count += 1
            new_request = request.copy()
            new_request.meta["retry_count"] = retry_count
            spider.logger.info(f"Retrying {request.url} ({retry_count}/{self.max_retry_times})...")
            return self._retry(new_request, response_status_message(response.status), spider) or response

        # 如果不是重定向，直接返回原始响应
        return response


class TotalCountRetryMiddleware:
    def __init__(self, retry_times):
        self.retry_times = retry_times

    @classmethod
    def from_crawler(cls, crawler):
        # 获取配置的最大重试次数
        retry_times = crawler.settings.getint("RETRY_TIMES", 10)
        return cls(retry_times)

    def process_response(self, request, response, spider):
        if "captcha" in response.url:
            spider.logger.warning(f"Detected captcha on {request.url}, skipping retries")
            raise IgnoreRequest(f"Captcha detected for {request.url}")

        # 检查页面是否包含 total_count_str
        total_count_str = response.xpath('//span[@class="content__title--hl"]/text()').get()
        if total_count_str:
            return response  # 如果存在 total_count_str，则正常返回响应

        # 如果 total_count_str 不存在，判断是否需要重试
        retry_times = request.meta.get("retry_times", 0)
        if retry_times < self.retry_times:
            spider.logger.info(f"Retrying {request.url} due to missing total_count (attempt {retry_times + 1})")
            retry_req = request.copy()
            retry_req.meta["retry_times"] = retry_times + 1
            retry_req.dont_filter = True  # 防止 URL 被过滤
            return retry_req  # 返回一个新的请求以进行重试
        else:
            spider.logger.warning(f"Giving up on {request.url} after {retry_times} retries due to missing total_count")
            raise IgnoreRequest(f"Missing total_count_str after {retry_times} retries")


class LianjiaSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        yield from result

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        yield from start_requests

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class LianjiaDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class ProxyMiddleware:
    def __init__(self):
        self.proxies = [
            "http://t13401380689666:dpi6k4ix@b292.kdltpspro.com:15818",  # 替换为实际的代理信息
        ]

    def process_request(self, request, spider):
        proxy = random.choice(self.proxies)  # 随机选择一个代理
        request.meta["proxy"] = proxy
        spider.logger.info(f"Using Proxy: {proxy}")


class CloseConnectionMiddleware:
    def process_request(self, request, spider):
        request.headers["Connection"] = "close"  # 添加请求头
