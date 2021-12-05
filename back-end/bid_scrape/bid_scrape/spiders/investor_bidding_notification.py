import scrapy
from .spider_utils import SpiderUtils
from .spider_constants import DocumentConstants, XpathConstants


class BiddingNotificationInvestors(scrapy.Spider):
    #  Thông báo mời thầu cho nhà đầu tư
    name = "investor_bidding_notification"
    start_urls, first_key, second_key, collection_name = SpiderUtils.init_attribute(name)

    def parse(self, response):
        links = response.xpath(XpathConstants.XPATH_GET_LINKS).extract()
        for link in links:
            yield scrapy.Request(link, callback=self.parse_a_page)

    def parse_a_page(self, response):
        yield {
            DocumentConstants.THOI_DIEM_DANG_TAI: response.xpath(XpathConstants.XPATH_GET_THOI_DIEM_DANG_TAI).get(),
            DocumentConstants.THOI_DIEM_DONG_THAU: response.xpath(XpathConstants.XPATH_GET_THOI_DIEM_DONG_THAU).get(),
            DocumentConstants.THONG_TIN_CHI_TIET: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET
            )
        }
