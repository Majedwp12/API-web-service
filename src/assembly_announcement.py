import pandas as pd

from src.base_functions import (
    make_url,
    get_data,
    data_to_js,
    js_to_df,
    remove_columns,
    df_to_js,
    rename_columns,
    convert_datetime_in_dataframe
)
pd.set_option('display.max_columns',None)
def convert_xml(content):
    import xml.etree.ElementTree as ET
    import pandas as pd

    root = ET.fromstring(content)
    try:
        data = {
            "Type Code": root.find(".//Type").get("Code") if root.find(".//Type") is not None else None,
            "Title": root.find(".//Type").get("Title") if root.find(".//Type") is not None else None,
            "YearEndToDate": root.find(".//YearEndToDate").text if root.find(".//YearEndToDate") is not None else None,
            "Date": root.find(".//PlaceAndDateTime/Date").text if root.find(".//PlaceAndDateTime/Date") is not None else None,
            "Time": root.find(".//PlaceAndDateTime/Time").text if root.find(".//PlaceAndDateTime/Time") is not None else None,
            "Place": root.find(".//PlaceAndDateTime/Place").text if root.find(".//PlaceAndDateTime/Place") is not None else None,
            "Agenda": [item.text for item in root.findall(".//AgendaItem")] if root.findall(".//AgendaItem") else []
        }
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return None

    df = pd.DataFrame(data)  # Wrapped data in a list to ensure a single row
    return df




def get_assembly_announcement_data(instrument_code: str) -> dict:
    """
    Fetches and processes notification data from a remote API based on the provided instrument code.

    Args:
        instrument_code (str): The code of the financial instrument to fetch notifications for.

    Returns:
        dict: A dictionary containing processed notification data with cleaned column names and specific columns removed.
    """
    base_url = "https://cdn.tsetmc.com/api/Codal/GetStatementContentByInsCode/13/0/-1"
    columns_to_remove = [
        "publishDateTime_Gregorian",
        'publishDateTime_DEven',
        'reportSubType',
        'pageID',
    ]

    try:
        api_url = make_url(base_url, instrument_code)
        data = get_data(api_url)
        data = data_to_js(data, 'statemetnContent')
        data = js_to_df(data)
        data = remove_columns(data, columns_to_remove)
        column_renames = {"sentDateTime_Gregorian": "DateTime"}
        data = rename_columns(data, column_renames)
        data['Title_content'] = None
        data['Place_content'] = None
        data['datetime_content'] = None
        res_content = pd.DataFrame(columns=['Agenda', 'df_ID'])
        for index, row in data.iterrows():
            content = row['content']
            pars = convert_xml(content)
            pars = convert_datetime_in_dataframe(pars, date_column='Date', time_column='Time')
            pars = remove_columns(pars, ['YearEndToDate', 'Type Code'])
            data.at[index, 'Title_content'] = pars.loc[0, 'Title']
            data.at[index, 'Place_content'] = pars.loc[0, 'Place']
            data.at[index, 'datetime_content'] = pars.loc[0, 'datetime']
            pars['df_ID'] = index
            res_content = pd.concat([res_content, pars[['Agenda', 'df_ID']]], ignore_index=True)

        res_content = res_content.to_dict(orient='index')
        data = remove_columns(data, ['content'])
        data = data.to_dict(orient='index')
        return {
            'contents': data,
            'details': res_content
        }

    except ConnectionError:
        raise ConnectionError("Failed to connect to the API. Please check your internet connection or the API URL.")

    except KeyError as e:
        raise ValueError(e)

    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {e}. Please check your inputs and ensure everything is in order.")



get_assembly_announcement_data('33293588228706998')
