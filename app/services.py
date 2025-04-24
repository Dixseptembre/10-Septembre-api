import pandas as pd
from app.utils import clean_value, c_normalize, list_employees, find_emmployee_name

def process_file_A(file):
    # Load all sheets without header
    all_sheets = pd.read_excel(file, sheet_name=None, header=None)

    if not all_sheets:
        raise ValueError("The file is empty or invalid format")

    result = {"employees": [], "libelle_patronal": []}

    for sheet_name, df in all_sheets.items():
        if df.empty:
            continue

        # Check if any value in the first column contains "Libellé rubrique"
        if not df.iloc[:, 0].astype(str).str.contains("Libellé rubrique", na=False).any():
            continue
        
        # Set header manually 
        df.columns = df.iloc[2]
        df = df.iloc[3:].reset_index(drop=True)

        employee_data = {}

        for index, row in df.iterrows():
            if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], (int, float)):
                if employee_data:
                    result["employees"].append(employee_data)
                    employee_data = {}

                employee_name = row.iloc[1]
                employee_data = {"name": employee_name, "infos": []}
                continue

            if employee_data and isinstance(row.iloc[0], str):
                row_name = row.iloc[0]
                try:
                    base_s = clean_value(row.iloc[df.columns.get_loc('Base ou Nombre')])
                    salarial = clean_value(row.iloc[df.columns.get_loc('Part Salariale Gains')])
                    patronal = clean_value(row.iloc[df.columns.get_loc('Part Patronale Retenues')])
                except KeyError:
                    continue

                row_info = {
                    "Libellé": row_name,
                    "Base S.": base_s,
                    "Salarial": salarial,
                    "Patronal": patronal
                }
                employee_data["infos"].append(row_info)

                if (
                    patronal != 0
                    and row_name not in result["libelle_patronal"]
                    and not row_name[0].isdigit()
                    and '50_COTIS_DEDUCTIBLE' in df.iloc[:, 0].values
                    and index < df.index[df.iloc[:, 0] == '50_COTIS_DEDUCTIBLE'].tolist()[0]
                ):
                    result["libelle_patronal"].append(row_name)

        if employee_data:
            result["employees"].append(employee_data)

    return result

def process_file_B(file):
    # Charger le fichier avec toutes les feuilles
    all_sheets = pd.read_excel(file, sheet_name=None)  # Lire toutes les feuilles dans un dictionnaire

    if not all_sheets:
        raise ValueError("The file is empty or invalid format")

    result = {"employees": [], "libelle_patronal": []}  # Ajouter libelle_patronal au niveau global

    # Parcourir chaque feuille
    for sheet_name, df in all_sheets.items():
        if df.empty:
            continue  # Ignorer les feuilles vides

        # Récupérer le titre de la feuille et le nom de l'employé
        title = df.columns[0]
        employee = find_emmployee_name(title)

        # Nettoyer et standardiser les noms de colonnes pour faciliter le traitement
        df.columns = df.iloc[1]  # Utiliser la deuxième ligne comme en-tête
        df = df[2:]  # Supprimer les deux premières lignes
        df.reset_index(drop=True, inplace=True)

        # Extraire les colonnes pertinentes pour Libellé, Base S., Salarial et Patronal
        relevant_columns = ["Libellé", "Base S.", "Salarial", "Patronal"]
        df_prime = df[relevant_columns]

        # Initialiser la structure des employés
        employee_data = {"name": employee, "infos": []}

        # Boucle à travers les lignes et traitement des données des employés
        for index, row in df_prime.iterrows():
            libellé = row.iloc[0]  # Le nom de la ligne est dans la première colonne
            base_s = clean_value(row.iloc[df_prime.columns.get_loc('Base S.')])  # Base S.
            salarial = clean_value(row.iloc[df_prime.columns.get_loc('Salarial')])  # Salarial
            patronal = clean_value(row.iloc[df_prime.columns.get_loc('Patronal')])  # Patronal

            # Ajouter les informations de la ligne aux infos de l'employé
            row_info = {
                "Libellé": libellé,
                "Base S.": base_s,
                "Salarial": salarial,
                "Patronal": patronal
            }
            employee_data["infos"].append(row_info)

            # Ajouter le libellé à la liste globale si "patronal" est non nul
            if patronal != 0 \
                and libellé not in result["libelle_patronal"] \
                and index < df.index[df.iloc[:, 1] == 'Total des retenues déductibles'].tolist()[0]:
                result["libelle_patronal"].append(libellé)

        # Ajouter l'employé au résultat
        result["employees"].append(employee_data)

    return result

