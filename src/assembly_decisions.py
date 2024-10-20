# تصمیمات مجمع
from src.base_functions import (
    make_url,
    get_data,
    data_to_js,
    js_to_df,
    remove_columns,
    df_to_js,
    rename_columns,
)


def get_assembly_decisions_data(instrument_code: str) -> dict:

    # Base URL for the API to fetch prepared data.
    base_url = "https://cdn.tsetmc.com/api/Codal/GetStatementContentByInsCode/14/0/-1"

    # List of columns to remove from the final DataFrame as they are unnecessary.
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
        data.to_csv('./majed.csv')
        data = df_to_js(data)
        return data

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


get_assembly_announcement_data('33293588228706998')
