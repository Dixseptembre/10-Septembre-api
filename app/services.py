import pandas as pd
from app.utils import clean_value

def process_file(file):
    # Charger le fichier
    df = pd.read_excel(file, header=[2, 1])  # Lire avec un en-tête multi-niveau
    if df.empty:
        raise ValueError("The file is empty or invalid format")

    # Extraire les données
    employees = df.iloc[0].dropna().unique().tolist()
    result = []

    for idx, employee in enumerate(employees):
        employee_data = {"name": employee}
        for _, row in df.iloc[2:].iterrows():
            libelle = row[1]
            base_s = float(row[2 + idx * 3]) if row[2 + idx * 3] == row[2 + idx * 3] else 0
            salarial = float(row[3 + idx * 3]) if row[3 + idx * 3] == row[3 + idx * 3] else 0
            patronal = float(row[4 + idx * 3]) if row[4 + idx * 3] == row[4 + idx * 3] else 0

            employee_data[libelle] = {
                "Base S.": base_s,
                "Salarial": salarial,
                "Patronal": patronal
            }
        result.append(employee_data)

    return result