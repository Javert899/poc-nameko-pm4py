import json
import time
import uuid
from threading import Thread

import redis
from nameko.rpc import rpc
from poc_config import *

import pm4py

database = redis.Redis(OBJECT_DATAFRAME_HOSTNAME, db=OBJECT_DATAFRAME_ID)
registry = redis.Redis(REGISTRY_DATAFRAME_HOSTNAME, db=REGISTRY_DATAFRAME_ID)


class ImportingLog(object):
    name = "import_log"

    @rpc
    def import_log(self, path):
        log = pm4py.read_xes(path)
        log = pm4py.objects.log.exporter.xes.variants.etree_xes_exp.export_log_as_string(log)
        target_key = str(uuid.uuid4())
        database.set(target_key, log)
        database.set(target_key + "_type", "EventLog")
        return target_key

    @rpc
    def get_log_string(self, log_key):
        log = database.get(log_key).decode("utf-8")
        return log


class ServiceRegister(Thread):
    def __init__(self):
        self.registry = redis.Redis("localhost", db=1)
        Thread.__init__(self)

    def run(self):
        while True:
            self.registry.set("import_log.import_log",
                              json.dumps({"inputs": {"path": "str"}, "outputs": {"target_key": "EventLog"}}))
            self.registry.expire("import_log.import_log", 20)
            self.registry.set("import_log.get_log_string",
                              json.dumps({"inputs": {"log_key": "EventLog"}, "outputs": {"log_content": "str"}}))
            self.registry.expire("import_log.get_log_string", 20)
            time.sleep(10)


s = ServiceRegister()
s.start()
