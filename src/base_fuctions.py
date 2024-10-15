from datetime import datetime

import requests
import pandas as pd
import tools

pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)


# Utility Functions

def make_url(base_url: str, endpoint: str) -> str:
    """
    Constructs the full API URL using the base URL and endpoint identifier.

    Parameters:
    base_url (str): The base URL of the API.
    endpoint (str): The specific endpoint or resource identifier.

    Returns:
    str: The constructed API URL.
    """
    return f"{base_url}/{endpoint}"


def get_data(api_url: str) -> dict:
    """
    Fetches data from the API endpoint provided.

    Parameters:
    api_url (str): The full API URL to request data from.

    Returns:
    dict: Parsed JSON response from the API, or None if an error occurs.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return None


# Data Transformation Functions

def data_to_js(api_response: dict, name_dict: str) -> list:
    """
    Extracts the 'preparedData' list from the API response.

    Parameters:
    api_response (dict): The JSON response from the API.

    Returns:
    list: The 'preparedData' list extracted from the API response, or an empty list if not found.
    """
    try:
        return api_response.get(f"{name_dict}", [])
    except AttributeError as e:
        print(f"An error occurred while extracting prepared data: {e}")
        return []


def js_to_df(json_data: list) -> pd.DataFrame:
    """
    Converts JSON data to a Pandas DataFrame.

    Parameters:
    json_data (list): A list of dictionaries representing the data.

    Returns:
    pd.DataFrame: The data represented as a Pandas DataFrame.
    """
    try:
        return pd.DataFrame(json_data)
    except ValueError as e:
        print(f"An error occurred while converting JSON to DataFrame: {e}")
        return pd.DataFrame()


def df_to_js(dataframe: pd.DataFrame) -> dict:
    """
    Converts a Pandas DataFrame into a dictionary.

    Parameters:
    dataframe (pd.DataFrame): The input DataFrame.

    Returns:
    dict: The DataFrame converted into a dictionary format.
    """
    try:
        return dataframe.to_dict(orient="records")
    except ValueError as e:
        print(f"An error occurred while converting DataFrame to JSON: {e}")
        return {}


def remove_columns(dataframe: pd.DataFrame, columns_to_remove: list) -> pd.DataFrame:
    """
    Removes specified columns from a DataFrame.

    Parameters:
    dataframe (pd.DataFrame): The DataFrame from which columns are to be removed.
    columns_to_remove (list): A list of column names to drop from the DataFrame.

    Returns:
    pd.DataFrame: A new DataFrame with the specified columns removed.
    """
    try:
        return dataframe.drop(columns=columns_to_remove, errors='ignore')
    except KeyError as e:
        print(f"An error occurred while removing columns: {e}")
        return dataframe


def rename_columns(dataframe: pd.DataFrame, rename_dict: dict) -> pd.DataFrame:
    """
    Renames columns in a DataFrame using a provided dictionary.

    Parameters:
    dataframe (pd.DataFrame): The DataFrame containing columns to rename.
    rename_dict (dict): A dictionary where keys are the old column names and values are the new column names.

    Returns:
    pd.DataFrame: A DataFrame with renamed columns.
    """
    try:
        return dataframe.rename(columns=rename_dict)
    except KeyError as e:
        print(f"An error occurred while renaming columns: {e}")
        return dataframe


# Modify the function to handle the case where a code with null 'fileName' should still appear if it occurs only once.
def add_url_with_single_null_handling(df: pd.DataFrame, base_url: str) -> pd.DataFrame:
    # Count occurrences of each code
    df['code_count'] = df.groupby('tracingNo').cumcount() + 1

    # Filter out the rows where 'fileName' is null and the code appears more than once
    df['downlod_url'] = df.apply(
        lambda row: None if pd.isnull(row['fileName']) and (df['tracingNo'] == row['tracingNo']).sum() == 1
        else f"{base_url}/{row['tracingNo']}/{row['code_count']}" if pd.notnull(row['fileName']) else None, axis=1)

    # Drop the 'code_count' column as it's only needed for generating the URLs
    df = df.drop(columns=['code_count'])

    return df


def update_column_values(df: pd.DataFrame, column_name: str, new_value):
    # Check if the column exists in the DataFrame
    if column_name in df.columns:
        # Update the values in the specified column to the new value
        df[column_name] = new_value
    else:
        print(f"Column '{column_name}' does not exist in the DataFrame")

    return df

def add_datetime_column(df):
    # Convert dEven and hEven to strings and pad hEven to ensure it's 6 digits
    df['datetime'] = df.apply(lambda row: datetime.strptime(f"{row['dEven']}{str(row['hEven']).zfill(6)}", '%Y%m%d%H%M%S'), axis=1)
    return df