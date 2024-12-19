import os
import subprocess
import shutil
from flask import Flask, make_response, request, jsonify
from flask_cors import CORS
import requests
from analyze import analyze_pitch
from compare import compare_user_voice_with_score
from get_results import create_get_results_route

app = Flask(__name__)
CORS(app)

TEMP_DIR = "temp"
DATA_DIR = "data"
DONE_DIR = "done"
RESULTS_DIR = "results"
FIREBASE_TEMPLATE_URL = "https://firebasestorage.googleapis.com/v0/b/algorhymns04.appspot.com/o/scores%2F{artist} - {title}.json?alt=media"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DONE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Đăng ký route GET từ file get_results.py

@app.route('/analyze_audio', methods=['POST'])
def analyze_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    artist = request.form.get('artist')
    title = request.form.get('title')
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        temp_file_path = os.path.join(TEMP_DIR, file.filename)
        print(temp_file_path)
        file.save(temp_file_path)
        print("Running analyze.py...")
        # change_script_result = subprocess.run(
        #     ['python', 'analyze.py', temp_file_path],
        #     capture_output=True, text=True
        # )

        # print("Output from analyze.py:")
        # print(change_script_result.stdout)

        # if change_script_result.returncode != 0:
        #     return jsonify({'error': 'Failed to process audio file with analyze.py'}), 500
        analyze_pitch(temp_file_path)
        # Kiểm tra xem file JSON đã được tạo chưa
        data_file_path = os.path.join(DATA_DIR, "user_voice_notes.json")
        if not os.path.exists(data_file_path):
            return jsonify({'error': 'JSON result file not found after processing'}), 500
        
         # Tải template từ Firebase
        print("Downloading template from Firebase...")
        template_file_path = os.path.join(TEMP_DIR, "template.json")
        firebase_url = FIREBASE_TEMPLATE_URL.format(artist=artist, title=title)
        print(firebase_url)

        response = requests.get(firebase_url)

        if response.status_code == 200:
            with open(template_file_path, 'w') as f:
                f.write(response.text)
            print(f"Template downloaded successfully to {template_file_path}")
        else:
            return jsonify({
                'error': f'Failed to download template from Firebase. HTTP Status: {response.status_code}'
            }), 500

        # Thực thi file compare.py
        print("Running compare.py...")
        result_file_path = os.path.join(RESULTS_DIR, "compare_results.json")
        # compare_script_result = subprocess.run(
        #     ['python', 'compare.py', temp_file_path, data_file_path, result_file_path],
        #     capture_output=True, text=True
        # )
        # print("Output from compare.py:")
        # print(compare_script_result.stdout)
        # print("Error output from compare.py:")
        # print(compare_script_result.stderr)

        # if compare_script_result.returncode != 0:
        #     return jsonify({'error': 'Failed to compare notes with compare.py'}), 500
        # if not os.path.exists(result_file_path):
        #     return jsonify({'error': 'Comparison result file not created'}), 500
        compare_user_voice_with_score(template_file_path, data_file_path, result_file_path)

        done_file_path = os.path.join(DONE_DIR, file.filename)
        shutil.move(temp_file_path, done_file_path)
        print(f"File moved to done folder: {done_file_path}")
        return jsonify({
            'message': 'Analysis and result transmission completed successfully',
            'data_file': data_file_path,
            'result_file': result_file_path,
            'done_file': done_file_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/file-received', methods=['POST'])
def file_received():
    try:
        data = request.get_json()
        if not data or 'status' not in data or data['status'] != 'received':
            return make_response(jsonify({"error": "Invalid status or missing status"}), 400)
        result_file_path = os.path.join(RESULTS_DIR, "compare_results.json")
        if os.path.exists(result_file_path):
            os.remove(result_file_path)
            print(f"File {result_file_path} deleted successfully.")
            return jsonify({"message": "File deleted successfully."}), 200
        else:
            return make_response(jsonify({"error": "File not found"}), 404)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    
create_get_results_route(app)

if __name__ == '__main__':
    app.run(debug=True)