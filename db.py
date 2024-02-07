from pymongo.mongo_client import MongoClient
from settings import config
from datetime import datetime, timezone, timedelta
from enum import Enum

Period = Enum('Period', ['DAY','WEEK', 'MONTH', 'YEAR', 'ALL'])


class Db():

    def __init__(self) -> None:
        self.client = MongoClient(config.mongo_uri)
        self.db = self.client[config.db]

    def get_categories(self, user_id: int) -> dict:
        coll = self.db.categories
        cats = coll.find({'user_id': user_id})
        return { str(cat['_id']): cat['name'] for cat in cats } 

    def add_category(self, cat_name: str, user_id: int) -> None:
        rec = {
                'user_id': user_id,
                'name': cat_name 
        }
        self.db['categories'].insert_one(rec)
    
    def add_record(self, cat_name: str, user_id: int, amnt: int ) -> None:
        rec = {
            'user_id': user_id,
            'cat_name': cat_name,
            'date': datetime.now(), #(tz=timezone.utc),
            'amnt': amnt
        }
        self.db['records'].insert_one(rec)
       
    def delete_category(self, user_id: int, cat_name: str) -> bool:
        # delete all records
        self.db['records'].delete_many({'user_id':user_id, 'cat_name':cat_name })
        
        # delete category itself
        deleted = True
        res = self.db['categories'].delete_one({'user_id':user_id,'name': cat_name })
        if res.deleted_count == 0:
            deleted = False
            
        return deleted
    
    def get_stats( self, period: Period, user_id: int, detailed: bool = False ) -> list:
        pipeline = []
        
        match period:
            case Period.DAY:
                start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                pipeline = [
                    {
                        "$match": {
                            "date": {"$gte": start_of_day},
                            "user_id": {"$eq": user_id } 
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "totalValue": {"$sum": "$amnt"}
                        }
                    }
                ]
            
                if detailed:
                    pipeline[1]["$group"]["_id"] = {"cat_name":"$cat_name"}
                

            case Period.WEEK:
                current_date = datetime.now()
                start_of_week = (current_date - timedelta(days=current_date.weekday()) ).replace(hour=0, minute=0, second=0, microsecond=0)
                pipeline = [
                    {
                        "$match": {
                            "date": {"$gte": start_of_week},
                            "user_id": {"$eq": user_id } 
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "totalValue": {"$sum": "$amnt"}
                        }
                    }
                ]
                if detailed:
                    pipeline[1]["$group"]["_id"] = {"cat_name":"$cat_name"}
                    
            case Period.MONTH:
                start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                pipeline = [
                    {
                        "$match": {
                            "date": {"$gte": start_of_month},
                            "user_id": {"$eq": user_id } 
                        }
                    },
                    {
                        "$group": {
                            "_id": {
                                "year": {"$year": "$date"},
                                "month": {"$month": "$date"}
                            }, 
                            "totalValue": {"$sum": "$amnt"}
                        }
                    }
                ]
                if detailed:
                    pipeline[1]["$group"]["_id"]["cat_name"] = "$cat_name"  
            
            case Period.YEAR:
                current_year = datetime.utcnow().year
                pipeline = [
                    {
                        "$match": {
                            "date": {"$gte": datetime(current_year, 1, 1), "$lt": datetime(current_year + 1, 1, 1)},
                            "user_id": {"$eq": user_id} 
                        }
                    },
                    {
                        "$group": {
                            "_id": {
                                "year": {"$year": "$date"},
                                "month": {"$month": "$date"}
                            },
                            "totalValue": {"$sum": "$amnt"}
                        }
                    }
                ]
                pipeline[1]["$group"]["_id"]["cat_name"] = "$cat_name"  
                
                
            case Period.ALL:
                pipeline = [
                    {
                        "$match": {
                            "user_id": {"$eq": user_id} 
                        }
                    },
                    {
                        "$group": {
                            "_id": {
                                "year": {"$year": "$date"},
                                "month": {"$month": "$date"}
                            },
                            "totalValue": {"$sum": "$amnt"}
                        }
                    }
                ]
                pipeline[1]["$group"]["_id"]["cat_name"] = "$cat_name"  
        
        result = list(self.db['records'].aggregate(pipeline))
        return result

db = Db()
