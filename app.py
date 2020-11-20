import redis
from flask import Flask
from flask import request
from flask_nameko import FlaskPooledClusterRpcProxy

rpc = FlaskPooledClusterRpcProxy()
app = Flask(__name__)
database = redis.Redis("localhost", db=0)
registry = redis.Redis("localhost", db=1)


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


if __name__ == "__main__":
    app.config.update(dict(
        NAMEKO_AMQP_URI='amqp://localhost'
    ))
    rpc.init_app(app)
    app.run()
