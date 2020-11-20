# poc-nameko-pm4py
P.o.C. for the usage of Nameko in PM4Py

## Set-up

Follow the instructions contained in INSTALL.txt for the set-up of the P.o.C.

## Bootstrap

With four different command prompts, turn on the microservices

### Event log importer

nameko run --config config.yml importing_log

### Inductive Miner

nameko run --config config.yml inductive_miner

### Gets the SVG of the Petri net

nameko run --config config.yml get_petri_net_svg

### Object/Service Inspector Service

python app.py

## Usage

### Executing the calls to the services (RPC) using the Nameko shell

The Nameko shell can be open using the command:

nameko shell

Then, let's try to import an event log in the system:

Nameko Python 3.8.5 (tags/v3.8.5:580fbb0, Jul 20 2020, 15:57:54) [MSC v.1924 64 bit (AMD64)] shell on win32
Broker: pyamqp://guest:guest@localhost
In [1]: n.rpc.import_log.import_log("C:/running-example.xes")
Out[1]: 'efc1bc2d-03ef-4123-9c7a-c9f03fa34a70'

We can get the event log in a textual way, providing the ID returned by the import_log function, using:

In [2]: n.rpc.import_log.get_log_string("efc1bc2d-03ef-4123-9c7a-c9f03fa34a70")
...

Then, we apply the inductive miner, to get an accepting Petri net object (as identifier stored in Redis):

In [3]: n.rpc.inductive_miner.apply_inductive("efc1bc2d-03ef-4123-9c7a-c9f03fa34a70")
Out[3]: 'fc646980-41bf-4c4a-820d-866d6849e074'

We can performed then a visualization of the Petri net (SVG format):

In [4]: n.rpc.petri_net_svg_viewer.petri_net_svg("fc646980-41bf-4c4a-820d-866d6849e074")

MONITORING WEB SERVICE

The following web service can be used to check the list of objects stored in the Redis database:

http://localhost:5000/get_objects

The following web service can be used to check the microservices registered:

http://localhost:5000/get_entrypoints

The following web service can be used to execute a call to a service. In particular, we call the visualization of the
Petri net object

http://localhost:5000/call_service?service=petri_net_svg_viewer.petri_net_svg&model_key=fc646980-41bf-4c4a-820d-866d6849e074
