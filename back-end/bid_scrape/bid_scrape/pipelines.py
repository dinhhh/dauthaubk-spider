# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
import ssl
from pathlib import Path
import logging
from .spiders.contractor_bidding_result import AwardResultSpider
from .spiders.spider_constants import DocumentConstants, CollectionConstants
from .spiders.contractor_online_bidding_result import OnlineBidOpeningResultSpider
from .spiders.spider_utils import SpiderUtils
import json
import os
import requests

API_USER_BROADCAST = "localhost:5000/api/user/broadcast"


class BidScrapePipeline:
    def process_item(self, item, spider):
        return item


def build_contractor_history_item(item):
    brief_description = []
    if item.get(DocumentConstants.MO_TA_TOM_TAT_GOI_THAU) is not None:
        for des in item.get(DocumentConstants.MO_TA_TOM_TAT_GOI_THAU):
            brief_description.append({
                DocumentConstants.TEN_HANG_HOA: des.get(DocumentConstants.TEN_HANG_HOA, ""),
                DocumentConstants.SO_LUONG: des.get(DocumentConstants.SO_LUONG, ""),
                DocumentConstants.XUAT_XU: des.get(DocumentConstants.XUAT_XU, ""),
                DocumentConstants.GIA_DON_GIA_TRUNG_THAU: des.get(DocumentConstants.GIA_DON_GIA_TRUNG_THAU, "")
            })
    spec_info = item.get(DocumentConstants.THONG_TIN_CHI_TIET, {})
    add_to_set_item = {
        DocumentConstants.SO_HIEU_KHLCNT: spec_info.get(DocumentConstants.SO_HIEU_KHLCNT, ""),
        DocumentConstants.TEN_GOI_THAU: spec_info.get(DocumentConstants.TEN_GOI_THAU, ""),
        DocumentConstants.TEN_DU_AN_DU_TOAN_MUA_SAM: spec_info.get(DocumentConstants.TEN_DU_AN_DU_TOAN_MUA_SAM, ""),
        DocumentConstants.BEN_MOI_THAU: spec_info.get(DocumentConstants.BEN_MOI_THAU, ""),
        DocumentConstants.NGAY_PHE_DUYET: item.get(DocumentConstants.NGAY_PHE_DUYET, ""),
        DocumentConstants.LINH_VUC: item.get(DocumentConstants.LINH_VUC, ""),
        DocumentConstants.KET_QUA: DocumentConstants.TRUNG_THAU,
        DocumentConstants.GIA_GOI_THAU: spec_info.get(DocumentConstants.GIA_GOI_THAU, ""),
        DocumentConstants.DONG_TRUNG_THAU: item.get(DocumentConstants.CAC_NHA_THAU_TRUNG_THAU_KHAC, ""),
        DocumentConstants.MO_TA_TOM_TAT_GOI_THAU: brief_description
    }
    return add_to_set_item


def build_bid_info(item):
    spec_info = item.get(DocumentConstants.THONG_TIN_CHI_TIET, {})
    if not bool(spec_info):
        return {}
    return {
        DocumentConstants.SO_TBMT: spec_info.get(DocumentConstants.SO_TBMT, ""),
        DocumentConstants.TEN_GOI_THAU: spec_info.get(DocumentConstants.TEN_GOI_THAU, ""),
        DocumentConstants.TEN_DU_AN_DU_TOAN_MUA_SAM: spec_info.get(DocumentConstants.TEN_DU_AN_DU_TOAN_MUA_SAM, ""),
        DocumentConstants.BEN_MOI_THAU: spec_info.get(DocumentConstants.BEN_MOI_THAU, ""),
        DocumentConstants.NGAY_PHE_DUYET: spec_info.get(DocumentConstants.NGAY_PHE_DUYET, ""),
        DocumentConstants.LINH_VUC: spec_info.get(DocumentConstants.LINH_VUC, ""),
        DocumentConstants.KET_QUA: DocumentConstants.TRUNG_THAU,
        DocumentConstants.GIA_GOI_THAU: spec_info.get(DocumentConstants.GIA_GOI_THAU, "")
    }

