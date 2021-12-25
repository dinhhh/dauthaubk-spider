import pymongo
import json

client = pymongo.MongoClient("mongodb+srv://dinhhh:IhMxVdQkr7rrDj4f@dauthau-bk.cqscj.mongodb.net/DauThau-BK?retryWrites=true&w=majority")
db = client["DauThau-BK"]
query = {"Thông tin chi tiết.Hình thức thông báo": "Thông báo đã bị hủy"}
documents = db.contractorHistory.find(query)
for doc in documents:
    print(doc)
