import motor.motor_asyncio
import pymongo
from pymongo.collection import Collection

from yarapi.config import config

client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_url)
pymongo_client = pymongo.MongoClient(config.mongo_url)


class BaseCollection:
    _collection: motor.motor_asyncio.AsyncIOMotorCollection
    _pymongo_collection: Collection

    def __init__(self, db_name: str, collection: str) -> None:
        self._collection = client[db_name][collection]
        self._pymongo_collection = pymongo_client[db_name][collection]

    def _ensure_indexes(self):
        raise NotImplementedError

    @property
    def objects(self):
        return self._collection

    @property
    def objects_sync(self):
        return self._pymongo_collection


class UsersCollection(BaseCollection):
    def _ensure_indexes(self):
        self._pymongo_collection.create_index("username", unique=True)

    def __init__(self):
        super().__init__("olho_gordo", "users")
        self._ensure_indexes()


users_collection = UsersCollection()
