import os
import json

def save_session(user_id, session_data):
    path = f"static/sessions/{user_id}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(session_data, f)

def load_session(user_id):
    path = f"static/sessions/{user_id}.json"
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}
