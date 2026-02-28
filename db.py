from pymongo import MongoClient
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from bson import ObjectId

# Initialize MongoDB Connection
# Using a local MongoDB instance. In production, this would be a MongoDB URI from environment.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["python_chess_db"]

users_col = db["users"]
rooms_col = db["rooms"]


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]

    @staticmethod
    def get(user_id):
        user_data = users_col.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None


def create_user(username, password):
    if get_user_by_username(username):
        return None  # User exists

    hashed_password = generate_password_hash(password)
    result = users_col.insert_one(
        {
            "username": username,
            "password": hashed_password,
            "games_played": 0,
            "wins": 0,
        }
    )
    return User.get(result.inserted_id)


def get_user_by_username(username):
    user_data = users_col.find_one({"username": username})
    return User(user_data) if user_data else None


def verify_user(username, password):
    user_data = users_col.find_one({"username": username})
    if user_data and check_password_hash(user_data["password"], password):
        return User(user_data)
    return None


def create_room(host_username, is_private=False):
    room_data = {
        "host": host_username,
        "player_white": host_username,
        "player_black": None,
        "is_private": is_private,
        "status": "waiting",  # waiting, playing, finished
        "game_state": None,  # Will store the JSON serialized board
    }
    result = rooms_col.insert_one(room_data)
    return str(result.inserted_id)


def get_public_rooms():
    return list(rooms_col.find({"is_private": False, "status": "waiting"}))


def get_room(room_id):
    try:
        return rooms_col.find_one({"_id": ObjectId(room_id)})
    except Exception:
        return None


def join_room(room_id, username):
    room = get_room(room_id)
    if room and room["status"] == "waiting" and room["player_white"] != username:
        rooms_col.update_one(
            {"_id": ObjectId(room_id)},
            {"$set": {"player_black": username, "status": "playing"}},
        )
        return True
    return False


def update_room_state(room_id, serialized_game_state, status="playing"):
    rooms_col.update_one(
        {"_id": ObjectId(room_id)},
        {"$set": {"game_state": serialized_game_state, "status": status}},
    )


def record_win(winner_username, loser_username):
    if winner_username:
        users_col.update_one(
            {"username": winner_username}, {"$inc": {"wins": 1, "games_played": 1}}
        )
    if loser_username:
        users_col.update_one(
            {"username": loser_username}, {"$inc": {"games_played": 1}}
        )
