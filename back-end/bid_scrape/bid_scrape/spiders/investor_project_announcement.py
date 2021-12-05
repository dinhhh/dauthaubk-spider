import scrapy
from .spider_utils import SpiderUtils
from .spider_constants import DocumentConstants, XpathConstants


class ProjectListingAnnouncementSpider(scrapy.Spider):
    # Công bố danh mục dự án
    name = "investor_project_listing_announcement"
    start_urls, first_key, second_key, collection_name = SpiderUtils.init_attribute(name)

    XPATH_EXTRACT_CATEGORY_WITH_INDEX = "//table/tbody/tr[{}]/td/p[text() = 'Loại dự án: ']/span/text()"
    XPATH_EXTRACT_FORM = "//table/tbody/tr[{}]/td[4]/a[1]/text()"

    def parse(self, response):
        links = response.xpath(XpathConstants.XPATH_GET_LINKS).extract()
        categories = [SpiderUtils.extract_first_with_none_check(response,
                self.XPATH_EXTRACT_CATEGORY_WITH_INDEX.format(2 * index)) for index in range(1, len(links) + 1)]
        forms = [SpiderUtils.extract_first_with_none_check(response, self.XPATH_EXTRACT_FORM.format(2 * index))
                for index in range(1, len(links) + 1)]
        for link, category, form in zip(links, categories, forms):
            request = scrapy.Request(link, callback=self.parse_a_page,
                                     cb_kwargs=dict(category_value=category, form_value=form))
            yield request

    def parse_a_page(self, response, category_value, form_value):
        yield {
            DocumentConstants.HAN_NOP_HO_SO_DANG_KY: response.xpath(XpathConstants.XPATH_GET_HAN_NOP_HO_SO_DANG_KY).get(),
            DocumentConstants.LOAI_DU_AN: category_value,
            DocumentConstants.HINH_THUC_DAU_THAU: form_value,
            DocumentConstants.THONG_TIN_CHI_TIET: SpiderUtils.parse_a_table_with_multi_attach_files(
                response=response,
                xpath_get_tr_tag=XpathConstants.XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET
            )
        }
