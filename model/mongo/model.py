from bson import ObjectId
from lib_config.mongodb.mongodb import get_mongo_database, BaseMongoModel


class ShopModel(BaseMongoModel):
    _fields = {
        'jd_type': (str, False), # default SOP, other FBP, LBP, SOPL, SS(京东自营)
    }

    def __init__(self, **kwargs):
        super().__init__(get_mongo_database("xdmp"), "shop", **kwargs)