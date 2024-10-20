from fastapi import HTTPException, Query
import logging
from fastapi import HTTPException, Query, APIRouter
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional, Dict
from pydantic import BaseModel
from src.FinpyClassic import (
    get_tse_webid, get_price_history,
    get_ri_history, Get_Price_History,
    Get_CWI_History, Get_EWI_History,
    Get_IntradayTrades_History, Get_USD_RIAL,
    Build_Market_StockList, Get_MarketWatch,
    Get_60D_PriceHistory, Get_FFI_History,
    Get_CWPI_History, Get_EWPI_History,
    Get_MKT1I_History, Get_MKT2I_History,
    Get_INDI_History, Get_LCI30_History,
    Get_ACT50_History, Get_IntradayOB_History, Get_SectorIndex_History,
    Build_PricePanel, Get_ShareHoldersInfo

)
from src.change_status import get_change_status_data
from src.introduction import get_introduction_data
from src.notifications import get_notifications_data
from src.realـlegal import get_realـlegal_data
from src.shareholders import get_shareholders_data
from src.supervisor_message import get_supervisor_message_data
from src.statistics import get_statistics_data

app = FastAPI()
logging.basicConfig(level=logging.INFO)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/marketwatch", tags=["Market"], responses={
    200: {
        "description": "Market watch data retrieved successfully",
        "content": {
            "application/json": {
                "example": {
                    "final": [
                        {
                            "Ticker": "غمینو",
                            "Trade Type": "تابلو",
                            "Time": "11:37:58",
                            "Open": 4340.0,
                            "High": 4400.0,
                            "Low": 4326.0,
                            "Close": 4326.0,
                            "Final": 4370.0,
                            "Close(%)": -2.98,
                            "Final(%)": -2.0,
                            "Day_UL": 4592.0,
                            "Day_LL": 4326.0,
                            "Value": 10236424047.0,
                            "BQ-Value": 0,
                            "SQ-Value": 8675455572,
                            "BQPC": 0,
                            "SQPC": 542215973,
                            "Volume": 2360824.0,
                            "Vol_Buy_R": 606605.0,
                            "Vol_Buy_I": 1754219.0,
                            "Vol_Sell_R": 2119679.0,
                            "Vol_Sell_I": 241145.0,
                            "No": 630.0,
                            "No_Buy_R": 25.0,
                            "No_Buy_I": 4.0,
                            "No_Sell_R": 58.0,
                            "No_Sell_I": 2.0,
                            "Name": "شرکت صنایع غذایی مینو شرق",
                            "Market": "فرابورس",
                            "Sector": "محصولات غذایی و آشامیدنی به جز قند و شکر",
                            "Share-No": 2700000000.0,
                            "Base-Vol": 3264418.0,
                            "Market Cap": 11799000000000.0,
                            "EPS": 864.0,
                            "Download": "1403-07-29 11:45:09"
                        }
                    ]
                }
            }
        }
    },
    500: {"description": "Server error"}
})
async def api_get_marketwatch(
        save_excel: bool = Query(
            False, description="Save the output as Excel file"),
        save_path: str = Query('D:/FinPy-TSE Data/MarketWatch', description="Path to save the Excel file")):
    """
    Fetch the market watch data and optionally save it as an Excel file.

    - **save_excel**: Whether to save the data as an Excel file.
    - **save_path**: Path to save the file if `save_excel` is true.

    This API retrieves market watch data, processes it, and returns the result in JSON format.
    """
    logger.info(
        "Market watch data requested with save_excel=%s and save_path=%s", save_excel, save_path)

    try:
        # Fetch market data using Get_MarketWatch function
        df, ob = Get_MarketWatch(save_excel, save_path)

        # Fill missing values and reset indices for both dataframes
        logger.info("Processing DataFrames and replacing NaN values")
        df = df.fillna(value=None, method="ffill")
        df.reset_index(inplace=True)

        ob = ob.fillna(value=None, method="ffill")
        ob.reset_index(inplace=True)

        # Convert DataFrames to dictionary format
        final_df = {
            'final': df.to_dict(orient='records'),
            'orderbook': ob.to_dict(orient='records')
        }

        logger.info("Market watch data successfully retrieved and processed")
        return final_df

    except Exception as e:
        logger.error("Error retrieving market watch data: %s", str(e))
        raise HTTPException(status_code=500, detail="Server error: " + str(e))

@app.get("/GET/price-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved price history",
        "content": {"application/json": {
            "example": {
                "J-Date": "1400-01-07",
                "Date": "2021-03-27T00:00:00",
                "Open": 2520,
                "High": 2690,
                "Low": 2490,
                "Close": 2670,
                "Final": 2630,
                "Volume": 878226906,
                "Value": 2312728588060,
                "No": 28283,
                "Ticker": "خودرو",
                "Name": "ایران خودرو",
                "Market": "بورس"
            }
        }},
    },
    500: {"description": "Server error"}
})
async def api_get_price_history(
        stock: str = Query('خودرو', description="Stock symbol (in Persian)"),
        start_date: str = Query('1400-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query('1401-01-01', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        adjust_price: bool = Query(False, description="Adjust the price"),
        show_weekday: bool = Query(False, description="Show the weekday for each date"),
        double_date: bool = Query(True, description="Include both Jalali and Gregorian dates")):
    """
    Retrieve the price history for a stock.

    - **stock**: Stock symbol (e.g., خودرو).
    - **start_date**: Start date in Jalali calendar.
    - **end_date**: End date in Jalali calendar.
    - **ignore_date**: Whether to ignore the date range.
    - **adjust_price**: Whether to adjust the price.
    - **show_weekday**: Show the weekday for each date.
    - **double_date**: Include both Jalali and Gregorian dates.
    """
    logging.info(f"Fetching price history for stock: {stock}, start_date: {start_date}, end_date: {end_date}")
    
    try:
        # Fetching the price history based on provided parameters
        df = get_price_history(stock, start_date, end_date, ignore_date, adjust_price, show_weekday, double_date)
        
        # Resetting the index of the DataFrame for output clarity
        df.reset_index(inplace=True)
        
        logging.info(f"Successfully fetched price history for {stock}")
        return df.to_dict(orient='records')
    
    except Exception as e:
        logging.error(f"Error fetching price history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ app.get("/GET/price-history-alt", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved price history",
        "content": {"application/json": {"example": [
            {
                "J-Date": "1400-01-07",
                "Date": "2021-03-27T00:00:00",
                "Open": 2520,
                "High": 2690,
                "Low": 2490,
                "Close": 2670,
                "Final": 2630,
                "Volume": 878226906,
                "Value": 2312728588060,
                "No": 28283,
                "Ticker": "خودرو",
                "Name": "ایران خودرو",
                "Market": "بورس"
            }
        ]}}
    },
    500: {"description": "Server error"}
})
async def api_get_price_history_alt(
        stock: str = Query('خودرو', description="Stock symbol (in Persian)"),
        start_date: str = Query('1400-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query('1401-01-01', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        adjust_price: bool = Query(False, description="Adjust the price"),
        show_weekday: bool = Query(False, description="Show the weekday for each date"),
        double_date: bool = Query(True, description="Include both Jalali and Gregorian dates")):
    """
    Retrieve the price history for a stock.

    - **stock**: Stock symbol (e.g., خودرو).
    - **start_date**: Start date in Jalali calendar.
    - **end_date**: End date in Jalali calendar.
    - **ignore_date**: Whether to ignore the date range.
    - **adjust_price**: Whether to adjust the price.
    - **show_weekday**: Show the weekday for each date.
    - **double_date**: Include both Jalali and Gregorian dates.
    """
    # Logging input parameters for debugging purposes
    print(f"Fetching price history for stock: {stock}, from {start_date} to {end_date}, "
          f"ignore_date: {ignore_date}, adjust_price: {adjust_price}, "
          f"show_weekday: {show_weekday}, double_date: {double_date}")

    try:
        # Retrieve the price history data using the helper function
        df = Get_Price_History(stock, start_date, end_date,
                               ignore_date, adjust_price, show_weekday, double_date)

        # Resetting index to ensure the data frame can be properly converted to JSON
        df.reset_index(inplace=True)

        # Log successful data retrieval
        print(f"Successfully retrieved data for {stock} between {start_date} and {end_date}")

        # Returning the data as a JSON serializable format
        return df.to_dict(orient='records')

    except Exception as e:
        # Log the exception with detailed error message
        print(f"Error occurred while fetching price history: {str(e)}")

        # Raise HTTPException for internal server error (500) with the exception details
        raise HTTPException(status_code=500, detail=str(e))

@ app.post("/GET/60d-price-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved 60 days price history",
        "content": {
            "application/json": {
                "example": [
                    {
                        "Ticker": "خودرو",
                        "J-Date": "1403-05-01",
                        "Open": 2790,
                        "High": 2800,
                        "Low": 2732,
                        "Close": 2748,
                        "Final": 2762,
                        "Volume": 81959964,
                        "Value": 226353248512,
                        "No": 2463,
                        "Adj Open": 2790,
                        "Adj High": 2800,
                        "Adj Low": 2732,
                        "Adj Close": 2748,
                        "Adj Final": 2762
                    }
                ]
            }
        }
    },
    500: {
        "description": "Server error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error message"}
            }
        }
    }
})
async def api_get_60d_price_history(
    stock_list: List[str] = Query(
        default=['خودرو', 'فولاد'], description="List of stock symbols to fetch price history for"
    ),
    adjust_price: bool = Query(
        default=True, description="Whether to adjust prices"
    ),
    show_progress: bool = Query(
        default=True, description="Whether to show progress during data fetching"
    )
):
    """
    Fetch the last 60 days of price history for a given list of stocks.

    Parameters:
    - **stock_list**: List of stock symbols (e.g., ['خودرو', 'فولاد'])
    - **adjust_price**: Set to `True` to adjust prices, `False` otherwise
    - **show_progress**: Set to `True` to display progress during data fetching
    - **save_excel**: Set to `True` to save the output in an Excel file (optional)
    - **save_path**: Provide a file path to save the Excel file if `save_excel` is `True` (optional)

    Returns a JSON object with the price history for each stock.
    """

    try:
        df = Get_60D_PriceHistory(
            stock_list,
            adjust_price,
            show_progress
        )
        df = df[0]  # Assuming df[0] is the relevant data
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/tse-webid",
         tags=["Market"],
         summary="Retrieve TSE WebID",
         description="Fetch the TSE WebID for a specific stock symbol in Persian.",
         responses={
             200: {
                 "description": "Successfully retrieved TSE WebID",
                 "content": {
                     "application/json": {
                         "example": [
                             {
                                 "Ticker": "پترول",
                                 "Active": 1,
                                 "Name": "گ.س.وت.ص.پتروشیمی خلیج فارس",
                                 "WebID": "69143674941561637",
                                 "Market": "بورس"
                             }
                         ]
                     }
                 }
             },
             400: {"description": "Invalid stock symbol"},
             500: {"description": "Internal Server Error"}
         })
