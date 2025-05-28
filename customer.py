import os
import json
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'customer_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEFAULT_GUEST_ID = 'guest_profile'

def get_customer_id(customer_id):
    return secure_filename(customer_id or DEFAULT_GUEST_ID)

@app.route('/upload-profile/<customer_id>', methods=['POST'])
def upload_profile(customer_id):
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    folder = os.path.join(UPLOAD_FOLDER, get_customer_id(customer_id))
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, 'profile.webp')

    try:
        img = Image.open(file.stream)
        img.save(filepath, format='WEBP', quality=80)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Profile uploaded successfully', 'path': filepath})

@app.route('/profile/<customer_id>', methods=['GET'])
def get_profile(customer_id):
    profile_path = os.path.join(UPLOAD_FOLDER, get_customer_id(customer_id), 'profile.webp')
    if os.path.exists(profile_path):
        return send_file(profile_path, mimetype='image/webp')
    return jsonify({'error': 'Profile not found'}), 404

@app.route('/wishlist/<customer_id>', methods=['POST'])
def save_wishlist(customer_id):
    wishlist = request.get_json()
    if not isinstance(wishlist, list):
        return jsonify({'error': 'Wishlist must be a list'}), 400

    folder = os.path.join(UPLOAD_FOLDER, get_customer_id(customer_id))
    os.makedirs(folder, exist_ok=True)
    wishlist_path = os.path.join(folder, 'wishlist.json')

    try:
        with open(wishlist_path, 'w') as f:
            json.dump(wishlist, f)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Wishlist saved successfully'})

@app.route('/wishlist/<customer_id>', methods=['GET'])
def get_wishlist(customer_id):
    wishlist_path = os.path.join(UPLOAD_FOLDER, get_customer_id(customer_id), 'wishlist.json')
    if os.path.exists(wishlist_path):
        with open(wishlist_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/referrals/<customer_id>', methods=['POST'])
def save_referral(customer_id):
    referral = request.get_json()
    if not isinstance(referral, dict):
        return jsonify({'error': 'Referral must be a dictionary'}), 400

    folder = os.path.join(UPLOAD_FOLDER, get_customer_id(customer_id))
    os.makedirs(folder, exist_ok=True)
    referral_path = os.path.join(folder, 'referrals.json')

    try:
        with open(referral_path, 'w') as f:
            json.dump(referral, f)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Referral saved successfully'})

@app.route('/referrals/<customer_id>', methods=['GET'])
def get_referral(customer_id):
    referral_path = os.path.join(UPLOAD_FOLDER, get_customer_id(customer_id), 'referrals.json')
    if os.path.exists(referral_path):
        with open(referral_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
