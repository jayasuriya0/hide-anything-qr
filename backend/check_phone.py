from pymongo import MongoClient
import os

client = MongoClient(os.environ.get('MONGO_URI', 'mongodb://localhost:27017/'))
db = client.hide_anything_qr

users_with_null_phone = list(db.users.find({'phone': None}))
print(f'Found {len(users_with_null_phone)} users with phone=null')
for u in users_with_null_phone:
    print(f"  - {u.get('username', u.get('email', 'unknown'))}")

print("\nRemoving phone field from users with null phone...")
result = db.users.update_many({'phone': None}, {'$unset': {'phone': ''}})
print(f"Updated {result.modified_count} documents")
