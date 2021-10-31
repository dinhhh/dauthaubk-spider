import scrapy

class ContractorSpider(scrapy.Spider):
    name = "contractor_spider"

    start_urls = [
        "http://muasamcong.mpi.gov.vn/danh-sach-nha-thau-uoc-phe-duyet?p_auth=eedlpx9wK3&p_p_id=nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_id=132590&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_name=cong-ty-trach-nhiem-huu-han-mot-thanh-vien-giang-doan&_nhathauduocpheduyet_WAR_resourcesportlet_INSTANCE_CgxbQgdVGxlg_javax.portlet.action=detail"
                  ]

    # get general information of contractor
    # response.xpath("//h3[text() = 'THÔNG TIN CHUNG']/following-sibling::div/div/div/table/tr/td/text()").extract()

    # get empty field in td tag
    # for info in response.xpath("//h3[text() = 'THÔNG TIN CHUNG']/following-sibling::div/div/div/table/tr/td"):
    #     print(info.xpath('text()').extract())

    def parse(self, response):
        result = {}
        general_info = response.xpath("//h3[text() = 'THÔNG TIN CHUNG']/following-sibling::div/div/div/table/tr/td")
        for index in range(0, len(general_info), 2):
            key = general_info[index].xpath('text()').get()
            value = general_info[index + 1].xpath('text()').extract()
            if len(value) != 0:
                print("{}: {}".format(key, value[0]))
            result[key] = value[0] if len(value) != 0 else ''
        yield result
