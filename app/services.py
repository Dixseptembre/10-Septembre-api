import pandas as pd
from app.utils import clean_value

def process_file(file):
    # Charger le fichier
    df = pd.read_excel(file, header=[2, 1])  # Lire avec un en-tête multi-niveau
    if df.empty:
        raise ValueError("The file is empty or invalid format")

    # Extraire les données
    employees = df.iloc[0].dropna().unique().tolist()
    result = {"employees": [], "libelle_patronal": []}  # Ajouter libelle_patronal au niveau global

    for idx, employee in enumerate(employees):
        employee_data = {"name": employee, "infos": []}

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
    result["employees"].pop()
    return result