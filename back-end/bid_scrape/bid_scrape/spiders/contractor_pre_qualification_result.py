import scrapy
from .spider_constants import DocumentConstants, XpathConstants
from .spider_utils import SpiderUtils


class PreQualificationResultSpider(scrapy.Spider):
    # for contractors
    name = "contractor_pre_qualification_result"

    XPATH_EXTRACT_RESULT_LINKS = "//strong[@class = 'text-up color-1 ellipsis-content-1row']/a[@class = " \
                                 "'container-tittle']/@href "

    def __init__(self, single_link=None, start_page=None, end_page=None, *args, **kwargs):
        super(PreQualificationResultSpider, self).__init__(*args, **kwargs)
        self.base_url, self.start_urls, self.first_key, self.second_key, self.collection_name, self.crawl_single_link \
            = SpiderUtils.init_attribute(self.name, single_link, start_page, end_page)

    def parse(self, response):
        if self.crawl_single_link:
            yield scrapy.Request(response.url, callback=self.parse_a_result)
        else:
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


