from pymongo import MongoClient, ASCENDING, DESCENDING
from werkzeug.security import generate_password_hash
from datetime import datetime, UTC
datetime.now(UTC)
# ===== Kết nối DB =====
client = MongoClient("mongodb://localhost:27017/")

print("DBs:", client.list_database_names()) 
db = client["hp_water"]  # thống nhất DB

# ===== Dọn sạch (tuỳ chọn) =====
for col in [
    "roles","companies","branches","users",
    "watch_device","predict_ai","predict_ai_log","alerts",
    "repair_logs","audit_logs"
]:
    db[col].drop()

# ===== Index theo đặc tả =====
# Role
db.roles.create_index([("role_id", ASCENDING)], unique=True)

# Company
db.companies.create_index([("company_id", ASCENDING)], unique=True)
db.companies.create_index([("code", ASCENDING)], unique=True, sparse=True)
db.companies.create_index([("name", ASCENDING)])

# Branch
db.branches.create_index([("branch_id", ASCENDING)], unique=True)
db.branches.create_index([("company_id", ASCENDING)])
db.branches.create_index([("name", ASCENDING)])

# User
db.users.create_index([("user_id", ASCENDING)], unique=True)
db.users.create_index([("username", ASCENDING)], unique=True)
db.users.create_index([("email", ASCENDING)], unique=True, sparse=True)
db.users.create_index([("role_id", ASCENDING)])
db.users.create_index([("branch_id", ASCENDING)])

# Watch_device
db.watch_device.create_index([("watch_id", ASCENDING)], unique=True)
db.watch_device.create_index([("serial", ASCENDING)], unique=True)
db.watch_device.create_index([("branch_id", ASCENDING)])
db.watch_device.create_index([("status", ASCENDING)])

# Predict_AI (snapshot)
db.predict_ai.create_index([("id_model", ASCENDING)], unique=True)
db.predict_ai.create_index([("watch_id", ASCENDING)])
db.predict_ai.create_index([("date", DESCENDING)])

# Predict_AI_Log (time series)
db.predict_ai_log.create_index([("id", ASCENDING)], unique=True)
db.predict_ai_log.create_index([("watch_id", ASCENDING), ("ts", DESCENDING)])
# Nếu muốn chặn trùng một thời điểm: unique theo (watch_id, ts)
# db.predict_ai_log.create_index([("watch_id", ASCENDING), ("ts", DESCENDING)], unique=True)

# Alerts
db.alerts.create_index([("alert_id", ASCENDING)], unique=True)
db.alerts.create_index([("watch_id", ASCENDING)])
db.alerts.create_index([("status", ASCENDING)])
db.alerts.create_index([("severity", ASCENDING)])
db.alerts.create_index([("created_at", DESCENDING)])

# Repair_Log
db.repair_logs.create_index([("id", ASCENDING)], unique=True)
db.repair_logs.create_index([("watch_id", ASCENDING), ("ts", DESCENDING)])
db.repair_logs.create_index([("actor_id", ASCENDING), ("ts", DESCENDING)])

# Audit_Log
db.audit_logs.create_index([("id", ASCENDING)], unique=True)
db.audit_logs.create_index([("ts", DESCENDING)])
db.audit_logs.create_index([("user_id", ASCENDING), ("ts", DESCENDING)])
db.audit_logs.create_index([("action", ASCENDING), ("ts", DESCENDING)])

# ===== Helpers =====
def now():
    return datetime.now(UTC)

def hash_pw(p):
    return generate_password_hash(p)


companies = [
    {"company_id": 1, "code": "HP", "name": "Công ty Cấp Nước Hải Phòng", "address": "Hải Phòng"},
    {"company_id": 2, "code": "A",  "name": "Công ty Cấp Nước A (demo)",  "address": "Quảng Ninh"},
]
db.companies.insert_many(companies)


branches = [
    {"branch_id": 1, "company_id": 1, "name": "Chi nhánh Văn Đẩu",  "address": "Văn Đẩu"},
    {"branch_id": 2, "company_id": 1, "name": "Chi nhánh Hồng Bàng","address": "Hồng Bàng"},
    {"branch_id": 3, "company_id": 2, "name": "Chi nhánh Hải Châu", "address": "Hải Châu"},
]
db.branches.insert_many(branches)


roles = [
    {"role_id": 1, "name": "Admin",        "description": "Quản trị hệ thống"},
    {"role_id": 2, "name": "Tổng công ty", "description": "Xem toàn công ty"},
    {"role_id": 3, "name": "Viewer",       "description": "Người dùng thường"},
]
db.roles.insert_many(roles)

