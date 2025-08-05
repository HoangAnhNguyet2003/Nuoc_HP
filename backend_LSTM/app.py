from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import bcrypt

app = Flask(__name__)
# Cấu hình JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"  
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]
jwt = JWTManager(app)
blacklist = set()

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["HP_water"]
users_collection = db["users"]
client = MongoClient("mongodb://localhost:27017/")
db = client["HP_water"]


# ======= /login endpoint =======
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user_name = data.get("user_name")
    password = data.get("password")

    if not user_name or not password:
        return jsonify({"msg": "Thiếu thông tin đăng nhập"}), 400

    user = users_collection.find_one({"user_name": user_name})
    if not user:
        return jsonify({"msg": "Tài khoản không tồn tại"}), 404

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"msg": "Sai mật khẩu"}), 401

    #  sửa identity thành string
    access_token = create_access_token(
        identity=str(user["user_id"]),
        additional_claims={
            "user_name": user["user_name"],
            "role_id": user["role_id"],
            "company_id": user["company_id"],
            "branch_id": user["branch_id"]
        }
    )

    return jsonify({
        "msg": "Đăng nhập thành công",
        "access_token": access_token
    }), 200
    
@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    return jsonify({"msg": "Đăng xuất thành công"}), 200

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


@app.route("/get-all-lstm-data", methods=["GET"])
@jwt_required() 
def get_all_lstm_data():
    # Lấy thông tin người dùng đang đăng nhập (tuỳ chọn)
    current_user_id = get_jwt_identity()  # Có thể dùng để lọc theo user nếu muốn

    # Lấy bản ghi mới nhất từ collection
    lstm_model = db.ctgan_lstm_models.find_one(sort=[("_id", -1)])
    if not lstm_model:
        return jsonify([])

    model_type = lstm_model.get("model_type", "LSTM")

    # Tìm tên đồng hồ
    watch_doc = db.watch_collection.find_one({"_id": lstm_model["watch_id"]})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

    # Lấy dữ liệu trung bình và dự đoán
    avg = lstm_model["avg_flow"][0]
    flow = lstm_model["flow_LSTM"][0]

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


@app.route("/get-all-ae-data", methods=["GET"])
def get_all_ae_data():
    ae_model = db.autoencoder_models.find_one(sort=[("_id", -1)])
    if not ae_model:
        return jsonify([])

    model_type = ae_model.get("model_type", "Autoencoder")

    # Lấy thông tin watch name
    watch_doc = db.watch_collection.find_one({"_id": ae_model["watch_id"]})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

    # Thông tin trung bình lưu lượng
    avg = ae_model["avg_flow"][0]
    min_avg_map = dict(zip(avg.get("date_time", []), avg.get("min_avg", [])))
    max_avg_map = dict(zip(avg.get("date_time", []), avg.get("max_avg", [])))

    # Thông tin mô hình
    flow = ae_model["flow_AE"][0]

    morning_dates = flow.get("date_AE_min", [])
    evening_dates = flow.get("date_AE_max", [])

    morning_losses = flow.get("min_recon_loss", [])
    evening_losses = flow.get("max_recon_loss", [])

    morning_real = flow.get("min_real_values", [])
    morning_pred = flow.get("min_predicted_values", [])

    evening_real = flow.get("max_real_values", [])
    evening_pred = flow.get("max_predicted_values", [])

    result = []

    for i, date in enumerate(morning_dates):
        record = {
            "watch_name": watch_name,
            "model": model_type,
            "date": date,
            "min_avg": min_avg_map.get(date),
            "max_avg": max_avg_map.get(date),
            "recon_loss_morning": morning_losses[i] if i < len(morning_losses) else None,
            "real_value_morning": morning_real[i] if i < len(morning_real) else None,
            "predicted_value_morning": morning_pred[i] if i < len(morning_pred) else None,
            "recon_loss_evening": evening_losses[i] if i < len(evening_losses) else None,
            "real_value_evening": evening_real[i] if i < len(evening_real) else None,
            "predicted_value_evening": evening_pred[i] if i < len(evening_pred) else None
        }
        result.append(record)

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

@app.route("/get-all-ctgan-gru-data", methods=["GET"])
def get_all_ctgan_gru_data():
    # Lấy bản ghi mới nhất từ MongoDB
    gru_model = db.ctgan_lstm_models.find_one(
        {"model_type": {"$regex": "CTGAN\\+GRU"}},  # tìm đúng model GRU
        sort=[("_id", -1)]
    )
    if not gru_model:
        return jsonify([])

    # Thông tin mô hình và đồng hồ
    model_type = gru_model.get("model_type", "CTGAN+GRU")

    watch_doc = db.watch_collection.find_one({"_id": gru_model["watch_id"]})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc and "data" in watch_doc else "Không rõ"

    # Dữ liệu trung bình và dự đoán
    avg = gru_model.get("avg_flow", [{}])[0]
    flow = gru_model.get("flow_CTGAN_LSTM", [{}])[0]

    min_avg_map = dict(zip(avg.get("date_time", []), avg.get("min_avg", [])))
    max_avg_map = dict(zip(avg.get("date_time", []), avg.get("max_avg", [])))

    date_list = flow.get("date_LSTM", [])
    min_preds = flow.get("min_LSTM", [])
    max_preds = flow.get("max_LSTM", [])

    result = []
    for i, date in enumerate(date_list):
        result.append({
            "watch_name": watch_name,
            "model": model_type,
            "date": date,
            "min_avg": min_avg_map.get(date),
            "max_avg": max_avg_map.get(date),
            "min_pred": min_preds[i] if i < len(min_preds) else None,
            "max_pred": max_preds[i] if i < len(max_preds) else None
        })

    return jsonify(result)

@app.route("/get-all-gru-data", methods=["GET"])
def get_all_gru_data():
    model = db.gru_models.find_one(sort=[("_id", -1)])
    if not model:
        return jsonify([])

    model_type = model.get("model_type", "GRU (Real Data Only)")
    watch_doc = db.watch_collection.find_one({"_id": model.get("watch_id")})
    watch_name = watch_doc["data"][0].get("watch_name", "Không rõ") if watch_doc else "Không rõ"

    avg = model.get("avg_flow", [{}])[0]
    flow = model.get("flow_GRU", [{}])[0]

    min_avg_map = dict(zip(avg.get("date_time", []), avg.get("min_avg", [])))
    max_avg_map = dict(zip(avg.get("date_time", []), avg.get("max_avg", [])))

    date_list = flow.get("date_GRU", [])
    min_preds = flow.get("min_GRU", [])
    max_preds = flow.get("max_GRU", [])

    result = [
        {
            "watch_name": watch_name,
            "model": model_type,
            "date": date,
            "min_avg": min_avg_map.get(date),
            "max_avg": max_avg_map.get(date),
            "min_pred": min_preds[i] if i < len(min_preds) else None,
            "max_pred": max_preds[i] if i < len(max_preds) else None,
        }
        for i, date in enumerate(date_list)
    ]

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
