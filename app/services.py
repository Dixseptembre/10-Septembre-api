import pandas as pd
from app.utils import clean_value

def process_file_cbis(file):
    # Charger le fichier
    df = pd.read_excel(file, sheet_name=0, header=[2, 1])  # Lire avec un en-tête multi-niveau
    if df.empty:
        raise ValueError("The file is empty or invalid format")

    # Extraire les données
    employees = df.iloc[0].dropna().unique().tolist()
    result = {"employees": [], "libelle_patronal": []}  # Ajouter libelle_patronal au niveau global

    for idx, employee in enumerate(employees):
        employee_data = {"name": employee, "infos": []}
        if not employee or "total" in str(employee).lower():
            continue
        for _, row in df.iloc[2:].iterrows():
            libelle = row.iloc[1]  # Libellé
            base_s = clean_value(row.iloc[2 + idx * 3])  # Base S.
            salarial = clean_value(row.iloc[3 + idx * 3])  # Salarial
            patronal = clean_value(row.iloc[4 + idx * 3])  # Patronal

            # Append (libelle and related infos)
            employee_data["infos"].append({
                "Libellé": libelle,
                "Base S.": base_s,
                "Salarial": salarial,
                "Patronal": patronal
            })
            # Ajouter le libellé à la liste globale si "patronal" est non nul
            if patronal != 0 and libelle not in result["libelle_patronal"] and _ < df.index[df.iloc[:, 1] == 'Total des retenues déductibles'].tolist()[0]:
                result["libelle_patronal"].append(libelle)
        result["employees"].append(employee_data)

    return result

def process_file_A(file):
    # Load with appropriate header levels
    df = pd.read_excel(file, sheet_name=0, header=[2, 1])  # Assuming a simple single-level header
    if df.empty:
        raise ValueError("The file is empty or invalid format")
    df = df.iloc[1:]
    df.columns = df.columns.get_level_values(1)
    # Init the structure
    result = {"employees": [], "libelle_patronal": []}
    
    # Loop through the rows and process each employee's data
    employee_data = {}
    
    for index, row in df.iterrows():
        # Detect new employee based on the first column
        if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], (int, float)):
            # If there's an existing employee, add them to the result
            if employee_data:
                result["employees"].append(employee_data)
                employee_data = {}  # Reset for the new employee
            
            # Start a new employee record
            employee_name = row.iloc[1]  # Employee name is in the second column
            employee_data = {"name": employee_name, "infos": []}
            continue # Skip because New

        # Data for the current employee
        if employee_data:
            row_name = row.iloc[0]  # Row name is in the first column
            base_s = clean_value(row.iloc[df.columns.get_loc('Base ou Nombre')])  # Base S.
            salarial = clean_value(row.iloc[df.columns.get_loc('Part Salariale Gains')])  # Salarial
            patronal = clean_value(row.iloc[df.columns.get_loc('Part Patronale Retenues')])  # Patronal

            # Append the row data to the current employee's infos
            row_info = {
                "Libellé": row_name,
                "Base S.": base_s,
                "Salarial": salarial,
                "Patronal": patronal
            }
            employee_data["infos"].append(row_info)

            # Add libellé
            if patronal != 0 and row_name not in result["libelle_patronal"] \
                and not row_name[0].isdigit() \
                    and index < df.index[df.iloc[:, 0] == '50_COTIS_DEDUCTIBLE'].tolist()[0]:
                result["libelle_patronal"].append(row_name)
    
    # Add the final employee
    result["employees"].append(employee_data)

    return result