users = [
    {
        "user_id": 1, "username": "admin1", "password_hash": hash_pw("123456"),
        "full_name": "System Admin", "email": "admin1@example.com", "phone": None,
        "role_id": 1, "branch_id": 1, "is_active": True, "last_login_at": None
    },
    {
        "user_id": 2, "username": "tongcongty1", "password_hash": hash_pw("123456"),
        "full_name": "Tổng công ty 1", "email": "tc1@example.com", "phone": None,
        "role_id": 2, "branch_id": 2, "is_active": True, "last_login_at": None
    },
    {
        "user_id": 3, "username": "viewer1", "password_hash": hash_pw("123456"),
        "full_name": "Viewer 1", "email": "v1@example.com", "phone": None,
        "role_id": 3, "branch_id": 3, "is_active": True, "last_login_at": None
    },
]
db.users.insert_many(users)


watch_devices = [
    {
        "watch_id": 1, "serial": "WCH-001", "watch_name": "Văn Đẩu 8",
        "branch_id": 1, "status": "ACTIVE", "installed_at": None,
        "location_note": "Gần cổng", "created_at": now(), "updated_at": None
    },
    {
        "watch_id": 2, "serial": "WCH-002", "watch_name": "Hồng Bàng 1",
        "branch_id": 2, "status": "ACTIVE", "installed_at": None,
        "location_note": None, "created_at": now(), "updated_at": None
    },
    {
        "watch_id": 3, "serial": "WCH-003", "watch_name": "Hải Châu 5",
        "branch_id": 3, "status": "MAINTENANCE", "installed_at": None,
        "location_note": "Đang bảo trì", "created_at": now(), "updated_at": None
    },
]
db.watch_device.insert_many(watch_devices)


predict_ai = [
    {
        "id_model": 1, "watch_id": 1, "name_model": "leak_v1",
        "date": datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0),
        "min_avg": 60.0, "max_avg": 120.0, "min_pred": 60.0, "max_pred": 125.0
    },
    {
        "id_model": 2, "watch_id": 2, "name_model": "leak_v1",
        "date": datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0),
        "min_avg": 50.0, "max_avg": 110.0, "min_pred": 55.0, "max_pred": 118.0
    },
]
db.predict_ai.insert_many(predict_ai)


predict_ai_logs = [
    {
        "id": 1, "watch_id": 1, "name_model": "leak_v1",
        "ts": now(), "leak_prob": 0.82, "pred_value": 130.5,
        "min_avg": 65.0, "max_avg": 130.5, "min_pred": 65.0, "max_pred": 130.5,
        "meta": {"window": "1h", "ver": "1.0.3"}
    },
    {
        "id": 2, "watch_id": 2, "name_model": "leak_v1",
        "ts": now(), "leak_prob": 0.40, "pred_value": 95.2,
        "min_avg": 45.0, "max_avg": 100.0, "min_pred": 50.0, "max_pred": 99.0,
        "meta": {"window": "1h", "ver": "1.0.3"}
    },
]
db.predict_ai_log.insert_many(predict_ai_logs)

# 8) Alert (tạo 1 alert từ log id=1)
alerts = [
    {
        "alert_id": 1, "watch_id": 1, "predict_log_id": 1,
        "created_at": now(), "severity": "HIGH", "status": "OPEN",
        "leak_prob": 0.82, "threshold": 0.70,
        "message": "Leak prob 0.82 >= threshold 0.70",
        "acknowledged_by": None, "acknowledged_at": None,
        "resolved_at": None, "resolution_note": None
    }
]
db.alerts.insert_many(alerts)

# 10) Repair_Log
repairs = [
    {
        "id": 1, "watch_id": 1, "actor_id": 3,
        "action": "INSPECT", "note": "Kiểm tra ban đầu", "ts": now()
    },
    {
        "id": 2, "watch_id": 1, "actor_id": 3,
        "action": "REPAIR", "note": "Thay gioăng", "ts": now()
    },
]
db.repair_logs.insert_many(repairs)

# 11) Audit_Log
audits = [
    {
        "id": 1, "ts": now(), "user_id": 1, "action": "LOGIN",
        "entity": None, "entity_id": None, "ip_addr": "127.0.0.1",
        "details": {"ua": "seed_script"}
    },
    {
        "id": 2, "ts": now(), "user_id": 1, "action": "CREATE_DEVICE",
        "entity": "WATCH_DEVICE", "entity_id": "3", "ip_addr": "127.0.0.1",
        "details": {"serial": "WCH-003"}
    },
]
db.audit_logs.insert_many(audits)


