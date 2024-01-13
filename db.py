from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from settings import config
from datetime import datetime, timezone

class Db():

    def __init__(self) -> None:
        self.client = MongoClient(config.mongo_uri)
        self.db = self.client[config.db]

    def get_categories(self, user_id: int) -> dict:
        coll = self.db.categories
        cats = coll.find({'user_id': user_id})
        return { str(cat['_id']): cat['name'] for cat in cats } 

    def add_category(self, cat_name: str, user_id: int) -> bool:
        if self.db['categories'].find_one({"name":cat_name}):
            return False
        
        else:
            rec = {
                'user_id': user_id,
                'name': cat_name 
            }
            self.db['categories'].insert_one(rec)
            # вернуть бул
    
    def add_record(self, cat_id: str, user_id: int, amnt: int ) -> bool:
        rec = {
            'userid': user_id,
            'catid': cat_id,
            'date': datetime.now(tz=timezone.utc),
            'amnt': amnt
        }
        self.db['records'].insert_one(rec)
        # вернуть бул
        
    def delete_category(self, cat_id: str) -> bool:
        # delete all records
        self.db['records'].delete_many({'catid':cat_id })
        
        # delete category itself
        deleted = True
        res = self.db['categories'].delete_one({'_id': ObjectId(cat_id) })
        if res.deleted_count == 0:
            deleted = False
            
        return deleted
    
    def get_stats( period: enumerate, detailes: bool = False ) -> str:
        pass
    
    

db = Db()