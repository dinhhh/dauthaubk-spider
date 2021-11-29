import scrapy
import logging
from .spider_constants import DocumentConstants

class ContractorSpider(scrapy.Spider):
    name = "contractor_spider"
    collection_name = "contractors"
    first_key = "Thông tin chung"
    second_key = "Số ĐKKD"

    FROM_PAGE = 1
    TO_PAGE = 5000
    THONG_TIN_CHUNG = "THÔNG TIN CHUNG"
    THONG_TIN_NGANH_NGHE = "THÔNG TIN NGÀNH NGHỀ"
    XPATH_GET_THONG_TIN_CHUNG = "//h3[text() = '{}']/following-sibling::div/div/div/table/tr/td"
    XPATH_GET_THONG_TIN_NGANH_NGHE = "//h3[text() = '{}']/following-sibling::div/table/tbody/tr/td"
    GET_TEXT = "text()"
    CSS_GET_CONTRACTOR_LINKS = "strong.color-3 a::attr(href)"
    page_counter = 0
    start_urls = []

    def __init__(self):
        url = 'http://muasamcong.mpi.gov.vn/danh-sach-nha-thau-uoc-phe-duyet?p_auth=Ee1XhBk6wo&p_p_id' \
              '=nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg&p_p_lifecycle=1&p_p_state=normal' \
              '&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2' \
              '&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_tenNhaThau' \
              '=&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_soDkkd' \
              '=&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_denNgay' \
              '=&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_nhaThau=0' \
              '&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_tuNgay' \
              '=&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_date2' \
              '=&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_currentPage={' \
              '}&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_thanhPho=0' \
              '&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_displayItem=10' \
              '&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_date1' \
              '=&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_javax.portlet.action=list '

        for i in range(self.FROM_PAGE, self.TO_PAGE + 1):
            self.start_urls.append(url.format(i))

    def parse(self, response):
        logging.debug('response url: ' + response.url)
        yield scrapy.Request(response.url, callback=self.parse_a_page)

    def parse_a_page(self, response):
        contractor_links = response.css(self.CSS_GET_CONTRACTOR_LINKS).getall()
        logging.info('parsing a page has {} contractors'.format(len(contractor_links)))
        for link in contractor_links:
            yield scrapy.Request(link, callback=self.parse_a_contractor)

    def parse_a_contractor(self, response):
        general_info_xpath = response.xpath(self.XPATH_GET_THONG_TIN_CHUNG.format(self.THONG_TIN_CHUNG))
        job_info_xpath = response.xpath(self.XPATH_GET_THONG_TIN_NGANH_NGHE.format(self.THONG_TIN_NGANH_NGHE))
        general_info = {}
        job_info = []

        # get general information of contractor
        if len(general_info_xpath) % 2 == 1:
            logging.debug("GENERAL INFO is odd number")
        for index in range(0, len(general_info_xpath), 2):
            key = general_info_xpath[index].xpath(self.GET_TEXT).get()
            value = general_info_xpath[index + 1].xpath(self.GET_TEXT).extract()
            general_info[key.strip()] = value[0].strip() if len(value) != 0 else ''

        # get job information of contractor
        for index in range(1, len(job_info_xpath), 2):
            job = job_info_xpath[index].xpath(self.GET_TEXT).get()
            job_info.append(job)

        yield {
            DocumentConstants.THONG_TIN_CHUNG: general_info,
            DocumentConstants.THONG_TIN_NGANH_NGHE: job_info
        }
