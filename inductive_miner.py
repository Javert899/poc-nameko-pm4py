import json
import tempfile
import time
import uuid
from threading import Thread

import pm4py
import redis
from nameko.rpc import rpc

from poc_config import *

database = redis.Redis(OBJECT_DATAFRAME_HOSTNAME, db=OBJECT_DATAFRAME_ID)
registry = redis.Redis(REGISTRY_DATAFRAME_HOSTNAME, db=REGISTRY_DATAFRAME_ID)


class InductiveMiner(object):
    name = "inductive_miner"

    @rpc
    def apply_inductive(self, log_key):
        log = database.get(log_key).decode("utf-8")
        temp_xes = tempfile.NamedTemporaryFile(suffix=".xes")
        temp_xes.close()
        F = open(temp_xes.name, "w")
        F.write(log)
        F.close()
        log = pm4py.objects.log.importer.xes.importer.apply(temp_xes.name)
        net, im, fm = pm4py.algo.discovery.inductive.algorithm.apply(log)
        net_string = pm4py.objects.petri.exporter.variants.pnml.export_petri_as_string(net, im, fm)
        model_key = str(uuid.uuid4())
        database.set(model_key, net_string)
        database.set(model_key + "_type", "AcceptingPetriNet")
        database.set(model_key + "_name", "Petri Net Discovered by Inductive Miner")
        return model_key


class ServiceRegister(Thread):
    def __init__(self):
        self.registry = redis.Redis("localhost", db=1)
        Thread.__init__(self)

    def run(self):
        while True:
            self.registry.set("inductive_miner.apply_inductive", json.dumps(
                {"name": "Discover an Accepting Petri Net using the Inductive Miner", "inputs": {"log_key": "EventLog"},
                 "outputs": {"model_key": "AcceptingPetriNet"},
                 "type": "algorithm"}))
            self.registry.expire("inductive_miner.apply_inductive", 20)
            time.sleep(10)


s = ServiceRegister()
s.start()
