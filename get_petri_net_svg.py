import json
import tempfile
import time
import uuid
from threading import Thread

import redis
from nameko.rpc import rpc

import pm4py

database = redis.Redis("localhost", db=0)
registry = redis.Redis("localhost", db=1)


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
                {"inputs": {"model_key": "AcceptingPetriNet"}, "outputs": {"model_image": "SVG"}}))
            self.registry.expire("petri_net_svg_viewer.petri_net_svg", 20)
            time.sleep(10)


s = ServiceRegister()
s.start()
