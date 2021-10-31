import scrapy
from scrapy.crawler import CrawlerProcess
from spiders.contractors_spider import ContractorSpider

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(ContractorSpider)
    process.start()