import scrapy
from .spider_constants import DocumentConstants, XpathConstants
from .spider_utils import SpiderUtils

class InvestorPreQualificationResult(scrapy.Spider):
    name = "investor_pre_qualification_result"
    start_urls, first_key, second_key, collection_name = SpiderUtils.init_attribute(name)

    XPATH_EXTRACT_TR_TABLE_TAG = "//table/tbody/tr"

    def parse(self, response):
        for link, category in self.get_link_and_category(response, self.XPATH_EXTRACT_TR_TABLE_TAG):
            request = scrapy.Request(link, callback=self.parse_a_page, cb_kwargs=dict(category_value=category))
            yield request

    def parse_a_page(self, response, category_value):
        yield {
            DocumentConstants.LOAI_DU_AN: category_value,
            DocumentConstants.THONG_TIN_CHI_TIET: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET
            ),
            DocumentConstants.KET_QUA: self.parse_a_complex_table(
                response=response,
                xpath_get_table_tag="/html/body/div[1]/div/div/div/div[1]/div/div/section[2]/div/div/div[2]/div[2]/div/div/div/table"
            )
        }

    def parse_a_complex_table(self, response, xpath_get_table_tag):
        xpath_get_column_name = xpath_get_table_tag + "/thead/tr/th/text()"
        xpath_extract_tr_tag_row = xpath_get_table_tag + "/tbody/tr"
        xpath_extract_text_in_cell = xpath_get_table_tag + "/tbody/tr[{}]/td[{}]/text()"
        result = []
        column_name = response.xpath(xpath_get_column_name).extract()
        num_rows = len(response.xpath(xpath_extract_tr_tag_row).extract())
        self.log("Column name: {} Num of row: {}".format(column_name, num_rows))
        for row in range(1, num_rows + 2):
            temp = {}
            for col in range(1, len(column_name) + 1):
                xpath = xpath_extract_text_in_cell.format(row, col)
                value = SpiderUtils.extract_first_with_none_check(response, xpath)
                temp[column_name[col - 1]] = value
            result.append(temp)
        return result

    def get_link_and_category(self, response, xpath_get_tr_table_tag):
        num = len(response.xpath(xpath_get_tr_table_tag).extract())
        result = []
        for index in range(2, num + 1, 2):
            xpath_get_link = xpath_get_tr_table_tag + "[{}]/td[2]/p/strong/a/@href".format(index)
            link = response.xpath(xpath_get_link).get()
            xpath_get_category = xpath_get_tr_table_tag + "[{}]/td[3]/p[text() = 'Loại dự án: ']/span/text()".format(index)
            category = response.xpath(xpath_get_category).get()
            result.append((link, category))
        self.log("result {}".format(result))
        return result
