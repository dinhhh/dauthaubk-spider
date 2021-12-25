import scrapy
from .spider_constants import DocumentConstants, XpathConstants
from .spider_utils import SpiderUtils

class OnlineBidOpeningResultSpider(scrapy.Spider):
    # Kế hoạch mở thầu điện tử cho nhà thầu
    name = "contractor_online_bidding_result"
    start_urls, first_key, second_key, collection_name = SpiderUtils.init_attribute(name)

    XPATH_EXTRACT_KET_QUA = "//div[@class = 'd-box-new']/div/div/div/table/tbody/tr/td"
    XPATH_EXTRACT_RESULT_LINKS = "//strong[@class = 'text-up color-1 ellipsis-content-1row']/a/@href"

    def parse(self, response):
        self.log("Contractor_online_bidding_result is crawling")
        links = response.xpath(self.XPATH_EXTRACT_RESULT_LINKS).extract()
        self.log("Link: {}".format(links))
        if links is not None:
            for link in links:
                yield scrapy.Request(link, callback=self.parse_a_result)

    def parse_a_result(self, response):
        yield {
            DocumentConstants.THONG_TIN_CHI_TIET: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET),
            DocumentConstants.KET_QUA: SpiderUtils.parse_a_complex_table_with_out_attach_file(
                response=response,
                xpath_extract_table=self.XPATH_EXTRACT_KET_QUA
            ),
        }
