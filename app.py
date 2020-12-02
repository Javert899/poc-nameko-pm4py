import redis
import uuid
import pathlib
from flask import Flask
from flask import request, jsonify, send_file
from flask_nameko import FlaskPooledClusterRpcProxy
from tempfile import NamedTemporaryFile
from flask_cors import CORS
from poc_config import *

rpc = FlaskPooledClusterRpcProxy()
app = Flask(__name__)
CORS(app)
database = redis.Redis(OBJECT_DATAFRAME_HOSTNAME, db=OBJECT_DATAFRAME_ID)
registry = redis.Redis(REGISTRY_DATAFRAME_HOSTNAME, db=REGISTRY_DATAFRAME_ID)


@app.route('/call_service')
def call_service():
    service = None
    kwargs = {}
    for arg in request.args:
        val = request.args[arg]
        if arg == "service":
            service = val
        else:
            kwargs[arg] = val
    return eval("rpc." + service + "(**kwargs)")


@app.route('/get_objects')
def get_objects():
    types, names = __get_object_types_and_names()
    ret = {}
    for o, t in types.items():
        ret[o] = {"type": t, "name": ""}
    for o, n in names.items():
        ret[o]["name"] = n
    return ret


@app.route('/get_entrypoints')
def get_entrypoints():
    entrypoints = __get_entrypoints()
    ret = {}
    for e, t in entrypoints.items():
        ret[e] = t
    return ret


@app.route("/upload", methods=['POST'])
def upload():
    ret = []
    for filek in request.files:
        file = request.files[filek]
        object_id = str(uuid.uuid4())
        content = file.stream.read()
        database.set(object_id, content)
        database.set(object_id + "_type", "")
        database.set(object_id + "_name", object_id)
        ret.append(object_id)
    return jsonify(ret)


@app.route('/download', methods=['GET'])
def download():
    id = request.args.get("id", type=str)
    filename = request.args.get("filename", type=str)
    content = database[id]
    temp_file = NamedTemporaryFile(suffix=".temp")
    temp_file.close()
    file_name = temp_file.name
    temp_file = open(file_name, "wb")
    temp_file.write(content)
    temp_file.close()
    temp_file = open(file_name, "rb")
    resp = send_file(temp_file, attachment_filename=filename)
    return resp


@app.route("/set_objects_type", methods=['POST'])
def set_objects_type():
    content = request.json
    for object_id in content:
        database.set(object_id + "_type", content[object_id])
    return ""


@app.route("/set_objects_name", methods=['POST'])
def set_objects_name():
    content = request.json
    for object_id in content:
        database.set(object_id + "_name", content[object_id])
    return ""


def __get_object_types_and_names():
    keys = [k.decode("utf-8") for k in list(database.keys())]
    types = {}
    names = {}
    for k in keys:
        if "_type" in k:
            types[k.split("_type")[0]] = database[k].decode("utf-8")
        if "_name" in k:
            names[k.split("_name")[0]] = database[k].decode("utf-8")
    return types, names


def __get_entrypoints():
    keys = [k.decode("utf-8") for k in list(registry.keys())]
    ep = {}
    for k in keys:
        ep[k] = registry[k].decode("utf-8")
    return ep


if __name__ == "__main__":
    app.config.update(dict(
        NAMEKO_AMQP_URI=AMQP_URL
    ))
    rpc.init_app(app)
    app.run(host="0.0.0.0")
