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

