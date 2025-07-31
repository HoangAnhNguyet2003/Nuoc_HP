from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

app = Flask(__name__)
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

    # Lấy tên đồng hồ
    watch_doc = db.watch_collection.find_one({"_id": lstm_model["watch_id"]})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

    # Tách dữ liệu
    avg = lstm_model["avg_flow"][0]
    flow = lstm_model["flow_LSTM"][0]

    # Tạo ánh xạ ngày → min_avg và ngày → max_avg
    min_avg_map = dict(zip(avg.get("date_time", []), avg.get("min_avg", [])))
    max_avg_map = dict(zip(avg.get("date_time", []), avg.get("max_avg", [])))

    result = []
    date_list = flow.get("date_LSTM", [])
    
    for i, date in enumerate(date_list):
        result.append({
            "watch_name": watch_name,
            "model": model_type,
            "date": date,
            "min_avg": min_avg_map.get(date),
            "max_avg": max_avg_map.get(date),
            "min_pred": flow["min_LSTM"][i] if i < len(flow["min_LSTM"]) else None,
            "max_pred": flow["max_LSTM"][i] if i < len(flow["max_LSTM"]) else None,
        })

    return jsonify(result)

@app.route("/get-all-ae-data", methods=["GET"])
def get_all_ae_data():
    ae_model = db.autoencoder_models.find_one(sort=[("_id", -1)])
    if not ae_model:
        return jsonify([])

    model_type = ae_model.get("model_type", "Autoencoder")
    watch_doc = db.watch_collection.find_one({"_id": ae_model["watch_id"]})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

    avg = ae_model["avg_flow"][0]
    flow = ae_model["flow_AE"][0]

    min_avg_map = dict(zip(avg.get("date_time", []), avg.get("min_avg", [])))
    max_avg_map = dict(zip(avg.get("date_time", []), avg.get("max_avg", [])))

    morning_dates = flow.get("date_AE_min", [])
    evening_dates = flow.get("date_AE_max", [])

    morning_losses = flow.get("min_recon_loss", [])
    evening_losses = flow.get("max_recon_loss", [])

    result = []
    for i, date in enumerate(morning_dates):
        result.append({
            "watch_name": watch_name,
            "model": model_type,
            "date": date,
            "min_avg": min_avg_map.get(date),
            "max_avg": max_avg_map.get(date),
            "recon_loss_morning": morning_losses[i] if i < len(morning_losses) else None,
            "recon_loss_evening": evening_losses[i] if i < len(evening_losses) else None
        })

    return jsonify(result)

# GET model CTGAN+LSTM
@app.route("/get-all-ctgan-lstm-data", methods=["GET"])
def get_all_ctgan_lstm_data():
    # Lấy bản ghi mới nhất từ collection
    lstm_model = db.ctgan_lstm_models.find_one(sort=[("_id", -1)])
    if not lstm_model:
        return jsonify([])

    model_type = lstm_model.get("model_type", "CTGAN+LSTM")

    # Tìm tên đồng hồ
    watch_doc = db.watch_collection.find_one({"_id": lstm_model["watch_id"]})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

    # Lấy dữ liệu trung bình và dự đoán
    avg = lstm_model["avg_flow"][0]
    flow = lstm_model["flow_CTGAN_LSTM"][0]

    # Tạo ánh xạ ngày → min_avg và max_avg
    min_avg_map = dict(zip(avg.get("date_time", []), avg.get("min_avg", [])))
    max_avg_map = dict(zip(avg.get("date_time", []), avg.get("max_avg", [])))

    result = []
    date_list = flow.get("date_LSTM", [])
    
    for i, date in enumerate(date_list):
        result.append({
            "watch_name": watch_name,
            "model": model_type,
            "date": date,
            "min_avg": min_avg_map.get(date),
            "max_avg": max_avg_map.get(date),
            "min_pred": flow["min_LSTM"][i] if i < len(flow["min_LSTM"]) else None,
            "max_pred": flow["max_LSTM"][i] if i < len(flow["max_LSTM"]) else None,
        })

    return jsonify(result)



# @app.route("/get-all-vae-data", methods=["GET"])
# def get_all_vae_data():
#     # Lấy model VAE mới nhất
#     vae_model = db.vae_models.find_one(sort=[("_id", -1)])
#     if not vae_model:
#         return jsonify([])

#     # Lấy tên mô hình
#     model_type = vae_model.get("model_type", "VAE")

#     # Lấy tên đồng hồ
#     watch_doc = db.watch_collection.find_one({"_id": vae_model["watch_id"]})
#     watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

#     # Lấy dữ liệu từ document
#     avg = vae_model["avg_flow"][0]     # gồm date_time, min_avg, max_avg
#     flow = vae_model["flow_VAE"][0]    # gồm date_VAE, min_VAE, max_VAE

#     result = []
#     date_list = flow.get("date_VAE", [])

#     for i, date in enumerate(date_list):
#         result.append({
#             "watch_name": watch_name,
#             "model": model_type,
#             "date": date,
#             "min_avg": avg["min_avg"][i] if i < len(avg["min_avg"]) else None,
#             "max_avg": avg["max_avg"][i] if i < len(avg["max_avg"]) else None,
#             "min_pred": flow["min_VAE"][i] if i < len(flow["min_VAE"]) else None,
#             "max_pred": flow["max_VAE"][i] if i < len(flow["max_VAE"]) else None,
#         })

#     return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
