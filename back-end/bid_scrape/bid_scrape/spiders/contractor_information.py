import scrapy
import logging
from .spider_constants import DocumentConstants
from .spider_utils import SpiderUtils

class ContractorSpider(scrapy.Spider):
    # Thông tin nhà thầu
    name = "contractor_information"

    THONG_TIN_CHUNG = "THÔNG TIN CHUNG"
    THONG_TIN_NGANH_NGHE = "THÔNG TIN NGÀNH NGHỀ"
    XPATH_GET_THONG_TIN_CHUNG = "//h3[text() = '{}']/following-sibling::div/div/div/table/tr/td"
    XPATH_GET_THONG_TIN_NGANH_NGHE = "//h3[text() = '{}']/following-sibling::div/table/tbody/tr/td"
    GET_TEXT = "text()"
    CSS_GET_CONTRACTOR_LINKS = "strong.color-3 a::attr(href)"

    def __init__(self, single_link=None, start_page=None, end_page=None, *args, **kwargs):
        super(ContractorSpider, self).__init__(*args, **kwargs)
        self.base_url, self.start_urls, self.first_key, self.second_key, self.collection_name, self.crawl_single_link \
            = SpiderUtils.init_attribute(self.name, single_link, start_page, end_page)

    def parse(self, response):
        logging.debug('response url: ' + response.url)
        if self.crawl_single_link:
            yield scrapy.Request(response.url, callback=self.parse_a_contractor)
        else:
            yield scrapy.Request(response.url, callback=self.parse_a_page)

    def parse_a_page(self, response):
        contractor_links = response.css(self.CSS_GET_CONTRACTOR_LINKS).getall()
        logging.info('parsing a page has {} contractors'.format(len(contractor_links)))
        for link in contractor_links:
            yield scrapy.Request(link, callback=self.parse_a_contractor)

    def parse_a_contractor(self, response):
        general_info_xpath = response.xpath(self.XPATH_GET_THONG_TIN_CHUNG.format(self.THONG_TIN_CHUNG))
        job_info_xpath = response.xpath(self.XPATH_GET_THONG_TIN_NGANH_NGHE.format(self.THONG_TIN_NGANH_NGHE))
        general_info = {}
        job_info = []

        # get general information of contractor
        if len(general_info_xpath) % 2 == 1:
            logging.debug("GENERAL INFO is odd number")
        for index in range(0, len(general_info_xpath), 2):
            key = general_info_xpath[index].xpath(self.GET_TEXT).get()
            value = general_info_xpath[index + 1].xpath(self.GET_TEXT).extract()
            general_info[key.strip()] = value[0].strip() if len(value) != 0 else ''

        # get job information of contractor
        for index in range(1, len(job_info_xpath), 2):
            job = job_info_xpath[index].xpath(self.GET_TEXT).get()
            job_info.append(job)

        yield {
            DocumentConstants.THONG_TIN_CHUNG: general_info,
            DocumentConstants.THONG_TIN_NGANH_NGHE: job_info
        }
