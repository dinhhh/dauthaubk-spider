import scrapy
import logging
from .spider_constants import DocumentConstants

class InvestorSpider(scrapy.Spider):
    name = "investors_spider"
    start_urls = []
    # for update database
    collection_name = "investors"
    first_key = "Thông tin chung"
    second_key = "Mã cơ quan"

    MA_CO_QUAN = "Mã cơ quan"
    FROM_PAGE = 1
    TO_PAGE = 10
    TITLE = "THÔNG TIN CƠ QUAN"
    GET_INVESTOR_LINKS = "//a[@class = 'container-tittle color-0086D7 font-roboto-regular']/@href"
    GET_GENERAL_INFO = "//h3[text() = '{}']/following-sibling::div/div/div/table/tr/td".format(TITLE)
    GET_TEXT = "text()"

    def __init__(self):
        url = "http://muasamcong.mpi.gov.vn/danh-sach-ben-moi-thau?p_auth=hyxiiKQ8En&p_p_id" \
              "=benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view" \
              "&p_p_col_id=column-1&p_p_col_count=2&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_boBanNganh" \
              "=0&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_maCoQuan" \
              "=&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_denNgay" \
              "=&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_tuNgay" \
              "=&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_tapDoan=0" \
              "&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_searchText" \
              "=&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_currentPage={" \
              "}&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_thanhPho=0" \
              "&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_displayItem=10" \
              "&_benmoithau_WAR_resourcesportlet_INSTANCE_hSJpefpjz7tb_javax.portlet.action=list "
        for i in range(self.FROM_PAGE, self.TO_PAGE + 1):
            self.start_urls.append(url.format(i))

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.parse_one_page)

    def parse_one_page(self, response):
        investor_links = response.xpath(self.GET_INVESTOR_LINKS).extract()
        logging.info("parsing a page has {} investors".format(len(investor_links)))
        for link in investor_links:
            yield scrapy.Request(url=link, callback=self.parse_a_investor)

    def parse_a_investor(self, response):
        logging.info("parsing a investor at link {}".format(response.url))
        general_info_xpath = response.xpath(self.GET_GENERAL_INFO)
        general_info = {}
        for index in range(0, len(general_info_xpath), 2):
            key = general_info_xpath[index].xpath(self.GET_TEXT).get().strip()
            value = general_info_xpath[index + 1].xpath(self.GET_TEXT).extract()
            general_info[key] = value[0].strip() if len(value) != 0 else ''
        yield {
            DocumentConstants.THONG_TIN_CHUNG: general_info
        }
