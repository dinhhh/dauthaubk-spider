# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
import logging
from .spiders.bidding_result_spider import AwardResultSpider
from .spiders.spider_constants import DocumentConstants, CollectionConstants

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
        self.client = pymongo.MongoClient(self.mongo_uri)
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
        else:
            raise Exception("[Spider exception] Collection name, filter key, first key or second key is None")

        if spider.name == AwardResultSpider.name:
            logging.info("Start update contractor history...")
            contractor_name = item.get(DocumentConstants.KET_QUA, {}).\
                get(DocumentConstants.NHA_THAU_TRUNG_THAU)
            if contractor_name is None:
                raise Exception("[Spider exception] Bidding result doesn't have result")
            add_to_set_item = build_contractor_history_item(item)
            self.db[CollectionConstants.CONTRACTOR_HISTORY].update(
                {DocumentConstants.TEN_NHA_THAU: contractor_name},
                {"$addToSet": {DocumentConstants.GOI_THAU_DA_THAM_GIA: add_to_set_item}},
                upsert=True
            )