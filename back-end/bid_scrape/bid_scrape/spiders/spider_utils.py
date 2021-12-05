import logging
from .spider_constants import XpathConstants, DocumentConstants, JavaScriptConstants
import yaml

class SpiderUtils:
    LOGGING_TAG = "[Spider Utils]"

    @staticmethod
    def init_attribute(spider_name):
        """ Return order: start_urls, from_page, to_page, first_key, second_key, collection_name """
        from pathlib import Path
        my_path = Path(__file__).resolve()  # resolve to get rid of any symlinks
        config_path = my_path.parent / 'config.yaml'
        with config_path.open() as c:
            config = yaml.safe_load(c)
        from_page = config[spider_name]["from_page"]
        to_page = config[spider_name]["to_page"]
        first_key = config[spider_name]["first_key"]
        second_key = config[spider_name]["second_key"]
        collection_name = config[spider_name]["collection_name"]
        start_urls = []
        base_url = config[spider_name]["base_url"]
        for i in range(from_page, to_page + 1):
            start_urls.append(base_url.format(i))
        logging.info(SpiderUtils.LOGGING_TAG + "base_url {} from_page {} to_page {} first_key {} second_key {} "
                                               "collection_name {}".format(base_url, from_page, to_page, first_key,
                                                                           second_key, collection_name))
        return start_urls, first_key, second_key, collection_name

    @staticmethod
    def parse_a_table_with_out_attach_file(response, xpath_extract_table):
        #  xpath sample: "//div/div/table/tr/td//text()"
        result = {}
        result_list = SpiderUtils.remove_unwanted_character_in_string_list(
            response.xpath(xpath_extract_table).extract())
        if len(result_list) == 0:
            logging.info("URL: {} Contents of table are empty".format(response.url))
            return result
        for index in range(0, len(result_list), 2):
            key = result_list[index]
            if index + 1 > len(result_list) - 1:
                raise Exception(SpiderUtils.LOGGING_TAG + " Index {} out of range {}. result_list {}".
                                format(index, len(result_list), result_list))
            value = result_list[index + 1]
            result[key] = value
        return result

    @staticmethod
    def parse_a_complex_table_with_out_attach_file(response, xpath_extract_table):
        # xpath sample: "/div/table/tbody/tr/td"
        result = []
        removed_br_tag_response = response.replace(body=response.body.replace(b'<br>', b'\n'))
        column_name = SpiderUtils.get_column_name_by_xpath(removed_br_tag_response,
                                                           xpath_extract_table,
                                                           removed_br_tag=True)
        column_size = len(column_name)
        if column_size == 0:
            logging.info("Table of page {} is empty {}".format(response.url, xpath_extract_table))
            return result
        table_contents = removed_br_tag_response.xpath(xpath_extract_table)
        for row_index in range(column_size, len(table_contents), column_size):
            row = {}
            for column_index in range(column_size):
                key = column_name[column_index].strip().replace('\n', '')
                value = table_contents[row_index + column_index].xpath(XpathConstants.GET_TEXT).extract()
                row[key] = value[0].strip() if len(value) != 0 else ''
            result.append(row)
        return result

    @staticmethod
    def get_column_name_by_xpath(response, xpath_extract_table, removed_br_tag: bool):
        index = xpath_extract_table.index("tr") + 2
        new_xpath = xpath_extract_table[:index] + "[1]" + xpath_extract_table[index:]
        if not removed_br_tag:
            removed_br_tag_response = response.replace(body=response.body.replace(b'<br>', b'\n'))
            return removed_br_tag_response.xpath(new_xpath).xpath(XpathConstants.GET_TEXT).extract()
        return response.xpath(new_xpath).xpath(XpathConstants.GET_TEXT).extract()

    @staticmethod
    def parse_a_table_with_multi_attach_file(response, xpath_extract_table, attach_file_key, next_field_key,
                                             xpath_extract_document_names, xpath_extract_document_links,
                                             special_document_name=None, xpath_get_special_document_links=None):
        # xpath_extract_table sample: div/table/tr/td/text()
        result = {}
        result_list = SpiderUtils.remove_unwanted_character_in_string_list(
            response.xpath(xpath_extract_table).extract()
        )
        if len(result_list) == 0:
            logging.info("URL: {} Contents of table are empty".format(response.url))
            return result
        if special_document_name is not None and special_document_name in result_list:
            logging.info(SpiderUtils.LOGGING_TAG + " special document name is not NONE")
            result_list = SpiderUtils.remove_unwanted_string_in_list_with_value(result_list,
                                                                                attach_file_key,
                                                                                next_field_key)
            logging.info(SpiderUtils.LOGGING_TAG + " result_list here: {}".format(result_list))
            index_of_special_document = result_list.index(special_document_name) + 1
            if xpath_get_special_document_links is None:
                logging.info(SpiderUtils.LOGGING_TAG + " xpath get special link in url {} is None".format(response.url))
                result_list.insert(index_of_special_document, '')
            else:
                special_links = response.xpath(xpath_get_special_document_links).getall()
                result_list.insert(index_of_special_document, special_links)
        else:
            result_list = SpiderUtils.remove_empty_string_in_list_with_value(result_list,
                                                                             attach_file_key,
                                                                             next_field_key)
        result_list.insert(result_list.index(attach_file_key) + 1, '')
        logging.info(SpiderUtils.LOGGING_TAG + " result_list {} url {}".format(result_list, response.url))
        for index in range(0, len(result_list), 2):
            if result_list[index] != attach_file_key:
                key = result_list[index]
                if index + 1 > len(result_list) - 1:
                    raise Exception(SpiderUtils.LOGGING_TAG + " Index {} out of range {}. result_list {}".
                                    format(index, len(result_list), result_list))
                value = result_list[index + 1]
                result[key] = value
            else:
                key = attach_file_key
                value = SpiderUtils.parse_bidding_documents(response,
                                                            xpath_extract_document_names,
                                                            xpath_extract_document_links)
                result[key] = value
        return result

    @staticmethod
    def parse_a_table_with_multi_attach_files(response, xpath_get_tr_tag):
        # xpath sample: //span[text() = 'THÔNG TIN CHI TIẾT']/../following-sibling::div/div/div/table/tr
        trs = response.xpath(xpath_get_tr_tag).extract()
        result = {}
        if len(trs) < 1:
            logging.info(SpiderUtils.LOGGING_TAG + " Get table by xpath {} of page {} is empty".format(xpath_get_tr_tag,
                                                                                                       response.url))
            return result

        for i in range(1, len(trs) + 1):
            xpath_get_td = SpiderUtils.build_xpath_get_td_text(xpath_get_tr_tag, i)
            contents = response.xpath(xpath_get_td).extract()
            if len(contents) < 1:
                logging.error(
                    SpiderUtils.LOGGING_TAG + " cell {} haven't content in page {} xpath {} contents {}"
                    .format(i, response.url, xpath_get_tr_tag, contents))
                break
            title = contents[0].strip()
            if len(contents) == 2:
                result[title] = contents[1]
            elif len(contents) == 1:
                tags = ["/span", "/b"]
                result[title] = SpiderUtils.get_children_tag_text(response, xpath_get_td, tags)
            else:
                flag = title == DocumentConstants.THONG_BAO_LIEN_QUAN
                document_with_link = SpiderUtils.parse_a_cell_with_multi_attach_files(
                    response, xpath_get_tr_tag + "[{}]/td[2]".format(i), flag)
                result[title] = document_with_link
        return result

    @staticmethod
    def get_children_tag_text(response, xpath_get_td, children_tags):
        for tag in children_tags:
            xpath = xpath_get_td[0: -7] + tag + "/text()"
            texts = response.xpath(xpath).extract()
            if len(texts) == 1:
                return texts[0]
        return ""

    @staticmethod
    def parse_a_cell_with_multi_attach_files(response, xpath_get_td_tag, is_no_name=False):
        # xpath_get_td_tag sample: div/div/div/table/tr[3]/td[1]
        logging.info(SpiderUtils.LOGGING_TAG + " parse a cell in url {} xpath_get_td {} is_no_name {}"
                     .format(response.url, xpath_get_td_tag, is_no_name))
        if is_no_name:
            return SpiderUtils.parse_a_cell_with_multi_link_with_out_name(response, xpath_get_td_tag)
        result = []
        all_document_names = SpiderUtils.remove_empty_string_in_list(response.xpath(
            xpath_get_td_tag + "//text()").extract())
        document_names_with_link = SpiderUtils.remove_empty_string_in_list(
            response.xpath(xpath_get_td_tag + "/a/text()").extract())
        for name in all_document_names:
            if name not in document_names_with_link:
                result.append(SpiderUtils.get_document_name_with_link(name, ""))
            else:
                index = document_names_with_link.index(name)
                link = response.xpath(xpath_get_td_tag + "/a[{}]/@href".format(index)).get()
                result.append(SpiderUtils.get_document_name_with_link(name, link))
        return result

    @staticmethod
    def parse_a_cell_with_multi_link_with_out_name(response, xpath_get_td_tag):
        result = []
        links = response.xpath(xpath_get_td_tag + "/a/@href").extract()
        logging.info(SpiderUtils.LOGGING_TAG + " links with name {}".format(links))
        for link in links:
            result.append(SpiderUtils.get_document_name_with_link("", link))
        return result

    @staticmethod
    def get_document_name_with_link(name, link):
        if name is None:
            raise Exception(SpiderUtils.LOGGING_TAG + " document don't have name")
        document = {DocumentConstants.TEN_TAI_LIEU: name}
        if link is None or link == "":
            document[DocumentConstants.LINK] = ""
        else:
            document[DocumentConstants.LINK] = link
        return document

    @staticmethod
    def build_xpath_get_td_text(xpath_get_tr_tag, index):
        return xpath_get_tr_tag + "[" + str(index) + "]" + "/td/text()"

    @staticmethod
    def parse_a_table_with_one_attach_file_last(response, xpath_extract_table, attach_file_key):
        result = {}
        result_list = SpiderUtils.remove_unwanted_character_in_string_list(
            response.xpath(xpath_extract_table).extract())
        if len(result_list) == 0:
            logging.info("URL: {} Contents of table are empty".format(response.url))
            return result
        for index in range(0, len(result_list), 2):
            if result_list[index] != attach_file_key:
                key = result_list[index]
                value = result_list[index + 1]
                result[key] = value
            else:
                key = attach_file_key
                value = result_list[index: len(result_list)]
                result[key] = list(filter(lambda c: c.strip() != '' and c != attach_file_key, value))
                break
        return result

    @staticmethod
    def remove_unwanted_character_in_string_list(string_list):
        new_list = []
        for string in string_list:
            new_list.append(string.strip().replace('\n', ''))
        return new_list

    @staticmethod
    def remove_empty_string_in_list_with_index(string_list, left, right):
        if right > len(string_list):
            raise IndexError("Right > Len(String list)")
        result = string_list[0: left]
        for index in range(left, right + 1):
            if string_list[index] != '':
                result.append(string_list[index])
        result.extend(string_list[right + 1: len(string_list)])
        return result

    @staticmethod
    def remove_empty_string_in_list_with_value(string_list, left, right):
        if left not in string_list:
            if right not in string_list:
                raise Exception(SpiderUtils.LOGGING_TAG + " {} and {} not in {}".format(left, right, string_list))
            return SpiderUtils.remove_empty_string_in_list_with_index(string_list, 0, string_list.index(right))
        if right not in string_list:
            return SpiderUtils.remove_empty_string_in_list_with_index(string_list, string_list.index(left),
                                                                      len(string_list) - 1)
        if string_list.index(left) > string_list.index(right):
            logging.info(
                SpiderUtils.LOGGING_TAG + " index of {} > index of {} in list {}".format(left, right, string_list))
            left, right = right, left
        return SpiderUtils.remove_empty_string_in_list_with_index(string_list, string_list.index(left),
                                                                  string_list.index(right))

    @staticmethod
    def remove_unwanted_string_in_list_with_index(string_list, left, right):
        if right > len(string_list):
            raise IndexError("Right > Len(String list)")
        result = string_list[0: left]
        for index in range(left, right + 1):
            if string_list[index] != '' and string_list[index] != '[' and string_list[index] != ']':
                result.append(string_list[index])
        result.extend(string_list[right + 1: len(string_list)])
        return result

    @staticmethod
    def remove_unwanted_string_in_list_with_value(string_list, left, right):
        if left not in string_list:
            if right not in string_list:
                raise Exception(SpiderUtils.LOGGING_TAG + " {} and {} not in {}".format(left, right, string_list))
            return SpiderUtils.remove_unwanted_string_in_list_with_index(string_list, 0, string_list.index(right))
        if right not in string_list:
            return SpiderUtils.remove_unwanted_string_in_list_with_index(string_list, string_list.index(left),
                                                                         len(string_list) - 1)
        if string_list.index(left) > string_list.index(right):
            logging.info(
                SpiderUtils.LOGGING_TAG + " index of {} > index of {} in list {}".format(left, right, string_list))
            left, right = right, left
        return SpiderUtils.remove_unwanted_string_in_list_with_index(string_list, string_list.index(left),
                                                                     string_list.index(right))

    @staticmethod
    def remove_empty_string_in_list(string_list):
        new_list = SpiderUtils.remove_unwanted_character_in_string_list(string_list)
        return list(filter(lambda c: c != '', new_list))

    @staticmethod
    def get_index(value, string_list):
        #  return -1 if value not in string_list
        if len(string_list) < 1:
            return -1
        for string in string_list:
            if value == string:
                return string_list.index(string)
        return -1

    @staticmethod
    def parse_bidding_documents(response, xpath_extract_document_names, xpath_extract_document_links):
        #  xpath_extract_document_names sample: /div/table/tr/td
        #  xpath_extract_document_links sample: /div/table/tr/td/a//@href
        #  return [
        #       {name: Tai lieu 1, link: abc.edu.vn},
        #       {name: Tai lieu 2}
        #  ]
        links = SpiderUtils.remove_unwanted_character_in_string_list(
            response.xpath(xpath_extract_document_links).extract()
        )
        all_names = SpiderUtils.remove_empty_string_in_list(
            response.xpath(xpath_extract_document_names + XpathConstants.GET_ALL_CHILDREN_TEXT).extract()
        )
        names_with_link = SpiderUtils.remove_empty_string_in_list(
            response.xpath(
                xpath_extract_document_names + XpathConstants.GET_A_TAG + XpathConstants.GET_ALL_CHILDREN_TEXT
            ).extract()
        )
        result = []
        if len(all_names) != len(names_with_link):
            logging.info(SpiderUtils.LOGGING_TAG + " length of all names and names with link is different " +
                         " all_names: {}; names with link: {}".format(all_names, names_with_link))
        for name in all_names:
            temp = {DocumentConstants.TEN_TAI_LIEU: name}
            index = SpiderUtils.get_index(name, names_with_link)
            temp[DocumentConstants.LINK] = links[index] if index != -1 and links[index] != JavaScriptConstants.JS_VOID \
                else ""
            result.append(temp)
        return result

    @staticmethod
    def get_with_none_check(response, xpath):
        result = response.xpath(xpath).get()
        return result if result is not None else ""

    @staticmethod
    def extract_first_with_none_check(response, xpath):
        result = response.xpath(xpath).extract()
        return result[0] if result is not None and len(result) != 0 else ""
