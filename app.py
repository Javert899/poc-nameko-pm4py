import redis
import uuid
import pathlib
from flask import Flask
from flask import request, jsonify, send_file
from flask_nameko import FlaskPooledClusterRpcProxy
from tempfile import NamedTemporaryFile
from poc_config import *

rpc = FlaskPooledClusterRpcProxy()
app = Flask(__name__)
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
    types = __get_object_types()
    stru = ["<ul>"]
    for o, t in types.items():
        stru.append("<li>%s %s</li>" % (o, t))
    stru.append("</ul>")
    return "".join(stru)


@app.route('/get_entrypoints')
def get_entrypoints():
    entrypoints = __get_entrypoints()
    stru = ["<ul>"]
    for e, t in entrypoints.items():
        stru.append("<li>%s %s</li>" % (e, t))
    stru.append("</ul>")
    return "".join(stru)


@app.route("/upload", methods=['POST'])
def upload():
    ret = []
    for filek in request.files:
        file = request.files[filek]
        object_id = str(uuid.uuid4())
        content = file.stream.read()
        database.set(object_id, content)
        database.set(object_id + "_type", "")
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


def __get_object_types():
    keys = [k.decode("utf-8") for k in list(database.keys())]
    types = {}
    for k in keys:
        if "_type" in k:
            types[k.split("_type")[0]] = database[k].decode("utf-8")
    return types


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
