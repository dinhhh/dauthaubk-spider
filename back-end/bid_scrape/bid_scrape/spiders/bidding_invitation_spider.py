import scrapy
from .spider_constants import DocumentConstants
from .spider_utils import SpiderUtils


class InvitationBidSpider(scrapy.Spider):
    name = "bidding_invitation_spider"
    start_urls = ["http://muasamcong.mpi.gov.vn/lua-chon-nha-thau?p_auth=CUVNWEItvr&p_p_id"
                  "=luachonnhathau_WAR_bidportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1"
                  "&p_p_col_count=2&_luachonnhathau_WAR_bidportlet_id=431548&_luachonnhathau_WAR_bidportlet_name=3"
                  "&_luachonnhathau_WAR_bidportlet_javax.portlet.action=detail"]
    first_key = "Thông tin chi tiết"
    second_key = "Số hiệu KHLCNT"
    collection_name = "biddingInvitations"
    FROM_PAGE = 1
    TO_PAGE = 10

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

    def parse(self, response):
        yield scrapy.Request(response.url, callback=self.parse_a_invitation)

    def parse_a_invitation(self, response):
        # sample page: "http://muasamcong.mpi.gov.vn/lua-chon-nha-thau?p_auth=fLHHstYwXU&p_p_id"
        #           "=luachonnhathau_WAR_bidportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1"
        #           "&p_p_col_count=2&_luachonnhathau_WAR_bidportlet_id=430244&_luachonnhathau_WAR_bidportlet_name=3"
        #           "&_luachonnhathau_WAR_bidportlet_javax.portlet.action=detail"
        #
        # OR http://muasamcong.mpi.gov.vn/lua-chon-nha-thau?p_auth=5fwIZtRwVT&p_p_id=luachonnhathau_WAR_bidportlet
        # &p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2
        # &_luachonnhathau_WAR_bidportlet_id=431548&_luachonnhathau_WAR_bidportlet_name=3
        # &_luachonnhathau_WAR_bidportlet_javax.portlet.action=detail

        item = {
            DocumentConstants.THAM_DU_THAU: (SpiderUtils.parse_a_table_with_out_attach_file(
                response, self.XPATH_EXTRACT_THAM_DU_THAU_TABLE)),
            DocumentConstants.MO_THAU: (SpiderUtils.parse_a_table_with_out_attach_file(
                response, self.XPATH_EXTRACT_MO_THAU_TABLE)),
            DocumentConstants.BAO_DAM_DU_THAU: SpiderUtils.parse_a_table_with_multi_attach_file(
                response, self.XPATH_EXTRACT_BAO_DAM_DU_THAU_TABLE, DocumentConstants.HO_SO_MOI_THAU,
                DocumentConstants.LAM_RO_E_HSMT, self.XPATH_GET_DOCUMENTS_NAME, self.XPATH_GET_DOCUMENTS_LINK)
        }

        checker = response.xpath(self.XPATH_EXTRACT_THONG_TIN_CHI_TIET_TABLE).extract()
        if len(response.xpath(self.XPATH_EXTRACT_BAO_DAM_DU_THAU_TABLE).extract()) < 1 and SpiderUtils.get_index(
                DocumentConstants.HO_SO_MOI_THAU, checker) != -1:
            item[DocumentConstants.THONG_TIN_CHI_TIET] = SpiderUtils.parse_a_table_with_multi_attach_file(
                response, self.XPATH_EXTRACT_THONG_TIN_CHI_TIET_WITH_MULTI_ATTACH_FILE,
                DocumentConstants.HO_SO_MOI_THAU,
                DocumentConstants.LAM_RO_E_HSMT,
                self.XPATH_GET_DOCUMENTS_NAME,
                self.XPATH_GET_DOCUMENTS_LINK,
                special_document_name=DocumentConstants.THONG_BAO_LIEN_QUAN,
                xpath_get_special_document_links=self.XPATH_GET_THONG_BAO_LIEN_QUAN)
        else:
            item[DocumentConstants.THONG_TIN_CHI_TIET] = SpiderUtils.parse_a_table_with_out_attach_file(
                response, self.XPATH_EXTRACT_THONG_TIN_CHI_TIET_TABLE)

        yield item

