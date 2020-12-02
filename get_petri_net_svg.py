import json
import time
from threading import Thread

import pm4py
import redis
from nameko.rpc import rpc

from poc_config import *

database = redis.Redis(OBJECT_DATAFRAME_HOSTNAME, db=OBJECT_DATAFRAME_ID)
registry = redis.Redis(REGISTRY_DATAFRAME_HOSTNAME, db=REGISTRY_DATAFRAME_ID)


class PetriNetSvgViewer(object):
    name = "petri_net_svg_viewer"

    @rpc
    def petri_net_svg(self, model_key):
        petri_string = database.get(model_key).decode("utf-8")
        net, im, fm = pm4py.objects.petri.importer.variants.pnml.import_petri_from_string(petri_string)
        gviz = pm4py.visualization.petrinet.visualizer.apply(net, im, fm, parameters={"format": "svg"})
        render = gviz.render(cleanup=True)
        F = open(render, "r")
        content = F.read()
        F.close()
        return content


class ServiceRegister(Thread):
    def __init__(self):
        self.registry = redis.Redis("localhost", db=1)
        Thread.__init__(self)

    def run(self):
        while True:
            self.registry.set("petri_net_svg_viewer.petri_net_svg", json.dumps(
                {"inputs": {"model_key": "AcceptingPetriNet"}, "outputs": {"model_image": "SVG"},
                 "type": "algorithm"}))
            self.registry.expire("petri_net_svg_viewer.petri_net_svg", 20)
            self.registry.set("petri_net_svg_viewer.enable_pnml_uploading",
                              json.dumps(
                                  {"type": "importer", "extension": ".pnml", "object_type": "AcceptingPetriNet"}))
            self.registry.expire("petri_net_svg_viewer.enable_pnml_uploading", 20)
            self.registry.set("petri_net_svg_viewer.enable_pnml_downloading",
                              json.dumps(
                                  {"type": "exporter", "extension": ".pnml", "object_type": "AcceptingPetriNet"}))
            self.registry.expire("petri_net_svg_viewer.enable_pnml_downloading", 20)
            time.sleep(10)


s = ServiceRegister()
s.start()
