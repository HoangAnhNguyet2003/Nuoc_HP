from pymongo import MongoClient
import bcrypt

client = MongoClient("mongodb://localhost:27017/")
db = client["HP_water"]

db.roles.drop()
db.companies.drop()
db.branches.drop()
db.users.drop()

# ==== Bảng Role ====
roles = [
    { "role_id": 1, "name": "Admin" },
    { "role_id": 2, "name": "Tổng công ty" },
    { "role_id": 3, "name": "Viewer" }
]
db.roles.insert_many(roles)

# ==== Bảng Company ====
companies = [
    { "company_id": 1, "name": "Công ty Cấp Nước Hải Phòng" },

]
db.companies.insert_many(companies)

# ==== Bảng Branch ====
branches = [
    { "branch_id": 1, "name": "Chi nhánh Văn Đẩu", "company_id": 1 },
    { "branch_id": 2, "name": "Chi nhánh Hồng Bàng", "company_id": 1 },
]
db.branches.insert_many(branches)

# ==== Bảng User ====
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

users = [
    {
        "user_id": 1,
        "user_name": "admin1",
        "password": hash_password("123456"),
        "role_id": 1,         # Admin
        "company_id": 1,
        "branch_id": 1
    },
    {
        "user_id": 2,
        "user_name": "tongcongty1",
        "password": hash_password("123456"),
        "role_id": 2,         # Tổng công ty
        "company_id": 1,
        "branch_id": 2
    },
    {
        "user_id": 3,
        "user_name": "chinhanh1",
        "password": hash_password("123456"),
        "role_id": 3,         # Công ty con
        "company_id": 2,
        "branch_id": 1
    }
]
db.users.insert_many(users)


# ==== Bảng Watch_device ====
db.watch_device.drop()

watch_devices = [
    {
        "watch_id": 1,
        "watch_name": "Văn Đẩu 8",
        "branch_id": 1
    },
    {
        "watch_id": 2,
        "watch_name": "Hồng Bàng 1",
        "branch_id": 2
    },
    {
        "watch_id": 3,
        "watch_name": "Hải Châu 5",
        "branch_id": 3
    }
]

db.watch_device.insert_many(watch_devices)

print("✅ Đã tạo xong đầy đủ bảng Role, Company, Branch, User.")
