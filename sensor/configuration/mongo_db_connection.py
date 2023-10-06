import pymongo
from sensor.constant.database import DATABASE_NAME
from sensor.constant.env_variable import MONGODB_URI_KEY
import certifi
import os
ca = certifi.where()

class MongoDBClient:
    client = None
    def __init__(self, database_name=DATABASE_NAME) -> None:
        try:

            if MongoDBClient.client is None:
                               
                mongo_db_url = "mongodb+srv://asm07:asm07@cluster0.l7j3weq.mongodb.net/"
                #mongo_db_url  = os.getenv(MONGODB_URI_KEY)
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
            self.client = MongoDBClient.client
            self.database = self.client[database_name]
            self.database_name = database_name
        except Exception as e:
            raise e