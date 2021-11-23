import scrapy

from .spider_constants import XpathConstants, DocumentConstants
from .spider_utils import SpiderUtils


class AwardResultSpider(scrapy.Spider):
    name = "bidding_result_spider"
    start_urls = []

    collection_name = "biddingResults"
    first_key = "Thông tin chi tiết"
    second_key = "Số hiệu KHLCNT"

    FROM_PAGE = 1
    TO_PAGE = 5

    DINH_KEM_THONG_BAO = 'Đính kèm thông báo kết quả LCNT'
    LINH_VUC = "Lĩnh vực: "

    XPATH_GET_HINH_THUC_DAU_THAU = '/html/body/div/div/div/div/div[1]/div/div/section[2]/div/div/div[1]/div/div/div[' \
                                   '3]/div/h3/text() '
    XPATH_GET_ALL_THONG_TIN_CHI_TIET = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr/td//text()". \
        format(DocumentConstants.THONG_TIN_CHI_TIET_UPPER_CASE)
    XPATH_GET_GIA_GOI_THAU = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr/td/strong/text()". \
        format(DocumentConstants.THONG_TIN_CHI_TIET_UPPER_CASE)
    XPATH_GET_ALL_NAME_OF_ATTACH_FILES = "//a[@class = 'showNotify']/text()"
    XPATH_EXTRACT_KET_QUA = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr/td//text()". \
        format(DocumentConstants.KET_QUA)
    XPATH_GET_NHA_THAU_TRUNG_THAU_KHAC = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr/td//text()". \
        format(DocumentConstants.CAC_NHA_THAU_TRUNG_THAU_KHAC)
    XPATH_EXTRACT_MO_TA_TOM_TAT_GOI_THAU = "//span[text() = '{}']/../following-sibling::div/div/div/div/table/tbody/tr/td". \
        format(DocumentConstants.MO_TA_TOM_TAT_GOI_THAU)
    XPATH_EXTRACT_CO_WINNING = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr/td/text()". \
        format(DocumentConstants.CAC_NHA_THAU_TRUNG_THAU_KHAC)
    XPATH_EXTRACT_GIA_GOI_THAU = "//span[text() = '{}']/../following-sibling::div/div/div/table/tr/td/strong/text()". \
        format(DocumentConstants.CAC_NHA_THAU_TRUNG_THAU_KHAC)
    XPATH_EXTRACT_RESULT_LINKS = "//a[@class = 'container-tittle']/@href"
    XPATH_EXTRACT_CATEGORY = "//p[text() = '{}']/span/text()".format(LINH_VUC)

    def __init__(self):
        url = "http://muasamcong.mpi.gov.vn/lua-chon-nha-thau?p_auth=ZoScjIVHJx&p_p_id=luachonnhathau_WAR_bidportlet" \
              "&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2" \
              "&_luachonnhathau_WAR_bidportlet_timKiemTheo=1&_luachonnhathau_WAR_bidportlet_time=0" \
              "&_luachonnhathau_WAR_bidportlet_benMoiThau=&_luachonnhathau_WAR_bidportlet_denNgay" \
              "=&_luachonnhathau_WAR_bidportlet_tuNgay=&_luachonnhathau_WAR_bidportlet_loaiThongTin=8" \
              "&_luachonnhathau_WAR_bidportlet_searchText=&_luachonnhathau_WAR_bidportlet_sapXep=DESC" \
              "&_luachonnhathau_WAR_bidportlet_currentPage={}&_luachonnhathau_WAR_bidportlet_dongMo=0" \
              "&_luachonnhathau_WAR_bidportlet_nguonVon=1&_luachonnhathau_WAR_bidportlet_hinhThuc=1" \
              "&_luachonnhathau_WAR_bidportlet_displayItem=10&_luachonnhathau_WAR_bidportlet_linhVuc=-1" \
              "&_luachonnhathau_WAR_bidportlet_javax.portlet.action=list "
        for i in range(self.FROM_PAGE, self.TO_PAGE + 1):
            self.start_urls.append(url.format(i))

    def parse(self, response):
        result_links = response.xpath(self.XPATH_EXTRACT_RESULT_LINKS).extract()
        category_list = response.xpath(self.XPATH_EXTRACT_CATEGORY).extract()
        if len(result_links) != len(category_list):
            raise Exception("Response url {} parsing error".format(response.url))
        for link, category in zip(result_links, category_list):
            request = scrapy.Request(link, callback=self.parse_a_result, cb_kwargs=dict(category_value=category))
            yield request

    def parse_a_result(self, response, category_value):
        yield {
            DocumentConstants.NGAY_PHE_DUYET: response.xpath(XpathConstants.XPATH_GET_NGAY_PHE_DUYET).get(),
            DocumentConstants.NGAY_DANG_TAI: response.xpath(XpathConstants.XPATH_GET_NGAY_DANG_TAI).get(),
            DocumentConstants.HINH_THUC_DAU_THAU: response.xpath(self.XPATH_GET_HINH_THUC_DAU_THAU).get(),
            DocumentConstants.LINH_VUC: category_value,
            DocumentConstants.THONG_TIN_CHI_TIET:
                SpiderUtils.parse_a_table_with_one_attach_file_last(response,
                                                                    self.XPATH_GET_ALL_THONG_TIN_CHI_TIET,
                                                                    self.DINH_KEM_THONG_BAO),
            DocumentConstants.KET_QUA:
                SpiderUtils.parse_a_table_with_out_attach_file(response,
                                                               self.XPATH_EXTRACT_KET_QUA),
            DocumentConstants.MO_TA_TOM_TAT_GOI_THAU:
                SpiderUtils.parse_a_complex_table_with_out_attach_file(response,
                                                                       self.XPATH_EXTRACT_MO_TA_TOM_TAT_GOI_THAU),
            DocumentConstants.CAC_NHA_THAU_TRUNG_THAU_KHAC: self.parse_co_winning_table(response)
        }

    def parse_co_winning_table(self, response):
        res = []
        result_list = response.xpath(self.XPATH_EXTRACT_CO_WINNING).extract()
        if len(result_list) == 0:
            return []
        cost = response.xpath(self.XPATH_EXTRACT_GIA_GOI_THAU).extract()
        cost_index = 0
        for index in range(0, len(result_list)):
            result = result_list[index].strip()
            if result == DocumentConstants.TEN_NHA_THAU:
                res.append({
                    DocumentConstants.TEN_NHA_THAU: result_list[index + 1].strip(),
                    DocumentConstants.GIA_GOI_THAU: cost[cost_index].strip()
                })
                cost_index += 1
        return res
