import scrapy
import logging
from .spider_constants import DocumentConstants
from .spider_utils import SpiderUtils

class InvestorSpider(scrapy.Spider):
    # Thông tin nhà đầu tư
    name = "investors_information"

    MA_CO_QUAN = "Mã cơ quan"
    TITLE = "THÔNG TIN CƠ QUAN"
    GET_INVESTOR_LINKS = "//a[@class = 'container-tittle color-0086D7 font-roboto-regular']/@href"
    GET_GENERAL_INFO = "//h3[text() = '{}']/following-sibling::div/div/div/table/tr/td".format(TITLE)
    GET_TEXT = "text()"

    def __init__(self, single_link=None, start_page=None, end_page=None, *args, **kwargs):
        super(InvestorSpider, self).__init__(*args, **kwargs)
        self.base_url, self.start_urls, self.first_key, self.second_key, self.collection_name, self.crawl_single_link \
            = SpiderUtils.init_attribute(self.name, single_link, start_page, end_page)

    def parse(self, response):
        if self.crawl_single_link:
            yield scrapy.Request(response.url, callback=self.parse_a_investor)
        else:
            yield scrapy.Request(url=response.url, callback=self.parse_one_page)

    def parse_one_page(self, response):
        investor_links = response.xpath(self.GET_INVESTOR_LINKS).extract()
        logging.info("parsing a page has {} investors".format(len(investor_links)))
        for link in investor_links:
            yield scrapy.Request(url=link, callback=self.parse_a_investor)

    def parse_a_investor(self, response):
        logging.info("parsing a investor at link {}".format(response.url))
        general_info_xpath = response.xpath(self.GET_GENERAL_INFO)
        general_info = {}
        for index in range(0, len(general_info_xpath), 2):
            key = general_info_xpath[index].xpath(self.GET_TEXT).get().strip()
            value = general_info_xpath[index + 1].xpath(self.GET_TEXT).extract()
            general_info[key] = value[0].strip() if len(value) != 0 else ''
        yield {
            DocumentConstants.THONG_TIN_CHUNG: general_info
        }
