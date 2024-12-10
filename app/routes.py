from flask import Blueprint, request, jsonify, Flask
import json
from app.services import process_file_cbis, process_file_A, \
    process_file_B, find_file_type

main = Blueprint('main', __name__)

@main.route('/excel_type', methods=['POST'])
def find_type_endpoint():
    # Check if the file is part of the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']

    # Check if the file has a valid filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Call the find_file_type function and pass the file
        result = find_file_type(file)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/process_cbis', methods=['POST'])
def process_cbis_endpoint():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files['file']
        if not file.filename.endswith('.xlsx'):
            return jsonify({"success": False, "error": "Invalid file format. Only .xlsx allowed"}), 400

        # Traitement du fichier
        result = process_file_cbis(file)
        return Flask.response_class(
            response=json.dumps({"success": True, "data": result}, ensure_ascii=False, indent=4),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

@main.route('/process_A', methods=['POST'])
def process_A_endpoint():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files['file']
        if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xlsm'):
            return jsonify({"success": False, "error": "Invalid file format. Only .xlsx / .xlsm allowed"}), 400

        # Traitement du fichier
        result = process_file_A(file)
        return Flask.response_class(
            response=json.dumps({"success": True, "data": result}, ensure_ascii=False, indent=4),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@main.route('/process_B', methods=['POST'])
def process_B_endpoint():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files['file']
        if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xlsm'):
            return jsonify({"success": False, "error": "Invalid file format. Only .xlsx / .xlsm allowed"}), 400

        # Traitement du fichier
        result = process_file_B(file)
        return Flask.response_class(
            response=json.dumps({"success": True, "data": result}, ensure_ascii=False, indent=4),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500