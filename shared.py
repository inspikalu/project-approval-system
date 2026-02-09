import os
import json
import hashlib
import secrets

# --- Security & Data Constants ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.json")
SALT_LEGACY = b"salt123" # Legacy salt for migration

# --- Security Utilities ---
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(8)
    if isinstance(salt, str):
        salt_bytes = salt.encode()
    else:
        salt_bytes = salt
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt_bytes, 100000).hex(), salt

# --- Data Utilities ---
def load_json(filepath):
    if not os.path.exists(filepath): return []
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except: return []

def save_json(filepath, data):
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def sanitize_input(text):
    return text.strip()[:1000]
