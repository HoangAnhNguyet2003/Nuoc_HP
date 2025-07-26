from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from flask_cors import CORS  # <-- THÊM DÒNG NÀY

app = Flask(__name__)
CORS(app)  # <-- BẬT CORS TOÀN CỤC CHO TOÀN BỘ API

client = MongoClient("mongodb://localhost:27017/")
db = client["HP_water"]

# GET tất cả tên đồng hồ
@app.route("/get-all-watch-names", methods=["GET"])
def get_all_watch_names():
    names = set()
    documents = db.watch_collection.find()

    for doc in documents:
        data_list = doc.get("data", [])
        for item in data_list:
            name = item.get("watch_name")
            if name:
                names.add(name)

    sorted_names = sorted(list(names))
    return jsonify(sorted_names)

# GET model LSTM 
@app.route("/get-all-lstm-data", methods=["GET"])
def get_all_lstm_data():
    lstm_model = db.lstm_models.find_one(sort=[("_id", -1)])
    if not lstm_model:
        return jsonify([])
    model_type = lstm_model.get("model_type", "LSTM")

    watch_doc = db.watch_collection.find_one({"_id": lstm_model["watch_id"]})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

    avg = lstm_model["avg_flow"][0]
    flow = lstm_model["flow_LSTM"][0]

    result = []
    date_list = flow.get("date_LSTM", [])
    
    for i, date in enumerate(date_list):
        result.append({
            "watch_name": watch_name,
            "model": model_type, 
            "date": date,
            "min_avg": avg["min_avg"][i] if i < len(avg["min_avg"]) else None,
            "max_avg": avg["max_avg"][i] if i < len(avg["max_avg"]) else None,
            "min_pred": flow["min_LSTM"][i] if i < len(flow["min_LSTM"]) else None,
            "max_pred": flow["max_LSTM"][i] if i < len(flow["max_LSTM"]) else None,
        })

    return jsonify(result)

# GET model AutoEncoder 
@app.route("/get-all-autoencoder-data", methods=["GET"])
def get_all_lstm_data():
    autoencoder_model = db.AutoEncoder_models.find_one(sort=[("_id", -1)])
    if not autoencoder_model:
        return jsonify([])
    model_type = autoencoder_model.get("model_type", "AutoEncoder")

    watch_doc = db.watch_collection.find_one({"_id": autoencoder_model["watch_id"]})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

    avg = autoencoder_model["avg_flow"][0]
    flow = autoencoder_model["flow_AutoEncoder"][0]

    result = []
    date_list = flow.get("date_AutoEncoder", [])
    
    for i, date in enumerate(date_list):
        result.append({
            "watch_name": watch_name,
            "model": model_type, 
            "date": date,
            "min_avg": avg["min_avg"][i] if i < len(avg["min_avg"]) else None,
            "max_avg": avg["max_avg"][i] if i < len(avg["max_avg"]) else None,
            "min_pred": flow["min_AutoEncoder"][i] if i < len(flow["min_AutoEncoder"]) else None,
            "max_pred": flow["max_AutoEncoder"][i] if i < len(flow["max_AutoEncoder"]) else None,
        })

    return jsonify(result)

# GET model Iso
@app.route("/get-all-isolation-data", methods=["GET"])
def get_all_isolation_data():
    iso_model = db.isolation_models.find_one(sort=[("_id", -1)])
    if not iso_model:
        return jsonify([])

    # Lấy tên mô hình từ DB
    model_type = iso_model.get("model_type", "Isolation")

    # Lấy tên đồng hồ
    watch_doc = db.watch_collection.find_one({"_id": iso_model["watch_id"]})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

    avg = iso_model["avg_flow"][0]
    flow = iso_model["flow_iso"][0]

    result = []
    date_list = flow.get("date_Iso", [])

    for i, date in enumerate(date_list):
        result.append({
            "watch_name": watch_name,
            "model": model_type,
            "date": date,
            "min_avg": avg["min_avg"][i] if i < len(avg["min_avg"]) else None,
            "max_avg": avg["max_avg"][i] if i < len(avg["max_avg"]) else None,
            "min_pred": flow["min_flow"][i] if i < len(flow["min_flow"]) else None,
            "max_pred": flow["max_flow"][i] if i < len(flow["max_flow"]) else None,
        })

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