def process_file_C(file):
    # Charger le fichier avec toutes les feuilles
    all_sheets = pd.read_excel(file, sheet_name=None)  # Lire toutes les feuilles dans un dictionnaire

    if not all_sheets:
        raise ValueError("The file is empty or invalid format")

    result = {"employees": [], "libelle_patronal": []}  # Ajouter libelle_patronal au niveau global

    # Parcourir chaque feuille
    for sheet_name, df in all_sheets.items():
        if df.empty:
            continue  # Ignorer les feuilles vides

        # Standardiser le DataFrame
        df = c_normalize(df)

        # Extraire les données pour chaque feuille
        employees = list_employees(df)  # employees with Total if exist

        for idx, employee in enumerate(employees):
            employee_data = {"name": employee, "infos": []}
            if not employee or "total" in str(employee).lower():
                continue
            for _, row in df.iloc[0:].iterrows():
                libelle = row.iloc[1]  # Libellé
                if pd.isna(libelle):
                    continue
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
    
def process_file_D(file):
    # Charger le fichier avec toutes les feuilles
    all_sheets = pd.read_excel(file, sheet_name=None)  # Lire toutes les feuilles dans un dictionnaire

    if not all_sheets:
        raise ValueError("The file is empty or invalid format")

    result = {"employees": [], "libelle_patronal": []}  # Ajouter libelle_patronal au niveau global

    # Parcourir chaque feuille
    for sheet_name, df in all_sheets.items():
        if df.empty:
            continue  # Ignorer les feuilles vides

        # Check if any value in the first column contains "Mois"
        if not df.iloc[:, 0].astype(str).str.contains("Mois", na=False).any():
            continue

        # Nettoyer les colonnes inutiles
        df = df.iloc[:, 2:]
        if "Mois de fin" in df.iloc[:, 0].values:  # Cas avec Mois de fin / année de fin
            df = df.iloc[:, 2:]

        # Récupérer les employés
        employees = list_employees(df)

        # Nettoyer les données
        df = df.rename(columns=df.iloc[0])
        df = df.drop(['Effectif', 'Taux', 'Total des taux', 'Montant total'], axis=1)
        if 'Non obligatoire' in df.columns:
            df = df.drop('Non obligatoire', axis=1)
        df = df.iloc[1:]

        # Grouper les lignes avec la même valeur dans la troisième colonne ("Libellé")
        df_grouped = df.groupby('Libellé', sort=False).sum().reset_index()

        # Traiter les employés
        for idx, employee in enumerate(employees):
            employee_data = {"name": employee, "infos": []}
            if not employee or employee=='TOTAL':
                continue  # Ignorer si l'employé est vide

            for _, row in df_grouped.iterrows():
                libellé = row.iloc[0]
                base_s = clean_value(row.iloc[1 + idx * 3])
                salarial = clean_value(row.iloc[2 + idx * 3])
                patronal = clean_value(row.iloc[3 + idx * 3])

                # Ajouter les informations de la ligne aux informations de l'employé
                employee_data["infos"].append({
                    "Libellé": libellé,
                    "Base S.": base_s,
                    "Salarial": salarial,
                    "Patronal": patronal
                })

                # Ajouter le libellé à la liste globale si "patronal" est non nul
                if patronal != 0 and \
                    libellé not in result["libelle_patronal"] and \
                    not libellé.startswith('Sous-total') and \
                    not libellé.startswith('TOTAL'):
                    result["libelle_patronal"].append(libellé)

            result["employees"].append(employee_data)

    return result

def find_file_type(file):
    try:
        # Read all sheets into a dictionary
        sheets = pd.read_excel(file, sheet_name=None)

        # Initialize result dictionary
        result = {}

        # Iterate through each sheet
        for df in sheets.values():
            # Skip empty sheets
            if df.empty:
                continue

            # Prevent indexing errors by checking number of columns
            if df.shape[1] > 2:
                if df.iloc[:, 0].astype(str).str.contains("Code", na=False).any():
                    if df.iloc[:, 2].astype(str).str.contains("Nb Salariés", na=False).any():
                        result["type"] = "B"
                        return result
                    elif df.iloc[:, 2].astype(str).str.contains("Base S.", na=False).any():
                        result["type"] = "C"
                        return result

            if df.shape[1] > 0:
                if df.iloc[:, 0].astype(str).str.contains("Libellé rubrique", na=False).any():
                    result["type"] = "A"
                    return result
                if df.iloc[:, 0].astype(str).str.contains("Mois", na=False).any():
                    result["type"] = "D"
                    return result

        # If no pattern matches
        result["type"] = "not recognized"
        return result

    except Exception as e:
        return {"error": str(e)}
