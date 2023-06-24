from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from flask import Flask, request, jsonify, url_for
import json
from datetime import datetime
from bson import ObjectId

from .fornear_secrets import ATLAS_PASS, ATLAS_USERNAME

uri = f"mongodb+srv://{ATLAS_USERNAME}:{ATLAS_PASS}@ganso.koavv7w.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi("1"))

def dump_json(data):
    return json.dumps(data, default=str)

app = Flask(__name__)
CLIENT = MongoClient(uri, server_api=ServerApi("1"))
DB = CLIENT["fornear-v1"]


@app.route("/system/routes")
def get_routes():
    with app.app_context():
        routes_list = [str(rule) for rule in app.url_map.iter_rules()]
    return dump_json(routes_list)

@app.route("/api/get_inventory", methods=["GET"])
def get_inventory():
    inventory = list(DB["inventory"].find())
    return dump_json(inventory)

@app.route("/api/request_package", methods=["POST"])
def request_package():
    data = request.json
    data["request_date"] = datetime.now().strftime("%Y-%m-%d")
    data["request_time"] = datetime.now().strftime("%H:%M:%S")
    DB["requests"].insert_one(data)
    return jsonify({"message": "success"})

@app.route("/api/get_requests", methods=["GET"])
def get_requests():
    # group by packageId and get all requests
    requests = list(DB["requests"].aggregate([
        {
            "$group": {
                "_id": "$packageId",
                "requests": {
                    "$push": "$$ROOT"
                }
            }
        }
    ]))
    # add package name to each request
    for request in requests:
        package = DB["packages"].find_one({"_id": ObjectId(request["_id"])})
        request["packageName"] = package["packageName"]
    requests.sort(key=lambda x: x["packageName"])
    return dump_json(requests)

@app.route("/api/get_packages", methods=["GET"])
def get_packages():
    packages = list(DB["packages"].find())
    return dump_json(packages)

@app.route("/api/get_package_by_id", methods=["POST"])
def get_package_by_id():
    data = request.json
    package = DB["packages"].find_one({"_id": ObjectId(data["_id"])})
    return dump_json(package)

@app.route("/api/insert_item", methods=["POST"])
def insert_item():
    data = request.json
    DB["inventory"].insert_one(data)
    return jsonify({"message": "success"})

@app.route("/api/create_package", methods=["POST"])
def create_package():
    data = request.json
    data["creation_date"] = datetime.now().strftime("%Y-%m-%d")
    data["creation_time"] = datetime.now().strftime("%H:%M:%S")
    DB["packages"].insert_one(data)
    return jsonify({"message": "success"})

if __name__ == "__main__":
    app.run(debug=True)