import scrapy
from .spider_constants import DocumentConstants, XpathConstants
from .spider_utils import SpiderUtils


class InvitationBidSpider(scrapy.Spider):
    # Thông báo mời thầu cho nhà thầu
    name = "contractor_bidding_invitation"
    base_url = "http://muasamcong.mpi.gov.vn/lua-chon-nha-thau?p_auth=T3MvHbz04y&p_p_id=luachonnhathau_WAR_bidportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2&_luachonnhathau_WAR_bidportlet_denNgay=&_luachonnhathau_WAR_bidportlet_tuNgay=&_luachonnhathau_WAR_bidportlet_sapXep=DESC&_luachonnhathau_WAR_bidportlet_nguonVon=1&_luachonnhathau_WAR_bidportlet_hinhThuc=1&_luachonnhathau_WAR_bidportlet_displayItem=10&_luachonnhathau_WAR_bidportlet_chuDauTu=&_luachonnhathau_WAR_bidportlet_nhaThauIndex=nhaThauIndex&_luachonnhathau_WAR_bidportlet_timKiemTheo=&_luachonnhathau_WAR_bidportlet_benMoiThau=&_luachonnhathau_WAR_bidportlet_time=-1&_luachonnhathau_WAR_bidportlet_currentPage2={}&_luachonnhathau_WAR_bidportlet_currentPage1={}&_luachonnhathau_WAR_bidportlet_loaiThongTin=3&_luachonnhathau_WAR_bidportlet_searchText=&_luachonnhathau_WAR_bidportlet_dongMo=0&_luachonnhathau_WAR_bidportlet_javax.portlet.action=list"
    from_page = 1
    to_page = 10
    first_key = "Thông tin chi tiết"
    second_key = "Số hiệu KHLCNT"
    collection_name = "contractorBiddingInvitations"
    start_urls = []

    def __init__(self):
        for i in range(self.from_page, self.to_page + 1):
            for j in range(self.from_page, self.to_page + 1):
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
        yield scrapy.Request(response.url, callback=self.parse_a_page)

    def parse_a_page(self, response):
        links = response.xpath(self.XPATH_EXTRACT_INVITATION_LINKS).extract()
        self.log("Parse a page of {} invitations".format(len(links)))
        for link in links:
            yield scrapy.Request(link, callback=self.parse_a_invitation)


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
