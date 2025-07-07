# app.py (Flask Web Interface for Aadhar Validator)

import os
from flask import Flask, render_template, request, jsonify
from main import AadharValidator
from captcha_solver import CaptchaSolver

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

TOGETHER_API_KEY = 'YOUR_TOGETHER_API_KEY'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    aadhar_number = request.form.get('aadhar')
    
    validator = AadharValidator(headless=True)
    try:
        validator.save_captcha("static/captcha.png")

        # Use Together AI to solve captcha
        solver = CaptchaSolver(api_key=TOGETHER_API_KEY)

        captcha_text = solver.solve_captcha_from_url(request.host_url + "static/captcha.png")
        result = validator.validate_aadhar(aadhar_number, captcha_text)
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "ERROR - " + str(e), "data": None, "isValid": None})

    finally:
        validator.close_browser()

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
