from src.base_functions import (
    make_url,
    get_data,
    df_to_js,
)


def get_introduction_data(instrument_code: str) -> dict:
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
    base_url = "https://cdn.tsetmc.com/api/Codal/GetCodalPublisherBySymbol"

    # List of columns to remove from the final DataFrame as they are unnecessary.
    # columns_to_remove = [
    # ]
    try:
        # Step 1: Generate the complete API URL using the instrument code.
        api_url = make_url(base_url, instrument_code)

        # Step 2: Fetch the raw data from the API.
        data = get_data(api_url)

        # data = df_to_js(data)

        # Return the final JSON data after processing.
        return data

    # Handle common errors with meaningful messages.
    except ConnectionError:
        raise ConnectionError("Failed to connect to the API. Please check your internet connection or the API URL.")

    except KeyError as e:
        raise ValueError(f"Key error in processing data: {e}. Ensure the required columns exist in the API response.")

    except Exception as e:
        raise ValueError(
            f"An unexpected error occurred: {e}. Please check your inputs and ensure everything is in order.")
