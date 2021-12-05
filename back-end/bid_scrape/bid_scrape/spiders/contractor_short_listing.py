import scrapy
from .spider_constants import XpathConstants, DocumentConstants
from .spider_utils import SpiderUtils


def get_column_name(response, xpath_get_column_name):
    return response.xpath(xpath_get_column_name).extract()


class ShortListingSpider(scrapy.Spider):
    # Danh sách ngắn cho nhà thầu
    name = "contractor_short_listing"
    start_urls, first_key, second_key, collection_name = SpiderUtils.init_attribute(name)

    XPATH_GET_TR_TAG_THONG_TIN_CHUNG = "//div/div/section[2]/div/div/div[2]/div[1]/div[1]/div/div/table/tr"
    XPATH_EXTRACT_SECOND_TABLE = "//div/div/section[2]/div/div/div[2]/div[1]/div[2]/div/div/table"
    XPATH_EXTRACT_COLUMN_NAME = XPATH_EXTRACT_SECOND_TABLE + "/thead/tr/td/text()"
    XPATH_EXTRACT_TR_TAG_ROW = XPATH_EXTRACT_SECOND_TABLE + "/tbody/tr"
    XPATH_EXTRACT_TEXT_IN_CELL = XPATH_EXTRACT_SECOND_TABLE + "/tbody/tr[{}]/td[{}]/text()"

    def parse(self, response):
        links = response.xpath(XpathConstants.XPATH_GET_LINKS).extract()
        for link in links:
            yield scrapy.Request(link, callback=self.parse_a_page)

    def parse_a_page(self, response):
        yield {
            DocumentConstants.NGAY_DANG_TAI: response.xpath(XpathConstants.XPATH_GET_NGAY_DANG_TAI).get(),
            DocumentConstants.HINH_THUC_DAU_THAU: response.xpath(XpathConstants.XPATH_GET_HINH_THUC_THAU).get(),
            DocumentConstants.THONG_TIN_CHUNG: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=self.XPATH_GET_TR_TAG_THONG_TIN_CHUNG
            ),
            DocumentConstants.THONG_TIN_CHI_TIET: self.parse_a_complex_table(response)
        }

    def parse_a_complex_table(self, response):
        result = []
        column_name = get_column_name(response, self.XPATH_EXTRACT_COLUMN_NAME)
        num_rows = len(response.xpath(self.XPATH_EXTRACT_TR_TAG_ROW).extract())
        self.log("Column name: {} Num of row: {}".format(column_name, num_rows))
        for row in range(1, num_rows + 2):
            temp = {}
            for col in range(1, len(column_name) + 1):
                xpath = self.XPATH_EXTRACT_TEXT_IN_CELL.format(row, col)
                value = SpiderUtils.extract_first_with_none_check(response, xpath)
                temp[column_name[col - 1]] = value
            result.append(temp)
        return result

