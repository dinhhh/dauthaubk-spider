import scrapy
from .spider_constants import DocumentConstants, XpathConstants
from .spider_utils import SpiderUtils

class PreQualificationAnnouncementSpider(scrapy.Spider):
    #  Thông báo mời thầu / mời sơ tuyển cho nhà đầu tư
    name = "investor_pre_qualification_announcement"
    start_urls, first_key, second_key, collection_name = SpiderUtils.init_attribute(name)

    def parse(self, response):
        links = response.xpath(XpathConstants.XPATH_GET_LINKS).extract()
        for link in links:
            yield scrapy.Request(link, callback=self.parse_a_page)

    def parse_a_page(self, response):
        yield {
            DocumentConstants.THONG_TIN_CHI_TIET: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET
            ),
            DocumentConstants.DANH_SACH_FILE_DINH_KEM: self.parse_attach_files_table(
                response=response,
                xpath_extract_tbody="/html/body/div/div/div/div/div[1]/div/div/section[2]/div/div/div[2]/div[2]/div/div/div/div/table/tbody"
            )
        }

    def parse_attach_files_table(self, response, xpath_extract_tbody):
        #  xpath sample: /div/table/tbody
        xpath_extract_tr_tag = xpath_extract_tbody + "/tr"
        num_row = len(response.xpath(xpath_extract_tr_tag))
        if num_row == 0:
            raise Exception("Table with attach files is empty. URL {}".format(response.url))
        result = []
        column_name = response.xpath(xpath_extract_tr_tag + "[1]/td/text()").extract()
        for row in range(2, num_row + 1):
            temp = {}
            for col in range(1, len(column_name) + 1):
                xpath_extract_td_tag = xpath_extract_tr_tag + "[{}]/td[{}]/text()".format(row, col)
                text_list = response.xpath(xpath_extract_td_tag).extract()
                text = text_list[0] if len(text_list) != 0 else ""
                key = column_name[col - 1]
                if key == DocumentConstants.TAI_XUONG:
                    xpath_get_link = xpath_extract_tr_tag + "[{}]/td[{}]/a/@href".format(row, col)
                    value = response.xpath(xpath_get_link).get()
                    temp[key] = value
                else:
                    temp[key] = text
            result.append(temp)
        return result
