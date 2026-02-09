from flask import Flask, request, jsonify, session, send_from_directory
import os
import secrets
from shared import (
    load_json, save_json, sanitize_input, hash_password,
    USERS_FILE, SUBMISSIONS_FILE, SALT_LEGACY as SALT
)

app = Flask(__name__, static_folder='static')

# Load secret key from environment variable or generate a secure random one
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    # Generate a secure random key if not provided
    app.secret_key = secrets.token_hex(32)
    print("WARNING: Using auto-generated secret key. Set SECRET_KEY environment variable for production.")

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = sanitize_input(data.get('username', ''))
    password = data.get('password', '')
    
    users = load_json(USERS_FILE)
    user = next((u for u in users if u['username'] == username), None)
    
    if user:
        hashed, _ = hash_password(password, user.get('salt', SALT))
        if user['pw'] == hashed:
            session['user'] = {
                'username': user['username'],
                'role': user['role']
            }
            return jsonify({'success': True, 'user': session['user']})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/api/user', methods=['GET'])
def get_user():
    if 'user' in session:
        return jsonify({'success': True, 'user': session['user']})
    return jsonify({'success': False}), 401

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    if 'user' not in session:
        return jsonify({'success': False}), 401
    
    user = session['user']
    subs = load_json(SUBMISSIONS_FILE)
    
    if user['role'] == 'student':
        # Students only see their own submissions
        user_subs = [s for s in subs if s.get('student_id') == user['username']]
        return jsonify(user_subs)
    else:
        # Staff see all submissions
        return jsonify(subs)

@app.route('/api/submissions', methods=['POST'])
def create_submission():
    if 'user' not in session or session['user']['role'] != 'student':
        return jsonify({'success': False}), 403
    
    data = request.json
    content = sanitize_input(data.get('content', ''))
    sub_type = data.get('type', '')
    
    if not content or not sub_type:
        return jsonify({'success': False, 'message': 'Missing data'}), 400
    
    subs = load_json(SUBMISSIONS_FILE)
    new_sub = {
        "id": len(subs) + 1,
        "student_id": session['user']['username'],
        "type": sub_type,
        "content": content,
        "status": "Pending",
        "response": ""
    }
    subs.append(new_sub)
    save_json(SUBMISSIONS_FILE, subs)
    return jsonify({'success': True, 'submission': new_sub})

@app.route('/api/submissions/respond', methods=['POST'])
def respond_submission():
    if 'user' not in session or session['user']['role'] != 'staff':
        return jsonify({'success': False}), 403
    
    data = request.json
    sub_id = data.get('id')
    status = data.get('status')
    response = sanitize_input(data.get('response', ''))
    
    if sub_id is None or status not in ['Approved', 'Rejected']:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    subs = load_json(SUBMISSIONS_FILE)
    for s in subs:
        if s['id'] == sub_id:
            s['status'] = status
            s['response'] = response
            save_json(SUBMISSIONS_FILE, subs)
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Submission not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
