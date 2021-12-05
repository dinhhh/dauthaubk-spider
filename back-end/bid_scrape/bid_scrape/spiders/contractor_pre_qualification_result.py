import scrapy
from .spider_constants import DocumentConstants, XpathConstants
from .spider_utils import SpiderUtils


class PreQualificationResultSpider(scrapy.Spider):
    # for contractors
    name = "contractor_pre_qualification_result"
    start_urls, first_key, second_key, collection_name = SpiderUtils.init_attribute(name)

    XPATH_EXTRACT_RESULT_LINKS = "//strong[@class = 'text-up color-1 ellipsis-content-1row']/a[@class = " \
                                 "'container-tittle']/@href "

    def parse(self, response):
        links = response.xpath(self.XPATH_EXTRACT_RESULT_LINKS).extract()
        if links is not None:
            for link in links:
                yield scrapy.Request(link, callback=self.parse_a_result)

    def parse_a_result(self, response):
        yield {
            DocumentConstants.THONG_TIN_CHI_TIET: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET),
        }


