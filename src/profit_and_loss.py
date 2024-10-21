# سود و زیان
import re
import json
import pandas as pd
import xml.etree.ElementTree as ET
import requests
from pandas import DataFrame

from src.base_functions import make_url, get_data

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)


def extract_xml_tables(xml_content):
    root = ET.fromstring(xml_content)
    tables = []

    # Find all table elements and extract their data
    for table in root.findall('.//table'):
        table_data = []
        # Iterate over each row in the table
        for row in table.findall('tr'):
            row_data = []
            # Iterate over each cell in the row
            for cell in row.findall('td'):
                if cell.text:
                    row_data.append(cell.text)
            table_data.append(row_data)
        tables.append(table_data)

    return tables




def get_profit_and_loss_data(instrument_code: str) -> DataFrame:
    """
    Fetches and processes notification data from a remote API based on the provided instrument code.

    Args:
        instrument_code (str): The code of the financial instrument to fetch notifications for.

    Returns:
        dict: A dictionary containing processed notification data with cleaned column names and specific columns removed.

    Raises:
        ValueError: If any step in the process encounters a problem with the input data.
        ConnectionError: If there is an issue reaching the external API.
    """

    # Base URL for the API to fetch prepared data.
    base_url = "https://cdn.tsetmc.com/api/Codal/GetStatementContentByInsCode/6/6/1"

    # List of columns to remove from the final DataFrame as they are unnecessary.
    columns_to_remove = [
        "publishDateTime_Gregorian",
        'publishDateTime_DEven',
        'reportSubType',
        'pageID',
    ]

    try:
        # Step 1: Generate the complete API URL using the instrument code.
        api_url = make_url(base_url, instrument_code)
        # Step 2: Fetch the raw data from the API.
        req = requests.get(api_url)
        data = req.text
        cleaned_content = data.strip("'")

        # Now, attempt to parse the cleaned content as JSON
        data = json.loads(cleaned_content)

        # Convert the JSON to a Pandas DataFrame
        df = pd.json_normalize(data['statemetnContent'])
        df['content'] = df['content'].apply(extract_xml_tables)


        # Initialize tabels DataFrame
        tabels = pd.DataFrame(columns=['description', 'value', 'date', 'dateDesc'])

        # Function to check if the column is a JDate (e.g., 14xx/xx/xx)
        def is_jdate(column_name):
            return re.search(r'1\d{3}/\d{2}/\d{2}', column_name)

        # Iterate over rows of df
        for _, row in df.iterrows():
            # Convert row content to a DataFrame for easier handling
            try:
                sample = pd.DataFrame(row.content[0][1:], columns=row.content[0][0])

                # Find all columns that match the JDate pattern
                dateDesc = [col for col in sample.columns if is_jdate(col)]

                # Convert the date using api_date_converter
                date = row['publishDateTime_DEven']

                # Iterate over each row in the sample
                for _, srow in sample.iterrows():
                    # For each dateDesc, store the value separately in a new row
                    for i, date_col in enumerate(dateDesc):
                        # Create a new record for each value and dateDesc
                        tabels = pd.concat([tabels, pd.DataFrame({
                            'description': [srow['شرح']],  # Description remains the same
                            'value': [srow[date_col]],  # Store individual values
                            'date': [date],  # Converted date
                            'dateDesc': [date_col]  # Store individual dateDesc
                        })], ignore_index=True)
                        print(tabels)
            except:
                pass

        return tabels.to_dict(orient='index')

    # Handle common errors with meaningful messages.
    except ConnectionError:
        raise ConnectionError(
            "Failed to connect to the API. Please check your internet connection or the API URL.")

    except KeyError as e:
        raise ValueError(
            f"Key error in processing data: {e}. Ensure the required columns exist in the API response.")

    except Exception as e:
        raise ValueError(
            f"An unexpected error occurred: {e}. Please check your inputs and ensure everything is in order.")

get_profit_and_loss_data('33293588228706998')
