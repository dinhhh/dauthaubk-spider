import scrapy
from .spider_utils import SpiderUtils
from .spider_constants import XpathConstants, DocumentConstants


class BiddingExtensionCorrectionSpider(scrapy.Spider):
    # Thông báo gia hạn / đính chính cho nhà thầu
    name = "contractor_bidding_correction"

    XPATH_GET_LINKS = "//a[@class = 'container-tittle']/@href"

    def __init__(self, single_link=None, start_page=None, end_page=None, *args, **kwargs):
        super(BiddingExtensionCorrectionSpider, self).__init__(*args, **kwargs)
        self.base_url, self.start_urls, self.first_key, self.second_key, self.collection_name, self.crawl_single_link \
            = SpiderUtils.init_attribute(self.name, single_link, start_page, end_page)

    def parse(self, response):
        if self.crawl_single_link:
            yield scrapy.Request(response.url, callback=self.parse_a_page)
        else:
            links = response.xpath(self.XPATH_GET_LINKS).extract()
            for link in links:
                yield scrapy.Request(link, callback=self.parse_a_page)

    def parse_a_page(self, response):
        yield {
            DocumentConstants.THONG_TIN_CHI_TIET: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET
            ),
            DocumentConstants.THAM_DU_THAU: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_THAM_DU_THAU
            ),
            DocumentConstants.MOI_THAU: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_MOI_THAU
            ),
            DocumentConstants.BAO_DAM_DU_THAU: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_BAO_DAM_DU_THAU
            )
        }

