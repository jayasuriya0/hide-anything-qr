# init_db.py
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.hide_anything_qr

# Create collections with validation (optional)
db.create_collection('users')
db.create_collection('friendships')
db.create_collection('shared_content')
db.create_collection('notifications')

print("Database initialized successfully!")