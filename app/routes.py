from flask import Blueprint, request, jsonify, Flask, send_file
import json, os
import pandas as pd
import tempfile
from app.services import process_file_cbis, process_file_A, \
    process_file_B, process_file_D, find_file_type

main = Blueprint('main', __name__)

# Route to manage all types at once
@main.route('/extraction', methods=['POST'])
def extract_information_endpoint():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files['file']
        if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xlsm'):
            return jsonify({"success": False, "error": "Invalid file format. Only .xlsx /.xlsm allowed"}), 400

        # Check type
        # Call the find_file_type function and pass the file
        j_type = find_file_type(file)
        type = j_type['type']
        match type:
            case "A":
                result = process_file_A(file)
            case "B":
                result = process_file_B(file)
            case "Cbis":
                result = process_file_cbis(file)
            case "D":
                result = process_file_D(file)
            case _:
                return jsonify({"error": "File "+type}), 400
        # success : True
        return Flask.response_class(
            response=json.dumps({"success": True, "data": result}, ensure_ascii=False, indent=4),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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



@main.route('/convert', methods=['POST'])
def convert_to_utf8_endpoint():
    """
    Receives a CSV file, converts it to UTF-8 encoding, and sends it to the Bubble app.
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Read CSV file with proper encoding
        for encoding in ['utf-8', 'ISO-8859-1']:
            try:
                df = pd.read_csv(file, encoding=encoding, dtype=str)
                break
            except UnicodeDecodeError:
                continue
        
        # Clean column names to remove special characters and whitespace
        df.columns = df.columns.str.strip().str.encode('utf-8', 'ignore').str.decode('utf-8')
        
        # Create a temporary file to save the converted CSV
        with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', encoding='utf-8-sig') as tmpfile:
            output_filename = tmpfile.name
            df.to_csv(output_filename, index=False, encoding='utf-8-sig', lineterminator='\n')
        
        # Send the file as a response
        response = send_file(output_filename, as_attachment=True)
        response.headers['Content-Disposition'] = f'attachment; filename={file.filename}'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        # Optionally, remove the temporary file after sending it (depends on your use case)
        os.remove(output_filename)
        
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
