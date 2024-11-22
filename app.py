from flask import Flask, request, jsonify

# used libr
import pandas as pd
import json
import os

app = Flask(__name__)

"""
Processing files : C-bis
    * 3 functions A.K.A steps
    * Loading, extraction, downlaod

"""
# Load Excel file
def loading(fpath):
    try:
        df = pd.read_excel(fpath, header=[2, 1])  # Skip unnecessary rows
        return df
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")

# Extract data into a structured dictionary
def extraction(df):
    """
    Extracts structured data from the provided DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the raw data.

    Returns:
        list: A list of dictionaries representing each employee's data.
    """
    result = []

    # Get unique employee names (cleaning up .1, .2, etc.)
    employees = df.iloc[0].dropna().unique()  # First row contains employee names

    # Loop through each employee
    for i, employee in enumerate(employees):
        employee_data = {
            "name": employee.strip()  # Clean up any extra spaces or symbols
        }

        # Iterate over each row from the third row onwards
        for _, row in df.iloc[2:].iterrows():
            libelle = row[1]  # Second column contains the label
            base_s = float(row[2 + i * 3]) if row[2 + i * 3] == row[2 + i * 3] else 0  # The 'Base S.' is in column 3 + i*3
            salarial = float(row[3 + i * 3]) if row[3 + i * 3] == row[3 + i * 3] else 0  # The 'Salarial' is in column 4 + i*3
            patronal = float(row[4 + i * 3]) if row[4 + i * 3] == row[4 + i * 3] else 0 # The 'Patronal' is in column 5 + i*3

            # Add the extracted data into the employee's dictionary
            employee_data[libelle] = {
                "Base S.": base_s,
                "Salarial": salarial,
                "Patronal": patronal
            }

        # Append each employee's data to the result list
        result.append(employee_data)

    return result

@app.route('/process_cbis', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({"error": "File is required"}), 400

    file = request.files['file']

    if not file.filename.endswith('.xlsx'):
        return jsonify({"error": "Invalid file format. Please upload an Excel file"}), 400

    try:
        # Load the Excel file
        df = loading(file)

        # Extract the data
        result = extraction(df)

        # Return the JSON file for download
        return app.response_class(
        response=json.dumps({"object": result}, ensure_ascii=False, indent=4),
        status=200,
        mimetype='application/json'
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    """
    finally:
        # Clean up the temporary JSON file
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
    """
if __name__ == '__main__':
    app.run(Debug_mode=True) # Debug logs
