def clean_value(value):
    """
    NaN -> 0
    float others
    """
    return float(value) if value==value else 0

def cbis_normalize(df):
    """
    Try to increase population of C bis
    1) Normal
    2) With no header
    """
    if df.iloc[0].isna().all() :
        df = df.rename(columns=df.iloc[1])
        df = df.drop([0, 1])
        df = df.reset_index(drop=True)
    df = df.drop(0)
    return df

def list_employees(df):
    """
    Drop Nan values from the header
    & start with unnamed
    """
    employees = df.columns.dropna().tolist()
    employees = [col.strip() for col in employees if not col.strip().startswith("Unnamed")]
    return employees

def find_emmployee_name(text):
    first_dash = text.find("-")
    second_dash = text.find("-", first_dash + 1)
    return text[first_dash + 1:second_dash].strip() \
        if (first_dash != -1 and second_dash != -1) \
        else "Anonyme"
