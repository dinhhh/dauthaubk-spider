from subprocess import call

import scrapy
from .spider_constants import DocumentConstants, XpathConstants
from .spider_utils import SpiderUtils


class InvitationBidSpider(scrapy.Spider):
    # Thông báo mời thầu cho nhà thầu
    name = "contractor_bidding_invitation"

    def __init__(self, single_link=None, start_page=None, end_page=None, *args, **kwargs):
        super(InvitationBidSpider, self).__init__(*args, **kwargs)
        self.base_url, self.start_urls, self.first_key, self.second_key, self.collection_name, self.crawl_single_link \
            = SpiderUtils.init_attribute(self.name, single_link, start_page, end_page)

        # override start urls because of special case
        if not self.crawl_single_link:
            self.start_urls.clear()
            for i in range(start_page, end_page + 1):
                for j in range(start_page, end_page + 1):
                    url = self.base_url.format(i, j)
                    self.start_urls.append(url)

    XPATH_EXTRACT_TABLE = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr/td//text()"
    XPATH_EXTRACT_THONG_TIN_CHI_TIET_TABLE = XPATH_EXTRACT_TABLE.format(DocumentConstants.THONG_TIN_CHI_TIET_UPPER_CASE)
    XPATH_EXTRACT_THAM_DU_THAU_TABLE = XPATH_EXTRACT_TABLE.format(DocumentConstants.THAM_DU_THAU)
    XPATH_EXTRACT_MO_THAU_TABLE = XPATH_EXTRACT_TABLE.format(DocumentConstants.MO_THAU_UPPER_CASE)
    XPATH_EXTRACT_BAO_DAM_DU_THAU_TABLE = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr/td/text()".\
        format(DocumentConstants.BAO_DAM_DU_THAU_UPPER_CASE)
    XPATH_EXTRACT_THONG_TIN_CHI_TIET_WITH_MULTI_ATTACH_FILE = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr/td/text()".\
        format(DocumentConstants.THONG_TIN_CHI_TIET_UPPER_CASE)
    XPATH_GET_DOCUMENTS_NAME = "//td[@class = 'a-line']"
    XPATH_GET_DOCUMENTS_LINK = "//td[@class = 'a-line']/a/@href"
    XPATH_GET_THONG_BAO_LIEN_QUAN = "//td[text() = 'Thông báo liên quan']/following-sibling::td/a/@href"
    XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr".format(
        DocumentConstants.THONG_TIN_CHI_TIET_UPPER_CASE)
    XPATH_GET_TR_TAG_BAO_DAM_DU_THAU = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr".format(
        DocumentConstants.BAO_DAM_DU_THAU_UPPER_CASE)
    XPATH_EXTRACT_INVITATION_LINKS = "//a[@class = 'container-tittle']/@href"

    def parse(self, response):
        self.log('response url: ' + response.url)
        if self.crawl_single_link:
            yield scrapy.Request(response.url, callback=self.parse_a_invitation)
        else:
            yield scrapy.Request(response.url, callback=self.parse_a_page)

    def parse_a_page(self, response):
        links = response.xpath(self.XPATH_EXTRACT_INVITATION_LINKS).extract()
        self.log("Parse a page of {} invitations".format(len(links)))
        for link in links:
            yield scrapy.Request(link, callback=self.parse_a_invitation)


    def parse_a_invitation(self, response):
        item = {DocumentConstants.THONG_TIN_CHI_TIET: SpiderUtils.parse_a_table_with_multi_attach_files(
                    response=response,
                    xpath_get_tr_tag=self.XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET),
                DocumentConstants.THOI_DIEM_DONG_THAU: SpiderUtils.get_with_none_check(
                    response,
                    XpathConstants.XPATH_GET_THOI_DIEM_DONG_THAU),
                DocumentConstants.THOI_DIEM_DANG_TAI: SpiderUtils.get_with_none_check(
                    response,
                    XpathConstants.XPATH_GET_THOI_DIEM_DANG_TAI),
                DocumentConstants.THAM_DU_THAU: (SpiderUtils.parse_a_table_with_out_attach_file(
                    response, self.XPATH_EXTRACT_THAM_DU_THAU_TABLE)),
                DocumentConstants.MO_THAU: (SpiderUtils.parse_a_table_with_out_attach_file(
                    response, self.XPATH_EXTRACT_MO_THAU_TABLE)),
                DocumentConstants.BAO_DAM_DU_THAU: (SpiderUtils.parse_a_table_with_multi_attach_files(
                    response=response,
                    xpath_get_tr_tag=self.XPATH_GET_TR_TAG_BAO_DAM_DU_THAU
                ))}

        yield item

    def is_contain_thong_bao_lien_quan(self, response, xpath):
        checker = response.xpath(self.XPATH_EXTRACT_THONG_TIN_CHI_TIET_TABLE).extract()
        return SpiderUtils.get_index(DocumentConstants.HO_SO_MOI_THAU, checker) != -1
