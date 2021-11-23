import logging
from .spider_constants import XpathConstants, DocumentConstants, JavaScriptConstants


class SpiderUtils:
    LOGGING_TAG = "[Spider Utils]"

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
        if special_document_name is not None:
            result_list = SpiderUtils.remove_unwanted_string_in_list_with_index(result_list,
                                                                                result_list.index(attach_file_key),
                                                                                result_list.index(next_field_key))
            if xpath_get_special_document_links is None:
                logging.info(SpiderUtils.LOGGING_TAG + " xpath get special link in url {} is None".format(response.url))
                result_list.insert(result_list.index(special_document_name) + 1, '')
            else:
                special_links = response.xpath(xpath_get_special_document_links).getall()
                result_list.insert(result_list.index(special_document_name) + 1, special_links)
        else:
            result_list = SpiderUtils.remove_empty_string_in_list_with_index(result_list,
                                                                             result_list.index(attach_file_key),
                                                                             result_list.index(next_field_key))
        result_list.insert(result_list.index(attach_file_key) + 1, '')
        logging.info(SpiderUtils.LOGGING_TAG + " result_list {} url {}".format(result_list, response.url))
        for index in range(0, len(result_list), 2):
            if result_list[index] != attach_file_key:
                key = result_list[index]
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
