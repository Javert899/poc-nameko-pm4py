import requests

files = {"running-example": open("C:/running-example.xes", "rb")}

requests.post("http://localhost:5000/upload", files=files)
