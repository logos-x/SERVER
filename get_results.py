import os
import time
from flask import Flask, jsonify, send_file, make_response

RESULTS_DIR = "results"

def create_get_results_route(app):
    @app.route('/get-results', methods=['GET'])
    def get_results():
        result_file_name = "compare_results.json"
        result_file_path = os.path.join(RESULTS_DIR, result_file_name)
        while not os.path.exists(result_file_path):
            print("Waiting for the result file to be created...")
            time.sleep(1)  
        try:
            return send_file(result_file_path, as_attachment=True, mimetype='application/json')
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to send file: {str(e)}"}), 500)
