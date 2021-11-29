import scrapy
from .spider_constants import DocumentConstants, XpathConstants
from .spider_utils import SpiderUtils

class InvitationBidSpider(scrapy.Spider):
    name = "pre_qualification_result_spider"
    start_urls = []
    first_key = "Thông tin chi tiết"
    second_key = "Số TBMST"
    collection_name = "preQualificationResults"
    FROM_PAGE = 1
    TO_PAGE = 10

    XPATH_EXTRACT_RESULT_LINKS = "//strong[@class = 'text-up color-1 ellipsis-content-1row']/a[@class = " \
                                 "'container-tittle']/@href "

    def __init__(self):
        url = "http://muasamcong.mpi.gov.vn/lua-chon-nha-thau?p_auth=CuAKQjjjiE&p_p_id=luachonnhathau_WAR_bidportlet" \
              "&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2" \
              "&_luachonnhathau_WAR_bidportlet_timKiemTheo=1&_luachonnhathau_WAR_bidportlet_time=0" \
              "&_luachonnhathau_WAR_bidportlet_benMoiThau=&_luachonnhathau_WAR_bidportlet_denNgay" \
              "=&_luachonnhathau_WAR_bidportlet_tuNgay=&_luachonnhathau_WAR_bidportlet_loaiThongTin=6" \
              "&_luachonnhathau_WAR_bidportlet_searchText=&_luachonnhathau_WAR_bidportlet_sapXep=DESC" \
              "&_luachonnhathau_WAR_bidportlet_currentPage={}&_luachonnhathau_WAR_bidportlet_dongMo=0" \
              "&_luachonnhathau_WAR_bidportlet_nguonVon=1&_luachonnhathau_WAR_bidportlet_hinhThuc=1" \
              "&_luachonnhathau_WAR_bidportlet_displayItem=10&_luachonnhathau_WAR_bidportlet_linhVuc=-1" \
              "&_luachonnhathau_WAR_bidportlet_javax.portlet.action=list "
        for i in range(self.FROM_PAGE, self.TO_PAGE + 1):
            self.start_urls.append(url.format(i))

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


