import requests

files = {"running-example": open("C:/running-example.xes", "rb")}

resp = requests.post("http://localhost:5000/upload", files=files)
ids = resp.json()
types = {}
for id in ids:
    types[id] = "EventLog2"
requests.post("http://localhost:5000/set_objects_type", json=types)

for id in ids:
    resp = requests.get("http://localhost:5000/download?id="+id+"&filename=running-example.xes")
    print(resp)
