# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
import logging
from .spiders.contractor_bidding_result import AwardResultSpider
from .spiders.spider_constants import DocumentConstants, CollectionConstants
from .spiders.contractor_online_bidding_result import OnlineBidOpeningResultSpider

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
        if spider.name == OnlineBidOpeningResultSpider.name:
            logging.info("Start update contractor history...")
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
                self.db[CollectionConstants.CONTRACTOR_HISTORY].update(
                    {DocumentConstants.TEN_NHA_THAU: name},
                    {"$addToSet": {DocumentConstants.GOI_THAU_DA_THAM_GIA: bid_info}},
                    upsert=True
                )
