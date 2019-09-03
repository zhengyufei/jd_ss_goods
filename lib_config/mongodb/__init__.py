from copy import deepcopy
from pymongo import ReadPreference


MONGODB = {}


def load_mongodb(mongos_conf):
    for db_name, _db_conf in mongos_conf.items():
        db_conf = deepcopy(_db_conf)
        read_preference = db_conf.get("read_preference")
        if read_preference == "primary":
            db_conf["read_preference"] = ReadPreference.PRIMARY
        elif read_preference == "primary_preferred":
            db_conf["read_preference"] = ReadPreference.PRIMARY_PREFERRED
        elif read_preference == "secondary":
            db_conf["read_preference"] = ReadPreference.SECONDARY
        else:
            db_conf["read_preference"] = ReadPreference.SECONDARY_PREFERRED
        MONGODB[db_name] = db_conf