class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        # self.client = pymongo.MongoClient(self.mongo_uri)  # for linux
        self.client = pymongo.MongoClient(self.mongo_uri, ssl_cert_reqs=ssl.CERT_NONE)  # for window
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if spider.first_key is not None and spider.second_key is not None and spider.collection_name is not None:
            logging.info("Spider pipeline processing")
            filter_key = "{}.{}".format(spider.first_key, spider.second_key)
            filter_value = item.get(spider.first_key, {}).get(spider.second_key)
            logging.info("filter key: {}, filter value: {}".format(filter_key, filter_value))
            update_result = self.db[spider.collection_name].replace_one(
                filter={filter_key: filter_value},
                replacement=item,
                upsert=True
            )
            logging.info("Matched count: {}, modified count: {}"
                         .format(update_result.matched_count, update_result.modified_count))
            self.save_to_json_file(item=item, spider=spider)
            response = requests.post(API_USER_BROADCAST,
                                     json={'collection': spider.collection_name,
                                           'item': item})
        else:
            raise Exception("[Spider exception] Collection name, filter key, first key or second key is None")

        if spider.name == AwardResultSpider.name:
            self.update_contractor_history_collection(item)

        if spider.name == OnlineBidOpeningResultSpider.name:
            self.update_contractor_history_with_online_bidding(item)

    def save_to_json_file(self, item, spider):
        file_name = SpiderUtils.get_current_time() + '.json'
        logging.info(f"Saving into file {file_name}")

        try:
            with open(file_name, 'a', encoding='utf8') as file:
                self.truncate_utf8_chars(filename=file_name, count=1)
                if os.path.getsize(file_name) > 0:
                    file.write(",")
                else:
                    file.write("[")
                json.dump(item, file, ensure_ascii=False)
                file.write("]")

        except IOError:
            with open(file_name, 'w', encoding='utf8') as file:
                file.write("[")
                json.dump(item, file, ensure_ascii=False)
                file.write("]")


    def update_contractor_history_with_online_bidding(self, item):
        logging.info("Start update contractor history... with item {}".format(item))
        if len(item.get(DocumentConstants.KET_QUA, [])) == 0:
            raise Exception("[Spider exception] Bidding result doesn't have result")
        contractors_name = [c.get(DocumentConstants.TEN_NHA_THAU) for c in item.get(DocumentConstants.KET_QUA, [])]
        bid_info = build_bid_info(item=item)
        logging.info("Add to set in online bid result pipeline")
        for name in contractors_name:
            logging.info("name: {}".format(name))
            index = contractors_name.index(name)
            result = item.get(DocumentConstants.KET_QUA, [])
            if len(result) < 1:
                break
            bid_info[DocumentConstants.GIA_DU_THAU] = result[index].get(DocumentConstants.GIA_DU_THAU, "")
            bid_info[DocumentConstants.GIA_DU_THAU_SAU_GIAM_GIA] = result[index].get(
                DocumentConstants.GIA_DU_THAU_SAU_GIAM_GIA, "")
            bid_info[DocumentConstants.BAO_DAM_DU_THAU] = result[index].get(
                DocumentConstants.BAO_DAM_DU_THAU, "")

            co_winning = []
            for co_winning_name in list(filter(lambda c: c != name, contractors_name)):
                co_winning.append({
                    DocumentConstants.TEN_NHA_THAU: co_winning_name,
                    DocumentConstants.GIA_GOI_THAU: ""
                })
            bid_info[DocumentConstants.CAC_NHA_THAU_TRUNG_THAU_KHAC] = co_winning
            logging.info("Adding item {}".format(bid_info))
            self.db[CollectionConstants.ONLINE_BIDDING_OPEN_RESULT].update(
                {DocumentConstants.TEN_NHA_THAU: name},
                {"$addToSet": {DocumentConstants.GOI_THAU_DA_THAM_GIA: bid_info}},
                upsert=True
            )

    def update_contractor_history_collection(self, item):
        logging.info("Start update contractor history...")
        contractor_name = item.get(DocumentConstants.KET_QUA, {}). \
            get(DocumentConstants.NHA_THAU_TRUNG_THAU)
        if contractor_name is None:
            raise Exception("[Spider exception] Bidding result doesn't have result")
        add_to_set_item = build_contractor_history_item(item)
        # Xét trường hợp gói thầu update -> ko cần insert vào database
        query = {'Gói thầu đã tham gia.Số hiệu KHLCNT': add_to_set_item[DocumentConstants.SO_HIEU_KHLCNT]}
        exist_contractor = self.db[CollectionConstants.CONTRACTOR_HISTORY].find(query)
        if len(list(exist_contractor)) > 0:
            # Gói thầu đã được thêm vào lịch sử của nhà thầu
            logging.info("This bidding result already exist with contractor history {}")
            for exist in exist_contractor:
                print(exist)
        else:
            self.db[CollectionConstants.CONTRACTOR_HISTORY].update(
                {DocumentConstants.TEN_NHA_THAU: contractor_name},
                {"$addToSet": {DocumentConstants.GOI_THAU_DA_THAM_GIA: add_to_set_item}},
                upsert=True
            )


    def truncate_utf8_chars(self, filename, count, ignore_newlines=True):
        with open(filename, 'rb+') as f:
            last_char = None

            size = os.fstat(f.fileno()).st_size

            offset = 1
            chars = 0
            while offset <= size:
                f.seek(-offset, os.SEEK_END)
                b = ord(f.read(1))

                if ignore_newlines:
                    if b == 0x0D or b == 0x0A:
                        offset += 1
                        continue

                if b & 0b10000000 == 0 or b & 0b11000000 == 0b11000000:
                    # This is the first byte of a UTF8 character
                    chars += 1
                    if chars == count:
                        # When `count` number of characters have been found, move current position back
                        # with one byte (to include the byte just checked) and truncate the file
                        f.seek(-1, os.SEEK_CUR)
                        f.truncate()
                        return
                offset += 1
