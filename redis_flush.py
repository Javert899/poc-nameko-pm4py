from poc_config import *
import redis


database = redis.Redis(OBJECT_DATAFRAME_HOSTNAME, db=OBJECT_DATAFRAME_ID)
registry = redis.Redis(REGISTRY_DATAFRAME_HOSTNAME, db=REGISTRY_DATAFRAME_ID)

database.flushdb()
registry.flushdb()
