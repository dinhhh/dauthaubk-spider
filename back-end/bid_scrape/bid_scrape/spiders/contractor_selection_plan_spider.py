import scrapy
from .spider_constants import DocumentConstants

class ContractorSelectionPlanSpider(scrapy.Spider):
    name = "contractor_selection_plan"
    start_urls = []
    collection_name = "contractorSelectionPlans"
    first_key = "Thông tin chi tiết"
    second_key = "Số KHLCNT"

    FROM_PAGE = 1
    TO_PAGE = 100  # 14/11/2021: fetched first 200 pages of 10 plan (no log file)

    NGAY_DANG_TAI = "Ngày đăng tải"
    NGAY_PHE_DUYET = "Ngày phê duyệt"
    THONG_TIN_CHI_TIET = "THÔNG TIN CHI TIẾT"
    THAM_DU_THAU = "THAM DỰ THẦU"
    QUYET_DINH_PHE_DUYET = "Quyết định phê duyệt"
    GIA_GOI_THAU = "Giá gói thầu (VND)"

    XPATH_GET_NGAY_DANG_TAI = "//div[@class = 'bg-l1']/h3/text()"
    XPATH_GET_NGAY_PHE_DUYET = "//div[@class = 'bg-l2']/h3/text()"
    XPATH_GET_THONG_TIN_CHI_TIET = "//h2[@class = 'd-box-head-3']/following-sibling::div/div/div/table/tr/td"
    XPATH_GET_ATTACH_FILE = "//a[@class = 'showNotify']/text()"
    XPATH_GET_COLUMN_NAME = "//div[@class = 'col-sm-12']/div[@class = 'row tbl-internet']/table/tbody/tr[1]/td/text()"
    XPATH_GET_ALL_ROW_THAM_DU_THAU = "//div[@class = 'col-sm-12']/div[@class = 'row tbl-internet']/table/tbody/tr"
    XPATH_GET_ROW_THAM_DU_THAU_BY_INDEX = "//div[@class = 'col-sm-12']/div[@class = 'row " \
                                          "tbl-internet']/table/tbody/tr[{}]/td/text() "
    XPATH_GET_GIA_GOI_THAU = "//label/text()"
    XPATH_GET_PLAN_LINKS = "//strong[@class = 'text-up color-1 ellipsis-content-1row']/a/@href"
    XPATH_GET_NEXT_PAGE = "//li[@class ='active']/following-sibling::li[1]/a/@href"

    GET_TEXT = "text()"

    def __init__(self):
        url = "http://muasamcong.mpi.gov.vn/lua-chon-nha-thau?p_auth=MU4CklVCZI&p_p_id=luachonnhathau_WAR_bidportlet" \
              "&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2" \
              "&_luachonnhathau_WAR_bidportlet_timKiemTheo=1&_luachonnhathau_WAR_bidportlet_time=3" \
              "&_luachonnhathau_WAR_bidportlet_denNgay=14-11-2021&_luachonnhathau_WAR_bidportlet_tuNgay=14-05-2021" \
              "&_luachonnhathau_WAR_bidportlet_loaiThongTin=1&_luachonnhathau_WAR_bidportlet_searchText" \
              "=&_luachonnhathau_WAR_bidportlet_sapXep=DESC&_luachonnhathau_WAR_bidportlet_currentPage={}" \
              "&_luachonnhathau_WAR_bidportlet_dongMo=0&_luachonnhathau_WAR_bidportlet_displayItem=10" \
              "&_luachonnhathau_WAR_bidportlet_chuDauTu=&_luachonnhathau_WAR_bidportlet_javax.portlet.action=list"

        for i in range(self.FROM_PAGE, self.TO_PAGE + 1):
            self.start_urls.append(url.format(i))

    def parse(self, response):
        self.log('response url: ' + response.url)
        yield scrapy.Request(response.url, callback=self.parse_a_page)

    def parse_a_page(self, response):
        plan_links = response.xpath(self.XPATH_GET_PLAN_LINKS).getall()
        if plan_links is not None:
            for link in plan_links:
                yield scrapy.Request(link, callback=self.parse_a_plan)

    def parse_a_plan(self, response):
        # parse THONG_TIN_CHI_TIET
        spec_info = {}
        spec_info_xpath = response.xpath(self.XPATH_GET_THONG_TIN_CHI_TIET)
        for index in range(0, len(spec_info_xpath), 2):
            key = spec_info_xpath[index].xpath(self.GET_TEXT).get().strip()
            value = spec_info_xpath[index + 1].xpath(self.GET_TEXT).extract()  # return a list

            if key != self.QUYET_DINH_PHE_DUYET:  # if not get attach file name
                spec_info[key] = value[0].strip() if len(value) != 0 else ''
            else:  # if is attach file name
                spec_info[key] = []
                un_format_file_name = response.xpath(self.XPATH_GET_ATTACH_FILE).getall()
                for file_name in un_format_file_name:
                    if file_name.strip() != "":
                        spec_info[key].append(file_name.strip())

        # parse THAM_DU_THAU
        # get all GIA_GOI_THAU
        cost_per_package = response.xpath(self.XPATH_GET_GIA_GOI_THAU).extract()
        if len(cost_per_package) < 1:
            self.log("[error_when_parsing] {} bidding package has no cost value".format(response.url))

        package_info_list = []
        column_name = response.xpath(self.XPATH_GET_COLUMN_NAME).getall()
        num_col = len(column_name)
        num_row = len(response.xpath(self.XPATH_GET_ALL_ROW_THAM_DU_THAU))
        if num_row > 1:  # if so luong tham du thau > 0
            for index in range(2, num_row + 1):
                # return a row as list
                row_value = response.xpath(self.XPATH_GET_ROW_THAM_DU_THAU_BY_INDEX.format(index)).extract()
                temp = {}

                if len(row_value) + 1 != num_col:  # + 1 because cost of package is calculated independently
                    self.log("number of row {} not equal number of column {}".format(len(row_value), num_col))
                    self.log("column name: {} row value: {}".format(column_name, row_value))
                    continue

                for i in range(len(row_value)):
                    key = column_name[i]
                    if key == self.GIA_GOI_THAU:
                        continue
                    value = row_value[i].strip()
                    temp[key] = value

                temp[self.GIA_GOI_THAU] = cost_per_package[index - 2]
                package_info_list.append(temp)

        yield {
            DocumentConstants.NGAY_DANG_TAI: response.xpath(self.XPATH_GET_NGAY_DANG_TAI).get().strip()
            if response.xpath(self.XPATH_GET_NGAY_DANG_TAI).get() is not None else "",
            DocumentConstants.NGAY_PHE_DUYET: response.xpath(self.XPATH_GET_NGAY_PHE_DUYET).get().strip()
            if response.xpath(self.XPATH_GET_NGAY_PHE_DUYET).get() is not None else "",
            DocumentConstants.THONG_TIN_CHI_TIET: spec_info,
            DocumentConstants.THAM_DU_THAU: package_info_list
        }
