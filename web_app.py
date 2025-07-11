# web_app.py (Flask Web Interface for Aadhar Validator)

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from main import AadharValidator
from captcha_solver import CaptchaSolver
import os
import dotenv
import uuid
validators = {}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
dotenv.load_dotenv()

TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY', '')

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    aadhar_number = request.form.get('aadhar')
    session_id = str(uuid.uuid4())
    validator = AadharValidator(headless=False)
    validators[session_id] = validator
    captcha_value = None
    captcha_path = f"images/captcha_{session_id}.png"
    try:
        validator.save_captcha(captcha_path)
        # Try auto captcha solver
        # try:
        #     solver = CaptchaSolver(api_key=TOGETHER_API_KEY)
        #     captcha_value = solver.solve_captcha_from_url(request.host_url + f"images/captcha_{session_id}.png")
        #     if captcha_value:
        #         print("[INFO] Captcha solved automatically.", captcha_value)
        #         return jsonify({"status": "CAPTCHA_AUTO", "session_id": session_id, "captcha": captcha_value, "captcha_url": f"/images/captcha_{session_id}.png", "data": None, "isValid": None})
        # except Exception as solver_exc:
        #     pass  # Fallback to manual if solver fails
        
        return jsonify({"status": "CAPTCHA_REQUIRED", "session_id": session_id, "captcha_url": f"/images/captcha_{session_id}.png", "data": None, "isValid": None})
    except Exception as e:
        validator.close_browser()
        del validators[session_id]
        return jsonify({"status": "ERROR - " + str(e), "data": None, "isValid": None})

@app.route('/submit_captcha', methods=['POST'])
def submit_captcha():
    aadhar_number = request.form.get('aadhar')
    captcha_text = request.form.get('captcha')
    session_id = request.form.get('session_id')
    validator = validators.get(session_id)
    captcha_path = f"images/captcha_{session_id}.png"
    if not validator:
        return jsonify({"status": "ERROR - Session expired", "data": None, "isValid": None})
    try:
        result = validator.validate_aadhar(aadhar_number, captcha_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "ERROR - " + str(e), "data": None, "isValid": None})
    finally:
        validator.close_browser()
        del validators[session_id]
        try:
            os.remove(captcha_path)
        except Exception:
            pass

import requests

@app.route('/check_site', methods=['GET'])
def check_site():
    url = request.args.get('url')

    if not url:
        return jsonify({"status": "ERROR", "message": "Missing URL parameter"}), 400

    try:
        response = requests.get(url, timeout=5)
        return jsonify({
            "url": url,
            "status": "OK" if response.status_code == 200 else "WARNING",
            "status_code": response.status_code,
            "reason": response.reason
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            "url": url,
            "status": "ERROR",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000) 