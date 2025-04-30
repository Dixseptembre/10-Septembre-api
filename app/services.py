import pandas as pd
from app.utils import clean_value, c_normalize, list_employees, find_emmployee_name

code_to_libelle = {
    "SS001": "Maladie - maternité - invalidité - décès",
    "SS002": "Contribution Solidarité Autonomie",
    "SS003": "Vieillesse déplafonnée",
    "SS004": "Vieillesse plafonnée",
    "SS005": "Allocations familiales",
    "SS006": "Accident du travail",
    "SS007": "FNAL plafonné",
    "SS009": "Versement Transport/Chèques-Vacances",
    "SS010": "Forfait social sur contributions de prévoya",
    "SS011.4": "Réduction générale des cotisations patronal",
    "SS013.2": "Exonération cotisation sur HC/HS",
    "SS014.1": "Déduction forfaitaire/heures supplémentaire",
    "SS021": "CSG déductible",
    "SS022": "CSG non déductible et CRDS",
    "SS027": "CSG intégralement non déductible / CRDS",
    "SS050": "Contribution au dialogue social",
    "CH001": "Assurance chômage TrA+TrB",
    "CH002": "AGS",
    "AA201": "Retraite TU1",
    "AA202": "Retraite TU2",
    "AA211": "Contribution d'Equilibre Général TU1",
    "AA212": "Contribution d'Equilibre Général TU2",
    "AA221": "Contribution d'Equilibre Technique TU1",
    "AA222": "Contribution d'Equilibre Technique TU2",
    "AA311.4": "Réduct. générale des cotisat. pat. retraite",
    "PS110": "Prévoyance supplémentaire non cadre TrA, ré",
    "PS120": "Prévoyance supplémentaire non cadre TrB, ré",
    "PS279": "Frais de santé Famille",
    "TC001.L": "Contribution formation prof. (légal)",
    "TC004": "Taxe d'apprentissage",
    "TC004.L": "Taxe d'apprentissage (Libératoire)"
}

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

def proceess_file_E(file):
    # Charger le fichier avec toutes les feuilles
    all_sheets = pd.read_excel(file, sheet_name=None, header=None)  # Lire toutes les feuilles dans un dictionnaire

    if not all_sheets:
        raise ValueError("The file is empty or invalid format")
    
    result = {"employees": [], "libelle_patronal": []}

    # Parcourir chaque feuille
    for sheet_name, df in all_sheets.items():
        if df.empty: continue  # Ignorer les feuilles vides
        if not df.iloc[0].astype(str).str.contains("Dossier", case=False, na=False).any(): continue
        
        # Find title rows (assume they are where col 0 is not NaN)
        title_rows = df[df.iloc[:, 0].notna()].index.tolist()
        
        # Add end index (after last row)
        title_rows.append(len(df))
        
        # Reset index of columns
        df.reset_index(drop=True, inplace=True)

        # Identify columns with empty values in the second row
        empty_cols = df.iloc[2].isnull()  # Updated to handle NaNs correctly

        # Drop the identified columns
        df = df.loc[:, ~empty_cols]
        df = df.reset_index(drop=True)

        for i in range(len(title_rows) - 1):
            start, end = title_rows[i], title_rows[i + 1]
            sub_df = df.iloc[start:end].reset_index(drop=True)

            if sub_df.empty or len(sub_df) < 2:
                continue

            header = sub_df.iloc[1]
            data = sub_df[2:].reset_index(drop=True)
            data.columns = header
            data = c_normalize(data)

            # Current employees
            ls_employees = list_employees(data)

            for idx, employee in enumerate(ls_employees):
                if not employee or "total" in str(employee).lower() or "totaux" in str(employee).lower():
                    continue

                existing_employee = next(
                    (e for e in result["employees"] if e["name"] == employee), None
                )

                if not existing_employee:
                    employee_data = {"name": employee, "infos": []}
                    result["employees"].append(employee_data)
                else:
                    employee_data = existing_employee

                # Temporary dictionary to store sums by libelle
                libelle_to_data = {}

                for _, row in data.iterrows():
                    if not pd.isna(row.iloc[0]):
                        code = row.iloc[0]
                        libelle = code_to_libelle.get(code, row.iloc[1])
                    else:
                        libelle = row.iloc[1]

                    if pd.isna(libelle):
                        continue

                    base_s = clean_value(row.iloc[2 + idx * 3])
                    salarial = clean_value(row.iloc[3 + idx * 3])
                    patronal = clean_value(row.iloc[4 + idx * 3])

                    if libelle not in libelle_to_data:
                        libelle_to_data[libelle] = {
                            "Base S.": 0,
                            "Salarial": 0,
                            "Patronal": 0
                        }

                    libelle_to_data[libelle]["Base S."] += base_s
                    libelle_to_data[libelle]["Salarial"] += salarial
                    libelle_to_data[libelle]["Patronal"] += patronal

                    # Update patronal libelle list
                    if patronal != 0 and libelle not in result["libelle_patronal"]:
                        if "Total des retenues déductibles" in data.iloc[:, 2].values:
                            limit_index = data.index[data.iloc[:, 2] == 'Total des retenues déductibles'][0]
                            if _ < limit_index:
                                result["libelle_patronal"].append(libelle)
                        else:
                            result["libelle_patronal"].append(libelle)

                # Now assign the aggregated infos
                for libelle, values in libelle_to_data.items():
                    employee_data["infos"].append({
                        "Libellé": libelle,
                        "Base S.": values["Base S."],
                        "Salarial": values["Salarial"],
                        "Patronal": values["Patronal"]
                    })
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
                if df.columns.astype(str).str.contains("Dossier", case=False, na=False).any():
                    result["type"] = "E"
                    return result

        # If no pattern matches
        result["type"] = "not recognized"
        return result

    except Exception as e:
        return {"error": str(e)}
