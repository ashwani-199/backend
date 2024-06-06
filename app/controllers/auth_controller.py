from werkzeug.security import check_password_hash
from app.models import get_user_collection

def authenticate_user(username, password):
    user_collection = get_user_collection()
    user = user_collection.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        return True, user
    return False, None

def profile_user(username):
    user_collection = get_user_collection()
    user = user_collection.find_one({"username": username})
    if user:
        return True, user
    return False, None

def check_admin(username):
    user_collection = get_user_collection()
    admin = user_collection.find_one({"username": username, "role": 1})
    print(admin)
    print(bool(admin))
    return bool(admin)
