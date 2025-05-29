import os
import json
import requests
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'customer_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEFAULT_GUEST_ID = 'guest_profile'
LOCAL_SYNC_ENDPOINT = 'http://localhost:5001/sync-profile-image'


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
        print(f"[UPLOAD] Profile uploaded for {customer_id}")

        try:
            with open(filepath, 'rb') as f:
                requests.post(LOCAL_SYNC_ENDPOINT, files={'file': f}, data={'customer_id': customer_id})
                print(f"[SYNC] Sent profile to local server for {customer_id}")
        except Exception as sync_err:
            print(f"[SYNC ERROR] Could not sync to local: {sync_err}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    profile_url = f"{request.host_url.rstrip('/')}/profile/{get_customer_id(customer_id)}"
    return jsonify({'message': 'Profile uploaded successfully', 'url': profile_url})


@app.route('/profile/<customer_id>', methods=['GET'])
def get_profile(customer_id):
    profile_path = os.path.join(UPLOAD_FOLDER, get_customer_id(customer_id), 'profile.webp')
    if os.path.exists(profile_path):
        return send_file(profile_path, mimetype='image/webp')
    return jsonify({'error': 'Profile not found'}), 404


@app.route('/fetch-from-local/<customer_id>', methods=['POST'])
def fetch_from_local(customer_id):
    try:
        print(f"[FETCH REQUEST] Asking local server to send profile for {customer_id}")
        r = requests.post(
            'http://localhost:5001/send-profile',
            data={'customer_id': customer_id}
        )
        return jsonify({'status': 'requested from local'}), r.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/all-customers', methods=['GET'])
def list_all_customers():
    try:
        ids = [
            name for name in os.listdir(UPLOAD_FOLDER)
            if os.path.isdir(os.path.join(UPLOAD_FOLDER, name))
        ]
        return jsonify(ids)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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