async def api_get_tse_webid(stock: str = Query('پترول', description="Stock symbol in Persian (e.g., پترول)")):
    """
    API endpoint to retrieve the TSE WebID for a specific stock.

    - **stock**: Stock symbol in Persian (e.g., پترول).
    """
    try:
        # Log the incoming request
        logger.info(f"Fetching TSE WebID for stock: {stock}")

        # Call the function to get the TSE WebID
        df = get_tse_webid(stock)

        # Log the successful data retrieval
        logger.info(f"Data successfully retrieved for stock: {stock}")

        # Reset index for better JSON formatting
        df.reset_index(inplace=True)

        # Log the data being returned
        logger.debug(f"Returning data: {df.to_dict(orient='records')}")

        # Return the DataFrame as a list of dictionaries
        return df.to_dict(orient='records')

    except Exception as e:
        # Log the error details
        logger.error(
            f"Error fetching TSE WebID for stock: {stock}, Error: {str(e)}")

        # Raise a 500 HTTP Exception in case of an error
        raise HTTPException(status_code=500, detail=str(e))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/build-market-stocklist", tags=["Market"], responses={
    200: {
        "description": "Successfully built the market stock list",
        "content": {"application/json": {
            "example": [
                {
                    "Ticker": "آباد",
                    "Name": "توریستی ورفاهی آبادگران ایران",
                    "Market": "بورس",
                    "Panel": "بازار اول (تابلوی فرعی) بورس",
                    "Sector": "هتل و رستوران",
                    "Sub-Sector": "هتل ها ، اردو و دیگر تدارکات اقامت کوتاه",
                    "Comment": "-",
                    "Name(EN)": "Abadgaran",
                    "Company Code(12)": "IRO1ABAD0002",
                    "Ticker(4)": "ABAD",
                    "Ticker(5)": "ABAD1",
                    "Ticker(12)": "IRO1ABAD0001",
                    "Sector Code": "55",
                    "Sub-Sector Code": "5510",
                    "Panel Code": "3"
                },
            ]
        }}
    },
    500: {"description": "Server error"}
})
async def api_build_market_stocklist(
        bourse: bool = Query(True, description="Include Bourse stocks"),
        farabourse: bool = Query(
            True, description="Include Farabourse stocks"),
        payeh: bool = Query(True, description="Include Payeh stocks"),
        detailed_list: bool = Query(
            True, description="Return a detailed stock list"),
        show_progress: bool = Query(
            True, description="Show progress while fetching data"),
        save_excel: bool = Query(
            False, description="Save the stock list as an Excel file"),
        save_csv: bool = Query(
            False, description="Save the stock list as a CSV file"),
        save_path: str = Query('D:/FinPy-TSE Data/', description="Path to save the file if required")):
    """
    Build a stock list from the market.

    - **bourse**: Include stocks from the Bourse market.
    - **farabourse**: Include stocks from the Farabourse market.
    - **payeh**: Include Payeh stocks.
    - **detailed_list**: Return a detailed stock list.
    - **show_progress**: Show progress while fetching data.
    - **save_excel**: Save the stock list as an Excel file.
    - **save_csv**: Save the stock list as a CSV file.
    - **save_path**: The path where the file will be saved if required.
    """
    try:
        # Log input parameters for debugging
        logger.info("Fetching stock list with the following parameters:")
        logger.info(
            f"Bourse: {bourse}, Farabourse: {farabourse}, Payeh: {payeh}")
        logger.info(
            f"Detailed list: {detailed_list}, Show progress: {show_progress}")
        logger.info(
            f"Save Excel: {save_excel}, Save CSV: {save_csv}, Save path: {save_path}")

        # Call the function to build the market stock list
        df = Build_Market_StockList(
            bourse, farabourse, payeh, detailed_list, show_progress)
        df.reset_index(inplace=True)

        # Log success message
        logger.info("Successfully built the stock list")

        # Return the result as JSON
        return df.to_dict(orient='records')

    except Exception as e:
        # Log the error before raising it
        logger.error(f"Error occurred while building stock list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/ri-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved RI history",
        "content": {
            "application/json": {
                "example": [
                    {
                        "J-Date": "1400-01-07",
                        "No_Buy_R": 9497,
                        "No_Buy_I": 5,
                        "No_Sell_R": 10505,
                        "No_Sell_I": 12,
                        "Vol_Buy_R": 855400896,
                        "Vol_Buy_I": 22826010,
                        "Vol_Sell_R": 787008406,
                        "Vol_Sell_I": 91218500,
                        "Val_Buy_R": 2251817698700,
                        "Val_Buy_I": 60910889360,
                        "Val_Sell_R": 2068262590490,
                        "Val_Sell_I": 244465997570,
                        "Ticker": "خودرو",
                        "Name": "ایران خودرو",
                        "Market": "بورس"
                    }
                ]
            }
        }
    },
    500: {
        "description": "Internal server error occurred"
    }
})
async def api_get_ri_history(
        stock: str = Query('خودرو', description="Stock symbol (in Persian)"),
        start_date: str = Query(
            '1400-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1401-01-01', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        show_weekday: bool = Query(
            False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Include both Jalali and Gregorian dates")):
    """
    Retrieve the Relative Index (RI) history for a given stock within a specified date range.

    Parameters:
    - **stock**: The stock symbol (e.g., خودرو).
    - **start_date**: The start date in the Jalali calendar (yyyy-mm-dd).
    - **end_date**: The end date in the Jalali calendar (yyyy-mm-dd).
    - **ignore_date**: If True, fetch all records ignoring the date range.
    - **show_weekday**: If True, shows the weekday for each date.
    - **double_date**: If True, includes both Jalali and Gregorian dates in the output.

    Returns:
    - A list of RI history records with fields like No_Buy_R, No_Sell_R, Vol_Buy_R, Val_Sell_R, etc.
    Example:
    {
        "J-Date": "1400-01-07",
        "No_Buy_R": 9497,      # Number of retail buyers
        "No_Buy_I": 5,         # Number of institutional buyers
        "No_Sell_R": 10505,    # Number of retail sellers
        "No_Sell_I": 12,       # Number of institutional sellers
        "Vol_Buy_R": 855400896, # Volume bought by retail buyers
        "Vol_Buy_I": 22826010,  # Volume bought by institutional buyers
        "Vol_Sell_R": 787008406, # Volume sold by retail sellers
        "Vol_Sell_I": 91218500,  # Volume sold by institutional sellers
        "Val_Buy_R": 2251817698700, # Value bought by retail buyers (in local currency)
        "Val_Buy_I": 60910889360,   # Value bought by institutional buyers (in local currency)
        "Val_Sell_R": 2068262590490, # Value sold by retail sellers (in local currency)
        "Val_Sell_I": 244465997570,  # Value sold by institutional sellers (in local currency)
        "Ticker": "خودرو",      # Stock ticker
        "Name": "ایران خودرو",   # Company name
        "Market": "بورس"         # Market (بورس means stock exchange)
    }
    """
    logging.info(
        f"Fetching RI history for {stock} from {start_date} to {end_date}")

    try:
        # Fetching data from the function (assumed to be implemented elsewhere)
        df = get_ri_history(stock, start_date, end_date,
                            ignore_date, show_weekday, double_date)
        df.reset_index(inplace=True)

        logging.info("RI history fetched successfully")

        return df.to_dict(orient='records')
    except Exception as e:
        # Log the error
        logging.error(f"Error fetching RI history for {stock}: {str(e)}")

        # Raise HTTP 500 error with details
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching the RI history")

# Initialize a logger
logger = logging.getLogger("api_logger")


@app.get("/GET/cwi-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved CWI history",
        "content": {
            "application/json": {
                "example": [{
                    "J-Date": "1395-01-07",
                    "Open": 80133.0,
                    "High": 81200.0,
                    "Low": 80133.0,
                    "Close": 81200.0,
                    "Adj Close": 81200.3,
                    "Volume": 785545121
                }]
            }
        }
    },
    400: {"description": "Bad Request - Invalid input data or date format"},
    500: {"description": "Server error"}
})
async def api_get_cwi_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(
            False, description="Use only adjusted close prices"),
        show_weekday: bool = Query(
            False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Include both Jalali and Gregorian dates")):
    """
    Retrieve the Capital Weighted Index (CWI) history.

    Parameters:
    - **start_date**: The start date for fetching the CWI history in Jalali (Persian) calendar format.
    - **end_date**: The end date for fetching the CWI history in Jalali (Persian) calendar format.
    - **ignore_date**: If true, the date range will be ignored and all data will be fetched.
    - **just_adj_close**: If true, only adjusted close prices will be returned.
    - **show_weekday**: If true, the weekday for each date will be shown.
    - **double_date**: If true, both Jalali and Gregorian dates will be included.

    Returns:
    - A list of records containing CWI history data for each date.
    """
    try:
        # Ensure valid date format
        if not is_valid_jalali_date(start_date) or not is_valid_jalali_date(end_date):
            raise ValueError(
                "Invalid date format. Dates must be in Persian format (yyyy-mm-dd).")

        # Call the Get_CWI_History function with the required parameters
        df = Get_CWI_History(start_date, end_date, ignore_date,
                             just_adj_close, show_weekday, double_date)

        if df.empty:
            raise ValueError(
                "No data found for the provided date range or parameters.")

        # Reset index to ensure the data is well-formatted
        df.reset_index(inplace=True)

        return df.to_dict(orient='records')

    except ValueError as ve:
        # Handle invalid date formats or data issues
        logger.error(f"ValueError occurred: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except ConnectionError as ce:
        # Handle connection-related issues (e.g., network failure)
        logger.error(f"ConnectionError occurred: {str(ce)}")
        raise HTTPException(
            status_code=500, detail="Connection error. Please try again later.")

    except Exception as e:
        # Log and handle any unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An internal server error occurred. Please try again later.")


def is_valid_jalali_date(date_str: str) -> bool:
    """
    Validate if a given string is in the correct Jalali (Persian) date format (yyyy-mm-dd).
    """
    try:
        year, month, day = map(int, date_str.split('-'))
        # Simple check for year, month, and day ranges
        return 1300 <= year <= 1500 and 1 <= month <= 12 and 1 <= day <= 31
    except ValueError:
        return False


@app.get("/GET/ewi-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved EWI history",
        "content": {
            "application/json": {
                "example": [{
                    "J-Date": "1395-01-07",
                    "Open": 13347.0,
                    "High": 13450.0,
                    "Low": 13334.0,
                    "Close": 13450.0,
                    "Adj Close": 13450.1,
                    "Volume": 785545121
                }]
            }
        }
    },
    400: {"description": "Bad Request - Invalid input data or date format"},
    500: {"description": "Server error"}
})
async def api_get_ewi_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),

        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(
            False, description="Use only adjusted close prices"),
        show_weekday: bool = Query(
            False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Include both Jalali and Gregorian dates")):
    """
    Retrieve the Equal Weighted Index (EWI) history.

    Parameters:
    - **start_date**: The start date for fetching the EWI history in Jalali (Persian) calendar format.
    - **end_date**: The end date for fetching the EWI history in Jalali (Persian) calendar format.
    - **ignore_date**: If true, the date range will be ignored and all data will be fetched.
    - **just_adj_close**: If true, only adjusted close prices will be returned.
    - **show_weekday**: If true, the weekday for each date will be shown.
    - **double_date**: If true, both Jalali and Gregorian dates will be included.

    Returns:
    - A list of records containing EWI history data for each date.
    """
    try:
        # Validate date format
        if not is_valid_jalali_date(start_date) or not is_valid_jalali_date(end_date):
            raise ValueError(
                "Invalid date format. Dates must be in Persian format (yyyy-mm-dd).")

        # Fetch EWI history based on the provided parameters
        df = Get_EWI_History(start_date, end_date, ignore_date,
                             just_adj_close, show_weekday, double_date)

        if df.empty:
            raise ValueError(
                "No data found for the provided date range or parameters.")

        df.reset_index(inplace=True)
        return df.to_dict(orient='records')

    except ValueError as ve:
        # Handle invalid date formats or missing data
        logger.error(f"ValueError occurred: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except ConnectionError as ce:
        # Handle connection issues (e.g., network failure)
        logger.error(f"ConnectionError occurred: {str(ce)}")
        raise HTTPException(
            status_code=500, detail="Connection error. Please try again later.")

    except Exception as e:
        # Catch any unexpected errors and log them
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An internal server error occurred. Please try again later.")


@app.get("/GET/intraday-trades-history", tags=["Trades"], responses={
    200: {
        "description": "Successfully retrieved intraday trades history",
        "content": {
            "application/json": {
                "example": [{
                    "J-Date": "1400-09-15",
                    "Time": "09:00:15",
                    "Volume": 20000,
                    "Price": 4240
                }]
            }
        }
    },
    400: {"description": "Bad Request - Invalid input or date format"},
    500: {"description": "Server error"}
})
async def api_get_intraday_trades_history(
        stock: str = Query('وخارزم', description="Stock symbol (in Persian)"),
        start_date: str = Query(
            '1400-09-15', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        jalali_date: bool = Query(True, description="Use Jalali date format"),
        combined_datatime: bool = Query(
            False, description="Combine date and time"),
        show_progress: bool = Query(True, description="Show progress during fetching")):
    """
    Retrieve intraday trades history for a given stock symbol.

    Parameters:
    - **stock**: The stock symbol (in Persian) for which to retrieve intraday trades.
    - **start_date**: The start date in Jalali (Persian) format (yyyy-mm-dd).
    - **end_date**: The end date in Jalali (Persian) format (yyyy-mm-dd).
    - **jalali_date**: If true, returns dates in the Jalali calendar format.
    - **combined_datatime**: If true, combines date and time into one field.
    - **show_progress**: If true, displays progress during data fetching.

    Returns:
    - A list of records with trade history including date, time, volume, and price.
    """
    try:
        # Ensure valid date format
        if not is_valid_jalali_date(start_date) or not is_valid_jalali_date(end_date):
            raise ValueError(
                "Invalid date format. Dates must be in Persian format (yyyy-mm-dd).")

        # Call the Get_IntradayTrades_History function with the required parameters
        df = Get_IntradayTrades_History(
            stock, start_date, end_date, jalali_date, combined_datatime, show_progress)

        if df.empty:
            raise ValueError(
                f"No intraday trades found for stock '{stock}' between {start_date} and {end_date}.")

        # Reset index to ensure the data is well-formatted
        df.reset_index(inplace=True)

        return df.to_dict(orient='records')

    except ValueError as ve:
        # Handle invalid date formats or data issues
        logger.error(f"ValueError occurred: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except ConnectionError as ce:
        # Handle connection-related issues (e.g., network failure)
        logger.error(f"ConnectionError occurred: {str(ce)}")
        raise HTTPException(
            status_code=500, detail="Connection error. Please try again later.")

    except Exception as e:
        # Log and handle any unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An internal server error occurred. Please try again later.")


@app.get("/GET/usd-rial", tags=["Currency"], responses={
    200: {
        "description": "Successfully retrieved USD to Rial exchange rate history",
        "content": {"application/json": {"example": [{"date": "1400-01-01", "rate": 250000}]}}
    },
    500: {"description": "Server error"}})
async def api_get_usd_rial(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        show_weekday: bool = Query(
            False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Include both Jalali and Gregorian dates")):
    """
    Retrieve the USD to Rial exchange rate history.

    - **start_date**: Start date in Jalali calendar.
    - **end_date**: End date in Jalali calendar.
    - **ignore_date**: Whether to ignore the date range.
    - **show_weekday**: Show the weekday for each date.
    - **double_date**: Include both Jalali and Gregorian dates.
    """
    try:
        df = Get_USD_RIAL(start_date, end_date, ignore_date,
                          show_weekday, double_date)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except ConnectionError as e:
        # Handle connection errors and raise a 500 error
        raise HTTPException(status_code=500, detail=str(e))

    except ValueError as e:
        # Handle value-related errors and raise a 500 error
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        # Catch-all for other unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/supervisor-message-data",
         tags=["message"],
         summary="Retrieve Supervisor Message Data",
         description="Fetch supervisor message data for a given instrument code.",
         responses={
             200: {
                 "description": "Successfully retrieved supervisor message data",
                 "content": {
                     "application/json": {
                         "example": [
                             {
                                 "tseMsgIdn": 196411,
                                 "tseTitle": "text",
                                 "tseDesc": "text",
                                 "datetime": "2024-10-12T08:00:56"
                             }
                         ]
                     }
                 }
             },
             400: {"description": "Invalid instrument code"},
             500: {"description": "Internal Server Error"}
         })
async def api_get_supervisor_message_data(
        instrument_code: str = Query('33293588228706998', description="Code of the company")):
    """
    API endpoint to retrieve supervisor message data for the provided company instrument code.

    - **instrument_code**: The unique instrument code of the company (e.g., '33293588228706998')
    """
    try:
        # Log the start of the request
        logger.info(
            f"Fetching supervisor message data for instrument code: {instrument_code}")

        # Call the data retrieval function
        data = get_supervisor_message_data(instrument_code)

        # Log the successful data retrieval
        logger.info(
            f"Successfully retrieved data for instrument code: {instrument_code}")

        return data

    except Exception as e:
        # Log any exceptions
        logger.error(
            f"Error retrieving supervisor message data for instrument code: {instrument_code}, Error: {str(e)}")

        # Raise an HTTP exception with a 500 status code
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/FFI-history", tags=["FFI History"], responses={
    200: {
        "description": "Successful response with the FFI history",
        "content": {
            "application/json": {
                "example": [
                    {
                        "J-Date": "1395-01-07",
                        "Open": 90000.0,
                        "High": 92000.0,
                        "Low": 89000.0,
                        "Close": 92000.0,
                        "Adj Close": 92000.0,
                        "Volume": 100000000
                    }
                ]
            }
        }
    },
    500: {
        "description": "Internal server error"
    }
})
async def api_get_ffi_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(
            False, description="If True, ignores the date range"),
        just_adj_close: bool = Query(False, description="If True, only shows the adjusted close values")):
    """
    Fetches the FFI (Fund Flow Index) history for a given date range.

    Parameters:
    - start_date: Start date in Persian calendar (yyyy-mm-dd)
    - end_date: End date in Persian calendar (yyyy-mm-dd)
    - ignore_date: Option to fetch all records, ignoring the date range.
    - just_adj_close: Option to return only the adjusted close prices.

    Returns:
    - List of FFI records with Open, High, Low, Close, and Adjusted Close prices.
    """
    logging.info(f"Fetching FFI history from {start_date} to {end_date}")

    try:
        # Fetching data from the function (assumed to be implemented elsewhere)
        df = Get_FFI_History(start_date, end_date, ignore_date, just_adj_close)
        df.reset_index(inplace=True)

        logging.info("FFI history fetched successfully")

        return df.to_dict(orient='records')
    except Exception as e:
        # Log the error with details
        logging.error(f"Error fetching FFI history: {str(e)}")

        # Raise HTTP 500 error with a detailed message
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching the FFI history")


@app.get("/GET/CWPI-history", tags=["CWPI History"], responses={
    200: {
        "description": "Successful response with the CWPI history",
        "content": {
            "application/json": {
                "example": [
                    {
                        "J-Date": "1395-01-07",
                        "Open": 30000.0,
                        "High": 30500.0,
                        "Low": 29500.0,
                        "Close": 30500.0,
                        "Adj Close": 30500.5,
                        "Volume": 100000000
                    }
                ]
            }
        }
    },
    500: {
        "description": "Internal server error"
    }})
async def api_get_CWPI_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(
            False, description="If True, ignores the date range"),
        just_adj_close: bool = Query(
            False, description="If True, only shows the adjusted close values"),
        show_weekday: bool = Query(
            False, description="If True, shows the weekday for each date"),
        double_date: bool = Query(False, description="If True, includes both Persian and Gregorian dates")):
    """
    Fetches the CWPI (Consumer Price Index) history for a given date range.

    Parameters:
    - start_date: Start date in Persian calendar (yyyy-mm-dd)
    - end_date: End date in Persian calendar (yyyy-mm-dd)
    - ignore_date: Option to fetch all records, ignoring the date range.
    - just_adj_close: Option to return only the adjusted close prices.
    - show_weekday: Option to show the weekday for each date.
    - double_date: Option to show both Persian and Gregorian dates.

    Returns:
    - List of CWPI records with Open, High, Low, Close, and Adjusted Close prices.
    """
    logging.info(f"Fetching CWPI history from {start_date} to {end_date}")

    try:
        # Fetching data from the function (assumed to be implemented elsewhere)
        df = Get_CWPI_History(start_date, end_date, ignore_date,
                              just_adj_close, show_weekday, double_date)
        df.reset_index(inplace=True)

        logging.info("CWPI history fetched successfully")

        return df.to_dict(orient='records')
    except Exception as e:
        # Log the error with details
        logging.error(f"Error fetching CWPI history: {str(e)}")

        # Raise HTTP 500 error with a detailed message
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching the CWPI history")


@app.get("/GET/EWPI-history", tags=[""], responses={
    200: {
        "description": "",
        "content": {"application/json": {"example": [{
            "J-Date": "1395-01-07",
            "Open": 11194.0,
            "High": 11280.0,
            "Low": 11183.0,
            "Close": 11280.0,
            "Adj Close": 11280.3,
            "Volume": 785545121
        }]}}
    },
    500: {"description": ""}})
async def api_get_EWPI_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(
            False, description="Show the weekday for each date"),
        show_weekday: bool = Query(False, description=''),
        double_date: bool = Query(False, description=''),):
    try:
        df = Get_EWPI_History(start_date, end_date, ignore_date,
                              just_adj_close, show_weekday, double_date)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/MKT1I-history", tags=["Market Index"], responses={
    200: {
        "description": "History of MKT1I (First Market Index)",
        "content": {
            "application/json": {
                "example": [
                    {
                        "J-Date": "1395-01-07",
                        "Open": 57000.0,
                        "High": 58000.0,
                        "Low": 57000.0,
                        "Close": 58000.0,
                        "Adj Close": 57999.9,
                        "Volume": 600000000
                    }
                ]
            }
        }
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_MKT1I_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(
            False, description="If True, ignores the date range"),
        just_adj_close: bool = Query(
            False, description="If True, only shows the adjusted close values"),
        show_weekday: bool = Query(
            False, description="If True, shows the weekday for each date"),
        double_date: bool = Query(False, description="If True, shows both Persian and Gregorian dates")):
    """
    API endpoint to retrieve MKT1I history (First Market Index).

    Parameters:
    - start_date: Start date in Persian calendar (yyyy-mm-dd)
    - end_date: End date in Persian calendar (yyyy-mm-dd)
    - ignore_date: Option to fetch all records, ignoring the date range.
    - just_adj_close: Option to return only the adjusted close prices.
    - show_weekday: Option to show the weekday for each date.
    - double_date: Option to show both Persian and Gregorian dates.

    Returns:
    - List of MKT1I (First Market Index) records with Open, High, Low, Close, and Adjusted Close prices.
    """
    logging.info(f"Fetching MKT1I history from {start_date} to {end_date}")

    try:
        # Call the original function with the query parameters
        df = Get_MKT1I_History(
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # Reset index to make sure J-Date is part of the response
        df.reset_index(inplace=True)

        logging.info("MKT1I history fetched successfully")

        return df.to_dict(orient='records')

    except Exception as e:
        logging.error(f"Error fetching MKT1I history: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching the MKT1I history")


@app.get("/GET/MKT2I-history", tags=["Market Index"], responses={
    200: {
        "description": "History of MKT2I (Second Market Index)",
        "content": {
            "application/json": {
                "example": [{
                    "J-Date": "1400-12-29",
                    "Date": "2024-03-20",
                    "Weekday": "Wednesday",
                    "Open": 12345.67,
                    "High": 13000.00,
                    "Low": 12000.00,
                    "Close": 12500.00,
                    "Adj Close": 12450.75,
                    "Volume": 1000000
                }]
            }
        }
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_MKT2I_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(
            False, description="Show only the adjusted close price"),
        show_weekday: bool = Query(
            False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Show both Gregorian and Jalali dates")):
    """
    API endpoint to retrieve MKT2I (Second Market Index) history.

    Parameters:
    - start_date: Start date in Persian calendar (yyyy-mm-dd)
    - end_date: End date in Persian calendar (yyyy-mm-dd)
    - ignore_date: Option to fetch all records, ignoring the date range.
    - just_adj_close: Option to return only the adjusted close prices.
    - show_weekday: Option to show the weekday for each date.
    - double_date: Option to show both Persian and Gregorian dates.

    Returns:
    - List of MKT2I records with Open, High, Low, Close, and Adjusted Close prices.
    """
    logging.info(f"Fetching MKT2I history from {start_date} to {end_date}")

    try:
        # Fetching data using the Get_MKT2I_History function (assumed to be implemented elsewhere)
        df = Get_MKT2I_History(
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # Ensure the DataFrame index is reset to be part of the JSON response
        df.reset_index(inplace=True)

        logging.info("MKT2I history fetched successfully")

        # Return the data as a list of dictionaries (JSON)
        return df.to_dict(orient='records')

    except Exception as e:
        # Log the error for debugging
        logging.error(f"Error fetching MKT2I history: {str(e)}")

        # Raise an HTTP 500 error with a detailed message
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching the MKT2I history")


@app.get("/GET/INDI-history", tags=["Industry Index"], responses={
    200: {
        "description": "History of INDI (Industry Index) with open, close, high, low, and adjusted close prices",
        "content": {
            "application/json": {
                "example": [
                    {
                        "J-Date": "1395-01-07",
                        "Open": 67000.0,
                        "High": 67500.0,
                        "Low": 66500.0,
                        "Close": 67500.0,
                        "Adj Close": 67550.0,
                        "Volume": 500000000
                    }
                ]
            }
        }
    },
    500: {
        "description": "Internal Server Error"
    }
})
async def api_get_INDI_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(
            False, description="Ignore the date range and fetch all records"),
        just_adj_close: bool = Query(
            False, description="Return only the adjusted close prices"),
        show_weekday: bool = Query(
            False, description="Include the weekday for each date in the response"),
        double_date: bool = Query(
            False, description="Include both Gregorian and Jalali dates in the response")):
    """
    Fetches the history of INDI (Industry Index) for the specified date range.

    Parameters:
    - start_date: Start date in Persian format (yyyy-mm-dd)
    - end_date: End date in Persian format (yyyy-mm-dd)
    - ignore_date: If True, ignore the date range and return all records.
    - just_adj_close: If True, return only the adjusted close prices.
    - show_weekday: If True, include the weekday for each date in the response.
    - double_date: If True, include both Gregorian and Jalali dates.

    Returns:
    - List of records containing Open, High, Low, Close, Adjusted Close, and Volume.
    """
    logging.info(f"Fetching INDI history from {start_date} to {end_date}")

    try:
        # Fetch data using the provided query parameters
        df = Get_INDI_History(
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # Convert the DataFrame to a dictionary with records
        df.reset_index(inplace=True)
        logging.info(
            f"Successfully fetched INDI history for {len(df)} records.")
        return df.to_dict(orient='records')

    except Exception as e:
        # Log the error and raise a 500 HTTP error
        logging.error(f"Error fetching INDI history: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching the INDI history")


@app.get("/GET/LCI30-history", tags=["Market Index"], responses={
    200: {
        "description": "History of LCI30 (30 Large-Cap Index)",
        "content": {
            "application/json": {
                "example": [
                    {
                        "J-Date": "1395-01-07",    # Jalali date
                        # Gregorian date (if double_date is True)
                        "Date": "2024-03-20",
                        # Weekday (if show_weekday is True)
                        "Weekday": "Wednesday",
                        "Open": 3379.0,           # Opening price
                        "High": 3454.0,           # Highest price
                        "Low": 3379.0,            # Lowest price
                        "Close": 3454.0,          # Closing price
                        "Adj Close": 3454.2,      # Adjusted closing price
                        "Volume": 290228382       # Volume traded
                    }
                ]
            }
        }
    },
    500: {
        "description": "Internal Server Error"
    }
})
async def api_get_LCI30_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(
            False, description="Show only the adjusted close price"),
        show_weekday: bool = Query(
            False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Show both Gregorian and Jalali dates")):
    """
    Retrieve the historical data for the LCI30 (30 Large-Cap Index) within a specified date range.

    Parameters:
    - **start_date**: The start date in the Jalali calendar (yyyy-mm-dd).
    - **end_date**: The end date in the Jalali calendar (yyyy-mm-dd).
    - **ignore_date**: If True, fetch all records ignoring the date range.
    - **just_adj_close**: If True, show only the adjusted close prices.
    - **show_weekday**: If True, includes the weekday in the output.
    - **double_date**: If True, includes both Jalali and Gregorian dates in the output.

    Returns:
    - A list of LCI30 historical records with fields such as 'J-Date', 'Open', 'Close', 'Adj Close', etc.
    """
    logging.info(f"Fetching LCI30 history from {start_date} to {end_date}")

    try:
        # Fetching the LCI30 history data using the provided parameters
        df = Get_LCI30_History(
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # Reset the index to ensure proper formatting in the output
        df.reset_index(inplace=True)

        logging.info("LCI30 history fetched successfully")

        # Return the data as a dictionary
        return df.to_dict(orient='records')

    except Exception as e:
        # Log the error message
        logging.error(f"Error fetching LCI30 history: {str(e)}")

        # Raise HTTP 500 error with detailed error message
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching the LCI30 history")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/ACT50-history",
         tags=["Market Index"],
         responses={
             200: {
                 "description": "History of ACT50 (50 Most Active Stocks Index)",
                 "content": {
                     "application/json": {
                         "example": [
                             {
                                 "J-Date": "1400-12-29",
                                 "Date": "2024-03-20",
                                 "Weekday": "Wednesday",
                                 "Open": 12345.67,
                                 "High": 13000.00,
                                 "Low": 12000.00,
                                 "Close": 12500.00,
                                 "Adj Close": 12450.75,
                                 "Volume": 1000000
                             }
                         ]
                     }
                 }
             },
             500: {"description": "Internal Server Error"}
         }
         )
async def api_get_ACT50_history(
    start_date: str = Query(
        '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
    end_date: str = Query(
        '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
    ignore_date: bool = Query(
        False, description="Ignore the date range and fetch all data"),
    just_adj_close: bool = Query(
        False, description="Return only the adjusted close price"),
    show_weekday: bool = Query(
        False, description="Include the weekday of each date"),
    double_date: bool = Query(
        False, description="Include both Jalali and Gregorian dates")
):
    """
    API endpoint to retrieve the historical data for the ACT50 index (50 Most Active Stocks).
    Allows filtering based on date range and other options such as showing only adjusted close price, 
    showing the weekday, or including both Jalali and Gregorian dates.

    Parameters:
    - **start_date**: Start date in Jalali format (default: '1395-01-01')
    - **end_date**: End date in Jalali format (default: '1400-12-29')
    - **ignore_date**: Boolean flag to ignore the date range and retrieve all data
    - **just_adj_close**: Boolean flag to return only the adjusted close prices
    - **show_weekday**: Boolean flag to include the weekday for each date
    - **double_date**: Boolean flag to include both Jalali and Gregorian dates

    Returns:
    - JSON object containing historical data for the ACT50 index, with keys such as 'J-Date', 'Open', 'High', 
      'Low', 'Close', 'Adj Close', and 'Volume'.
    """
    try:
        # Log incoming request
        logger.info(f"Fetching ACT50 history with start_date={start_date}, end_date={end_date}, "
                    f"ignore_date={ignore_date}, just_adj_close={just_adj_close}, show_weekday={show_weekday}, "
                    f"double_date={double_date}")

        # Call to retrieve the data
        df = Get_ACT50_History(
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # If the result is a pandas DataFrame, convert it to JSON-compatible format
        df.reset_index(inplace=True)  # Ensure 'J-Date' is part of the JSON
        result = df.to_dict(orient='records')

        # Log the successful response
        logger.info(f"Successfully fetched {len(result)} records.")
        return result

    except Exception as e:
        # Log the error
        logger.error(f"Error fetching ACT50 history: {str(e)}")

        # Return a 500 response with the error message
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching ACT50 history.")

logger = logging.getLogger(__name__)


@app.get("/GET/statistics-data",
         tags=["Market Data"],
         summary="Retrieve Statistics Data",
         description="Fetch statistical data for the provided financial instrument code.",
         responses={
             200: {
                 "description": "Statistics data for the provided instrument code",
                 "content": {
                     "application/json": {
                         "example": {
                             "instrument_code": "123456",
                             "column1": "value1",
                             "column2": "value2",
                             # Add more fields as per the expected output format
                         }
                     }
                 }
             },
             400: {"description": "Bad Request: Invalid input or processing error"},
             500: {"description": "Internal Server Error: API connection failed"}
         })
async def api_get_statistics_data(
        instrument_code: str = Query('33293588228706998', description="The code of the financial instrument to fetch data for")):
    """
    API endpoint to fetch and process statistics data for a given financial instrument code.

    - **instrument_code**: The unique code of the financial instrument (e.g., '33293588228706998').
    """
    try:
        # Log the start of the data fetch operation
        logger.info(
            f"Fetching statistics data for instrument_code: {instrument_code}")

        # Call the original function to get the statistics data
        result = get_statistics_data(instrument_code)

        # Log the success of data retrieval
        logger.info(
            f"Statistics data retrieved successfully for instrument_code: {instrument_code}")

        # Return the final result in JSON format
        return result

    except ValueError as e:
        # Log the value error details
        logger.error(
            f"ValueError for instrument_code: {instrument_code}, Error: {str(e)}")

        # Handle value errors and return a 400 error
        raise HTTPException(status_code=400, detail=str(e))

    except ConnectionError as e:
        # Log the connection error details
        logger.error(
            f"ConnectionError for instrument_code: {instrument_code}, Error: {str(e)}")

        # Handle connection errors and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        # Log any other unexpected errors
        logger.error(
            f"Unexpected error for instrument_code: {instrument_code}, Error: {str(e)}")

        # Handle any other exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))

logger = logging.getLogger("intradayOB_history_logger")


@app.get("/GET/IntradayOB-history", tags=["Order Book"], responses={
    200: {
        "description": "Intraday Order Book History",
        "content": {
            "application/json": {
                "example": [{
                    "J-Date": "1400-08-01",
                    "Time": "12:30",
                    "Depth": 5,
                    "Sell_No": 100,
                    "Sell_Vol": 500,
                    "Sell_Price": 15000,
                    "Buy_Price": 14950,
                    "Buy_Vol": 400,
                    "Buy_No": 95,
                    "Day_LL": 13000,
                    "Day_UL": 15500
                }]
            }
        }
    },
    404: {"description": "No data available for the given parameters"},
    500: {"description": "Internal Server Error"}
})
async def api_get_intradayOB_history(
        stock: str = Query('کرمان', description="Stock name (in Persian)"),
        start_date: str = Query(
            '1400-08-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-08-01', description="End date in Persian format (yyyy-mm-dd)"),
        jalali_date: bool = Query(True, description="Show Jalali date"),
        combined_datetime: bool = Query(
            False, description="Combine Jalali date and time"),
        show_progress: bool = Query(
            True, description="Show progress in data retrieval")):
    """
    API endpoint to retrieve intraday order book (OB) history for a given stock.

    Parameters:
    - **stock**: The name of the stock in Persian.
    - **start_date**: The start date of the data retrieval in Jalali (Persian) calendar format.
    - **end_date**: The end date of the data retrieval in Jalali (Persian) calendar format.
    - **jalali_date**: Whether to show dates in the Jalali (Persian) format.
    - **combined_datetime**: If true, the Jalali date and time will be combined into a single field.
    - **show_progress**: Whether to show the progress of data retrieval.

    Returns:
    - A list of records containing the intraday order book history.
    """
    try:
        # Log the input parameters
        logger.info(
            f"Request received with parameters: stock={stock}, start_date={start_date}, end_date={end_date}, jalali_date={jalali_date}, combined_datetime={combined_datetime}, show_progress={show_progress}")

        # Fetch the intraday order book history using the provided function
        df = Get_IntradayOB_History(
            stock=stock,
            start_date=start_date,
            end_date=end_date,
            jalali_date=jalali_date,
            combined_datatime=combined_datetime,
            show_progress=show_progress
        )

        # Log if no data is found
        if df is None or df.empty:
            logger.warning(
                f"No data found for stock: {stock}, date range: {start_date} to {end_date}")
            raise HTTPException(
                status_code=404, detail="No data available for the given parameters.")

        # Reset the index of the dataframe to include it in the JSON response
        df.reset_index(inplace=True)

        # Log successful retrieval
        logger.info(
            f"Successfully retrieved {len(df)} records for stock: {stock}, date range: {start_date} to {end_date}")

        # Return the dataframe as a list of dictionaries
        return df.to_dict(orient='records')

    except ValueError as ve:
        # Log the error and raise HTTP 400 Bad Request
        logger.error(
            f"ValueError: {str(ve)} occurred for stock: {stock}, start_date: {start_date}, end_date: {end_date}")
        raise HTTPException(
            status_code=400, detail=f"Invalid input: {str(ve)}")

    except Exception as e:
        # Log the error and raise HTTP 500 Internal Server Error
        logger.error(
            f"Unexpected error: {str(e)} occurred for stock: {stock}, start_date: {start_date}, end_date: {end_date}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/GET/SectorIndex-history", tags=["Sector Index"], responses={
    200: {
        "description": "History of Sector Index",
        "content": {
            "application/json": {
                "example": [{
                    "J-Date": "1400-12-29",
                    "Date": "2024-03-20",
                    "Weekday": "Wednesday",
                    "Open": 12345.67,
                    "High": 13000.00,
                    "Low": 12000.00,
                    "Close": 12500.00,
                    "Adj Close": 12450.75,
                    "Volume": 1000000
                }]
            }
        }
    },
    400: {"description": "Bad Request - Invalid input or parameters"},
    500: {"description": "Internal Server Error - Unable to process the request"}
})
async def api_get_sector_index_history(
        sector: str = Query(
            'خودرو', description="Name of the sector in Persian"),
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(
            False, description="Show only the adjusted close price"),
        show_weekday: bool = Query(
            False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Show both Gregorian and Jalali dates")):
    """
    Retrieve the historical Sector Index data for the specified sector.

    Parameters:
    - **sector**: The name of the sector in Persian.
    - **start_date**: Start date in Jalali (Persian) format (yyyy-mm-dd).
    - **end_date**: End date in Jalali (Persian) format (yyyy-mm-dd).
    - **ignore_date**: Ignore the date range and fetch all available data.
    - **just_adj_close**: Show only the adjusted close price.
    - **show_weekday**: Display the weekday for each record.
    - **double_date**: Include both Jalali and Gregorian dates in the result.

    Returns:
    - A list of records containing the historical sector index data, including fields such as open, close, high, low, and volume.
    """
    try:
        # Check if date formats are valid
        if not is_valid_jalali_date(start_date) or not is_valid_jalali_date(end_date):
            raise ValueError(
                "Invalid date format. Dates must be in Persian format (yyyy-mm-dd).")

        # Call the function to get Sector Index history
        df = Get_SectorIndex_History(
            sector=sector,
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # Check if DataFrame is empty
        if df.empty:
            raise ValueError(
                "No data found for the provided date range or parameters.")

        # Ensure the index (J-Date) is included and reset the index for correct formatting
        df.reset_index(inplace=True)

        # Return the DataFrame as a list of dictionaries (JSON format)
        return df.to_dict(orient='records')

    except ValueError as ve:
        # Handle issues such as invalid date format or missing data
        logger.error(f"ValueError: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except ConnectionError as ce:
        # Handle network or connection issues
        logger.error(f"ConnectionError: {str(ce)}")
        raise HTTPException(
            status_code=500, detail="Connection error. Please try again later.")

    except Exception as e:
        # Log and handle unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An internal server error occurred. Please try again later.")


@app.get("/GET/PricePanel", tags=["Price Panel"], responses={
    200: {
        "description": "Price Panel for Given Stocks",
        "content": {"application/json": {"example": [{
        "J-Date": "1380-01-05",
        "خودرو": 54
    },]}}
    },
    500: {"description": "Internal Server Error"}})
async def api_build_price_panel(
        stock_list: List[str] = Query(['خودرو'],
                                      description="List of stock symbols"),
        param: str = Query(
            'Adj Final', description="The type of price data to retrieve ('Final' or 'Adj Final')"),
        jalali_date: bool = Query(
            True, description="Show Jalali date instead of Gregorian"),):
    """
    API endpoint to build a price panel for a given list of stocks.
    """
    try:
        # Call the original Build_PricePanel function with the provided parameters
        df_panel = Build_PricePanel(
            stock_list=stock_list,
            param=param,
            jalali_date=jalali_date,
        )
        
        # If the result is a pandas DataFrame, convert it to a dictionary for JSON response
        if df_panel is not None:
            return df_panel.reset_index().to_dict(orient='records')
        else:
            return {"message": "No data returned"}

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/shareholders-info",
         tags=["Shareholders"],
         summary="Retrieve Shareholder Information",
         description="Fetch the latest shareholder details for a given ticker symbol.",
         responses={
             200: {
                 "description": "Shareholder Information for the given ticker",
                 "content": {
                     "application/json": {
                         "example": [
                             {
                                 "Ticker": "خودرو",
                                 "Market": "TSE",
                                 "Name": "Company Name",
                                 "ShareNo": 1000000,
                                 "SharePct": 5.00,
                                 "Changes": 10000
                             }
                         ]
                     }
                 }
             },
             400: {"description": "Invalid ticker format"},
             500: {"description": "Internal Server Error"}
         })
async def api_get_shareholders_info(
        ticker: str = Query('خودرو', description="Ticker symbol in Persian (example: 'خودرو')")):
    """
    API endpoint to retrieve the latest shareholder information for the given ticker.

    - **ticker**: The ticker symbol in Persian (e.g., 'خودرو')
    """
    try:
        # Log the start of the request processing
        logger.info(f"Fetching shareholder information for ticker: {ticker}")

        # Call the original function with the ticker parameter
        df = Get_ShareHoldersInfo(ticker=ticker)

        # Log the success of the data retrieval
        logger.info(f"Data retrieved successfully for ticker: {ticker}")

        # If the result is a pandas DataFrame, convert it to a dictionary
        df.reset_index(inplace=True)

        # Log the result before returning
        logger.debug(
            f"Returning data for ticker: {ticker} - {df.to_dict(orient='records')}")

        return df.to_dict(orient='records')

    except Exception as e:
        # Log the exception details
        logger.error(
            f"Error fetching shareholder info for ticker: {ticker}, Error: {str(e)}")

        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/notifications-data", tags=["Notifications"], responses={
    200: {
        "description": "Notification data successfully fetched and processed",
        "content": {
            "application/json": {
                "example": [{
                    "id": 1,
                    "symbol": "XYZ",
                    "name": "Example Corp",
                    "title": "Mid-year financial report",
                    "DateTime": "2024-01-01T12:00:00",
                    "fileName": "report2024.pdf",
                    "fileExtension": "pdf",
                    "tracingNo": "123456",
                    "download_url": "https://example.com/file/123456/1"
                }]
            }
        }
    },
    500: {
        "description": "Internal Server Error"
    }
})
async def api_get_notifications_data(
        instrument_code: str = Query(
            '33293588228706998', description="The code of the financial instrument to fetch notifications for")):
    """
    Fetch and return the notification data based on the provided instrument code.

    Args:
        instrument_code (str): The code of the financial instrument to fetch notifications for.

    Returns:
        JSON: A list of notification data with details such as the symbol, title, and download URL.
    """
    try:
        # Call the provided get_notifications_data function
        return get_notifications_data(instrument_code)

    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/change-status-data",
         tags=["Market Data"],
         summary="Fetch Processed Notification Data",
         description="Retrieve and process notification data based on the given instrument code.",
         responses={
             200: {
                 "description": "Returns processed notification data based on the instrument code.",
                 "content": {
                     "application/json": {
                         "example": {
                             "idn": 0,
                             "insCode": "33293588228706998",
                             "cEtaval": "A ",
                             "cEtavalTitle": "مجاز",
                             "datetime": "2024-10-12T11:45:04"
                         }
                     }
                 }
             },
             400: {"description": "Invalid instrument code format."},
             500: {"description": "Internal Server Error. Check the details for more information."}
         })
async def api_get_change_status_data(
        instrument_code: str = Query(
            '33293588228706998', description="The code of the financial instrument to fetch notifications for.")):
    """
    API endpoint for fetching and processing notification data based on an instrument code.

    - **instrument_code**: The code of the financial instrument to retrieve notifications for.
    """
    try:
        # Log the start of the request
        logger.info(
            f"Fetching change status data for instrument_code: {instrument_code}")

        # Call the function to get the change status data
        result = get_change_status_data(instrument_code)

        # Log the successful data retrieval
        logger.info(
            f"Successfully fetched data for instrument_code: {instrument_code}")

        # Return the processed data as JSON
        return result

    except ConnectionError as e:
        # Log connection errors
        logger.error(
            f"Connection error for instrument_code: {instrument_code}, Error: {str(e)}")

        # Raise 500 if there is a connection issue with the API
        raise HTTPException(
            status_code=500, detail="Connection Error: " + str(e))

    except ValueError as e:
        # Log data processing errors
        logger.error(
            f"Data processing error for instrument_code: {instrument_code}, Error: {str(e)}")

        # Raise 500 if there is a value error in processing the data
        raise HTTPException(
            status_code=500, detail="Data Processing Error: " + str(e))

    except Exception as e:
        # Log unexpected errors
        logger.error(
            f"Unexpected error for instrument_code: {instrument_code}, Error: {str(e)}")

        # Catch any other errors and return a generic error response
        raise HTTPException(
            status_code=500, detail="Unexpected Error: " + str(e))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/real-legal-data",
         tags=["Market Data"],
         summary="Fetch and process real/legal data",
         description="Retrieve processed notification data based on a specific instrument code.",
         responses={
             200: {
                 "description": "Returns processed notification data based on instrument code.",
                 "content": {
                     "application/json": {
                         "example": [
                             {
                                 "recDate": 20241019,
                                 "insCode": "33293588228706998",
                                 "buy_I_Volume": 101406123.0,
                                 "buy_N_Volume": 11452230.0,
                                 "buy_I_Value": 239094206413.0,
                                 "buy_N_Value": 26890337519.0,
                                 "buy_N_Count": 7,
                                 "sell_I_Volume": 104582308.0,
                                 "buy_I_Count": 423.0,
                                 "sell_N_Volume": 8276045.0,
                                 "sell_I_Value": 246700303414.0,
                                 "sell_N_Value": 19284240518.0,
                                 "sell_N_Count": 4,
                                 "sell_I_Count": 333
                             }
                         ]
                     }
                 }
             },
             500: {
                 "description": "Internal Server Error. Check the details for more information."
             }
         })
async def api_get_realـlegal(
        instrument_code: str = Query(
            '33293588228706998', description="The code of the financial instrument to fetch notifications for.")):
    """
    API endpoint for fetching and processing notification data based on an instrument code.

    - **instrument_code**: The unique code of the financial instrument.
    """
    try:
        # Log the start of data fetching
        logger.info(
            f"Fetching real/legal data for instrument_code: {instrument_code}")

        # Call the function to get the data
        data = get_realـlegal_data(instrument_code)

        # Log the success of data retrieval
        logger.info(
            f"Data successfully retrieved for instrument_code: {instrument_code}")

        # Return the processed data as JSON
        return data

    except ConnectionError as e:
        # Log the connection error
        logger.error(
            f"Connection error for instrument_code: {instrument_code}, Error: {str(e)}")

        # Raise 500 if there is a connection issue
        raise HTTPException(
            status_code=500, detail="Connection Error: " + str(e))

    except ValueError as e:
        # Log the value error
        logger.error(
            f"Data processing error for instrument_code: {instrument_code}, Error: {str(e)}")

        # Raise 500 if there is a value error in processing the data
        raise HTTPException(
            status_code=500, detail="Data Processing Error: " + str(e))

    except Exception as e:
        # Log any unexpected errors
        logger.error(
            f"Unexpected error for instrument_code: {instrument_code}, Error: {str(e)}")

        # Catch any other errors and return a generic error response
        raise HTTPException(
            status_code=500, detail="Unexpected Error: " + str(e))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/shareholders-data",
         tags=["Shareholders Data"],
         summary="Retrieve Processed Shareholders Data",
         description="Fetch and process shareholders data for the given instrument code.",
         responses={
             200: {
                 "description": "Returns processed shareholders data based on the instrument code",
                 "content": {
                     "application/json": {
                         "example": {
                             "shareHolderName": "شركت گروه سرمايه گذاري تدبير-سهامي عام -",
                             "cIsin": "IRO1BPAR0009",
                             "numberOfShares": 11669785237.0,
                             "perOfShares": 7.464,
                             "change": 1,
                             "changeAmount": 0.0,
                             "shareHolderShareID": 21457889
                         }
                     }
                 }
             },
             404: {"description": "Instrument not found or invalid data"},
             500: {"description": "Internal Server Error"}
         })
async def api_get_shareholders_data(
        instrument_code: str = Query('33293588228706998',
                                     description="The code of the financial instrument")):
    """
    API endpoint to fetch and process shareholders data for a given instrument code.

    - **instrument_code**: The unique code of the financial instrument.
    """
    try:
        # Log the instrument code being processed
        logger.info(
            f"Fetching shareholders data for instrument code: {instrument_code}")

        # Call the function to get shareholders data
        result = get_shareholders_data(instrument_code)

        # Log successful data processing
        logger.info(
            f"Successfully processed data for instrument code: {instrument_code}")

        # Return the processed data in JSON format
        return result

    # Handle connection errors and data processing errors
    except ConnectionError as e:
        # Log connection error
        logger.error(
            f"Connection error for instrument code {instrument_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    except ValueError as e:
        # Log data processing error
        logger.warning(f"Invalid data or instrument not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        # Log unexpected errors
        logger.error(
            f"Unexpected error for instrument code {instrument_code}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/GET/introduction-data",
         tags=["Introduction Data"],
         summary="Fetch Introduction Data for a Given Instrument",
         description="Retrieves detailed information about a financial instrument based on its code.",
         responses={
             200: {
                 "description": "Successfully fetched introduction data",
                 "content": {
                     "application/json": {
                         "example": {
                             "codalPublisher": {
                                 "id": 6756,
                                 "symbol": "شپنا",
                                 "displaySymbol": "شپنا",
                                 "name": "پالایش نفت اصفهان",
                                 "isic": "232007",
                                 "reportingType": "1000000",
                                 "executiveManager": "محسن قديري",
                                 "address": "اصفهان- کیلومتر 5 جاده تهران صندوق پستی 415-81465",
                                 "telNo": "031-33802727",
                                 "faxNo": "031-36686962",
                                 "activitySubject": "انجام عملیات پالایش و فرآورش نفت خام و سایر هیدرو کربورها...",
                                 "officeAddress": "اصفهان- کیلومتر 5 جاده تهران صندوق پستی 415-81465",
                                 "shareOfficeAddress": "امور مالی شرکت پالایش نفت اصفهان",
                                 "website": "www.eorc.ir",
                                 "email": "info@eorc.ir",
                                 "financialYear": "12/30",
                                 "financialManager": "صاحب ارجمند",
                                 "nationalCode": "10101874620"
                             }
                         }
                     }
                 }
             },
             400: {"description": "Invalid Request"},
             500: {"description": "Internal Server Error"}
         })
async def api_get_introduction_data(
        instrument_code: str = Query(
            '%D8%B4%D9%BE%D9%86%D8%A7', description="The code of the financial instrument (example: '%D8%B4%D9%BE%D9%86%D8%A7')")):
    """
    Fetches and processes notification data for a given instrument code.

    - **instrument_code**: The code of the financial instrument in URL-encoded format.
    """
    try:
        # Log the start of the request
        logger.info(
            f"Fetching introduction data for instrument code: {instrument_code}")

        # Call the get_introduction_data function with the provided instrument code
        data = get_introduction_data(instrument_code)

        # Log successful data retrieval
        logger.info(
            f"Successfully fetched data for instrument code: {instrument_code}")

        # Return the fetched and processed data as a JSON response
        return data

    except ConnectionError:
        # Log connection error
        logger.error(
            f"Connection error while fetching data for instrument code: {instrument_code}")
        # Return a 500 status code for connection errors
        raise HTTPException(
            status_code=500, detail="Failed to connect to the API. Please check your connection.")

    except ValueError as e:
        # Log validation error
        logger.warning(
            f"Invalid data or request for instrument code: {instrument_code}, Error: {str(e)}")
        # Return a 400 status code for any input or data processing issues
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Log any other unexpected errors
        logger.error(
            f"Unexpected error occurred for instrument code: {instrument_code}, Error: {str(e)}")
        # Return a 500 status code for any unexpected errors
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}")
