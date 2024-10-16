from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional, Dict
from pydantic import BaseModel
from src.FinpyClassic import (
    get_tse_webid, get_price_history,
    get_ri_history, Get_RI_History,
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


def functionsnamed(x):
    pass


class PriceHistoryRequest(BaseModel):
    stock_list: List[str]
    adjust_price: Optional[bool] = True
    show_progress: Optional[bool] = True
    save_excel: Optional[bool] = False
    save_path: Optional[str] = 'D:/FinPy-TSE Data/MarketWatch'


# !error


@app.get("/GET/ri-history-alt", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved RI history",
        "content": {"application/json": {"example": [{"date": "1400-01-01", "ri_value": 1000}]}}
    },
    500: {"description": "Server error"}})
async def api_get_ri_history_alt(
        stock: str = Query('خودرو', description="Stock symbol (in Persian)"),
        start_date: str = Query(
            '1400-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1401-01-01', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(
            False, description="Whether to ignore the date range or not"),
        show_weekday: bool = Query(
            False, description="Show weekday for each date"),
        double_date: bool = Query(
            False, description="Include double date (Gregorian and Jalali)"),
        alt: bool = Query(False, description="Alternate method for fetching data")):
    """
    Retrieve the Relative Index (RI) history for a given stock.

    - **stock**: Stock symbol (e.g., خودرو).
    - **start_date**: Start date in Jalali calendar.
    - **end_date**: End date in Jalali calendar.
    - **ignore_date**: Whether to ignore the date range.
    - **show_weekday**: Whether to show the weekday in the response.
    - **double_date**: Whether to include both Gregorian and Jalali dates.
    - **alt**: Use alternate method to fetch data.
    """
    try:
        df = Get_RI_History(stock, start_date, end_date,
                            ignore_date, double_date, alt)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# !error


@app.get("/GET/marketwatch", tags=["Market"], responses={
    200: {
        "description": "Market watch data retrieved successfully",
        "content": {"application/json": {"example": [{"stock": "خودرو", "price": 1000}]}}
    },
    500: {"description": "Server error"}})
async def api_get_marketwatch(
        save_excel: bool = Query(
            False, description="Save the output as Excel file"),
        save_path: str = Query('D:/FinPy-TSE Data/MarketWatch', description="Path to save the Excel file")):
    """
    Fetch the market watch data and optionally save it as an Excel file.

    - **save_excel**: Whether to save the data as an Excel file.
    - **save_path**: Path to save the file if `save_excel` is true.
    """
    try:
        df, ob = Get_MarketWatch(save_excel, save_path)

        # Replacing NaN and Inf values
        # df = df.replace(['NaN'], None)
        df = df.fillna(value=None, method="ffill")

        df.reset_index(inplace=True)
        # ob = ob.replace([float('inf'), -float('inf')], None)
        ob = ob.fillna(value=None, method="ffill")
        ob.reset_index(inplace=True)

        final_df = {}
        final_df['final'] = df.to_dict(orient='records')
        final_df['orderbook'] = ob.to_dict(orient='records')
        return final_df
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ! error


@app.post("/GET/60d-price-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved 60 days price history",
        "content": {"application/json": {"example": [{"date": "1400-01-01", "price": 1000}]}}
    },
    500: {"description": "Server error"}})
async def api_get_60d_price_history(request_data: PriceHistoryRequest):
    """
    Fetch 60 days of price history for a list of stocks.

    - **stock_list**: List of stock symbols.
    - **adjust_price**: Whether to adjust the price.
    - **show_progress**: Show progress during fetching.
    - **save_excel**: Save the output as an Excel file.
    - **save_path**: Path to save the file if `save_excel` is true.
    """
    try:
        df = Get_60D_PriceHistory(
            request_data.stock_list,
            request_data.adjust_price,
            request_data.show_progress,
            request_data.save_excel,
            request_data.save_path
        )
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/tse-webid", tags=["Market"], responses={
    200: {
        "description": "Successfully retrieved TSE WebID",
        "content": {"application/json": {"example": [{"webid": "123456"}]}}
    },
    500: {"description": "Server error"}})
async def api_get_tse_webid(stock: str = Query('پترول', description="Stock symbol (in Persian)")):
    """
    Get TSE WebID for a specific stock.

    - **stock**: Stock symbol in Persian (e.g., پترول).
    """
    try:
        df = get_tse_webid(stock)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/build-market-stocklist", tags=["Market"], responses={
    200: {
        "description": "Successfully built the market stock list",
        "content": {"application/json": {"example": [{"stock": "خودرو", "price": 1000}]}}
    },
    500: {"description": "Server error"}})
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
        df = Build_Market_StockList(
            bourse, farabourse, payeh, detailed_list, show_progress)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/price-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved price history",
        "content": {"application/json": {"example": [{"date": "1400-01-01", "price": 1000}]}}
    },
    500: {"description": "Server error"}})
async def api_get_price_history(
        stock: str = Query('خودرو', description="Stock symbol (in Persian)"),
        start_date: str = Query(
            '1400-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1401-01-01', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        adjust_price: bool = Query(False, description="Adjust the price"),
        show_weekday: bool = Query(
            False, description="Show the weekday for each date"),
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
    try:
        df = get_price_history(stock, start_date, end_date,
                               ignore_date, adjust_price, show_weekday, double_date)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/ri-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved RI history",
        "content": {"application/json": {"example": [{"date": "1400-01-01", "ri_value": 1000}]}}
    },
    500: {"description": "Server error"}})
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
    Retrieve the Relative Index (RI) history for a stock.

    - **stock**: Stock symbol (e.g., خودرو).
    - **start_date**: Start date in Jalali calendar.
    - **end_date**: End date in Jalali calendar.
    - **ignore_date**: Whether to ignore the date range.
    - **show_weekday**: Show the weekday for each date.
    - **double_date**: Include both Jalali and Gregorian dates.
    """
    try:
        df = get_ri_history(stock, start_date, end_date,
                            ignore_date, show_weekday, double_date)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/cwi-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved CWI history",
        "content": {"application/json": {"example": [{"date": "1400-01-01", "cwi_value": 1000}]}}
    },
    500: {"description": "Server error"}})
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

    - **start_date**: Start date in Jalali calendar.
    - **end_date**: End date in Jalali calendar.
    - **ignore_date**: Whether to ignore the date range.
    - **just_adj_close**: Only use adjusted close prices.
    - **show_weekday**: Show the weekday for each date.
    - **double_date**: Include both Jalali and Gregorian dates.
    """
    try:
        df = Get_CWI_History(start_date, end_date, ignore_date,
                             just_adj_close, show_weekday, double_date)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/ewi-history", tags=["History"], responses={
    200: {
        "description": "Successfully retrieved EWI history",
        "content": {"application/json": {"example": [{"date": "1400-01-01", "ewi_value": 1000}]}}
    },
    500: {"description": "Server error"}})
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

    - **start_date**: Start date in Jalali calendar.
    - **end_date**: End date in Jalali calendar.
    - **ignore_date**: Whether to ignore the date range.
    - **just_adj_close**: Only use adjusted close prices.
    - **show_weekday**: Show the weekday for each date.
    - **double_date**: Include both Jalali and Gregorian dates.
    """
    try:
        df = Get_EWI_History(start_date, end_date, ignore_date,
                             just_adj_close, show_weekday, double_date)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/intraday-trades-history", tags=["Trades"], responses={
    200: {
        "description": "Successfully retrieved intraday trades history",
        "content": {"application/json": {"example": [{"date": "1400-01-01", "trade_value": 1000}]}}
    },
    500: {"description": "Server error"}})
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
    Retrieve the intraday trade history for a stock.

    - **stock**: Stock symbol (e.g., وخارزم).
    - **start_date**: Start date in Jalali calendar.
    - **end_date**: End date in Jalali calendar.
    - **jalali_date**: Use Jalali date format.
    - **combined_datatime**: Combine date and time in the result.
    - **show_progress**: Show progress during fetching.
    """
    try:
        df = Get_IntradayTrades_History(
            stock, start_date, end_date, jalali_date, combined_datatime, show_progress)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/GET/supervisor-message-data", tags=["majed"], responses={
    200: {
        "description": "Successfully retrieved ",
        "content": {"application/json": {"example": [{
            "tseMsgIdn": 196411,
            "tseTitle": "text",
            "tseDesc": "text",
            "datetime": "2024-10-12T08:00:56"
        }]}}
    },
    500: {"description": "Server error"}})
async def api_get_supervisor_message_data(
        instrument_code: str = Query(
            '33293588228706998', description="cod of company")):
    try:
        return get_supervisor_message_data(instrument_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/FFI-history", tags=[""], responses={
    200: {
        "description": "",
        "content": {"application/json": {"example": [{
            "tseMsgIdn": 196411,
            "tseTitle": "text",
            "tseDesc": "text",
            "datetime": "2024-10-12T08:00:56"
        }]}}
    },
    500: {"description": ""}})
async def api_get_ffi_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(
            False, description="Show the weekday for each date"),
):
    try:
        df = Get_FFI_History(start_date, end_date, ignore_date, just_adj_close)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/CWPI-history", tags=[""], responses={
    200: {
        "description": "",
        "content": {"application/json": {"example": [{
            "tseMsgIdn": 196411,
            "tseTitle": "text",
            "tseDesc": "text",
            "datetime": "2024-10-12T08:00:56"
        }]}}
    },
    500: {"description": ""}})
async def api_get_CWPI_history(
        start_date: str = Query(
            '1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query(
            '1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(
            False, description="Show the weekday for each date"),
        show_weekday: bool = Query(False, description=''),
        double_date: bool = Query(False, description=''),
):
    try:
        df = Get_CWPI_History(start_date, end_date, ignore_date, just_adj_close, show_weekday, double_date)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/EWPI-history", tags=[""], responses={
    200: {
        "description": "",
        "content": {"application/json": {"example": [{
            "tseMsgIdn": 196411,
            "tseTitle": "text",
            "tseDesc": "text",
            "datetime": "2024-10-12T08:00:56"
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
        double_date: bool = Query(False, description=''),
):
    try:
        df = Get_EWPI_History(start_date, end_date, ignore_date, just_adj_close, show_weekday, double_date)
        df.reset_index(inplace=True)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions like __Check_JDate_Validity__ can be defined here or imported if already available.

@app.get("/GET/MKT1I-history", tags=["Market Index"], responses={
    200: {
        "description": "History of MKT1I (First Market Index)",
        "content": {"application/json": {"example": [{
            "J-Date": "1400-12-29",
            "Date": "2024-03-20",
            "Weekday": "Wednesday",
            "Open": 12345.67,
            "High": 13000.00,
            "Low": 12000.00,
            "Close": 12500.00,
            "Adj Close": 12450.75,
            "Volume": 1000000
        }]}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_MKT1I_history(
        start_date: str = Query('1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query('1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(False, description="Show only the adjusted close price"),
        show_weekday: bool = Query(False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Show both Gregorian and Jalali dates")
):
    """
    API endpoint to retrieve MKT1I history (First Market Index).
    """
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

        # If the result is a pandas DataFrame, convert it to a dictionary
        df.reset_index(inplace=True)  # Make sure the index (J-Date) is part of the JSON
        return df.to_dict(orient='records')

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/MKT2I-history", tags=["Market Index"], responses={
    200: {
        "description": "History of MKT2I (Second Market Index)",
        "content": {"application/json": {"example": [{
            "J-Date": "1400-12-29",
            "Date": "2024-03-20",
            "Weekday": "Wednesday",
            "Open": 12345.67,
            "High": 13000.00,
            "Low": 12000.00,
            "Close": 12500.00,
            "Adj Close": 12450.75,
            "Volume": 1000000
        }]}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_MKT2I_history(
        start_date: str = Query('1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query('1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(False, description="Show only the adjusted close price"),
        show_weekday: bool = Query(False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Show both Gregorian and Jalali dates")
):
    """
    API endpoint to retrieve MKT2I history (Second Market Index).
    """
    try:
        # Call the original function with the query parameters
        df = Get_MKT2I_History(
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # If the result is a pandas DataFrame, convert it to a dictionary
        df.reset_index(inplace=True)  # Make sure the index (J-Date) is part of the JSON
        return df.to_dict(orient='records')

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/INDI-history", tags=["Industry Index"], responses={
    200: {
        "description": "History of INDI (Industry Index)",
        "content": {"application/json": {"example": [{
            "J-Date": "1400-12-29",
            "Date": "2024-03-20",
            "Weekday": "Wednesday",
            "Open": 15000.45,
            "High": 15500.00,
            "Low": 14500.00,
            "Close": 15200.00,
            "Adj Close": 15150.00,
            "Volume": 1200000
        }]}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_INDI_history(
        start_date: str = Query('1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query('1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(False, description="Show only the adjusted close price"),
        show_weekday: bool = Query(False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Show both Gregorian and Jalali dates")
):
    """
    API endpoint to retrieve INDI history (Industry Index).
    """
    try:
        # Call the original function with the query parameters
        df = Get_INDI_History(
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # If the result is a pandas DataFrame, convert it to a dictionary
        df.reset_index(inplace=True)  # Ensure the index (J-Date) is part of the JSON
        return df.to_dict(orient='records')

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/LCI30-history", tags=["Market Index"], responses={
    200: {
        "description": "History of LCI30 (30 Large-Cap Index)",
        "content": {"application/json": {"example": [{
            "J-Date": "1400-12-29",
            "Date": "2024-03-20",
            "Weekday": "Wednesday",
            "Open": 12345.67,
            "High": 13000.00,
            "Low": 12000.00,
            "Close": 12500.00,
            "Adj Close": 12450.75,
            "Volume": 1000000
        }]}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_LCI30_history(
        start_date: str = Query('1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query('1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(False, description="Show only the adjusted close price"),
        show_weekday: bool = Query(False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Show both Gregorian and Jalali dates")
):
    """
    API endpoint to retrieve LCI30 history (30 Large-Cap Index).
    """
    try:
        # Call the original function with the query parameters
        df = Get_LCI30_History(
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # If the result is a pandas DataFrame, convert it to a dictionary
        df.reset_index(inplace=True)  # Ensure 'J-Date' is included in the output
        return df.to_dict(orient='records')

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/ACT50-history", tags=["Market Index"], responses={
    200: {
        "description": "History of ACT50 (50 Most Active Stocks Index)",
        "content": {"application/json": {"example": [{
            "J-Date": "1400-12-29",
            "Date": "2024-03-20",
            "Weekday": "Wednesday",
            "Open": 12345.67,
            "High": 13000.00,
            "Low": 12000.00,
            "Close": 12500.00,
            "Adj Close": 12450.75,
            "Volume": 1000000
        }]}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_ACT50_history(
        start_date: str = Query('1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query('1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(False, description="Show only the adjusted close price"),
        show_weekday: bool = Query(False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Show both Gregorian and Jalali dates")
):
    """
    API endpoint to retrieve ACT50 history (50 Most Active Stocks Index).
    """
    try:
        # Call the original function with the query parameters
        df = Get_ACT50_History(
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # If the result is a pandas DataFrame, convert it to a dictionary
        df.reset_index(inplace=True)  # Make sure the index (J-Date) is part of the JSON
        return df.to_dict(orient='records')

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/statistics-data", tags=["Market Data"], responses={
    200: {
        "description": "Statistics data for the provided instrument code",
        "content": {"application/json": {"example": {
            "instrument_code": "123456",
            "column1": "value1",
            "column2": "value2",
            # Add more fields as per the expected output format
        }}}
    },
    400: {"description": "Bad Request: Invalid input or processing error"},
    500: {"description": "Internal Server Error: API connection failed"}
})
async def api_get_statistics_data(
        instrument_code: str = Query(
            '33293588228706998', description="The code of the financial instrument to fetch data for")
):
    """
    API endpoint to fetch and process notification data for a given instrument code.
    """
    try:
        # Call the original function
        result = get_statistics_data(instrument_code)

        # Return the final result in JSON format
        return result

    except ValueError as e:
        # Handle value errors and return a 400 error
        raise HTTPException(status_code=400, detail=str(e))

    except ConnectionError as e:
        # Handle connection errors and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        # Handle any other exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/IntradayOB-history", tags=["Order Book"], responses={
    200: {
        "description": "Intraday Order Book History",
        "content": {"application/json": {"example": [{
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
        }]}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_intradayOB_history(
        stock: str = Query('کرمان', description="Stock name (in Persian)"),
        start_date: str = Query('1400-08-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query('1400-08-01', description="End date in Persian format (yyyy-mm-dd)"),
        jalali_date: bool = Query(True, description="Show Jalali date"),
        combined_datetime: bool = Query(False, description="Combine Jalali date and time"),
        show_progress: bool = Query(True, description="Show progress in data retrieval")
):
    """
    API endpoint to retrieve intraday order book (OB) history for a given stock.
    """
    try:
        # Call the Get_IntradayOB_History function with the query parameters
        df = Get_IntradayOB_History(
            stock=stock,
            start_date=start_date,
            end_date=end_date,
            jalali_date=jalali_date,
            combined_datatime=combined_datetime,
            show_progress=show_progress
        )

        if df is None:
            raise HTTPException(status_code=404, detail="No data available for the given parameters.")

        # If the result is a pandas DataFrame, convert it to a dictionary
        df.reset_index(inplace=True)  # Make sure the index is part of the JSON response
        return df.to_dict(orient='records')

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/SectorIndex-history", tags=["Sector Index"], responses={
    200: {
        "description": "History of Sector Index",
        "content": {"application/json": {"example": [{
            "J-Date": "1400-12-29",
            "Date": "2024-03-20",
            "Weekday": "Wednesday",
            "Open": 12345.67,
            "High": 13000.00,
            "Low": 12000.00,
            "Close": 12500.00,
            "Adj Close": 12450.75,
            "Volume": 1000000
        }]}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_sector_index_history(
        sector: str = Query('خودرو', description="Name of the sector in Persian"),
        start_date: str = Query('1395-01-01', description="Start date in Persian format (yyyy-mm-dd)"),
        end_date: str = Query('1400-12-29', description="End date in Persian format (yyyy-mm-dd)"),
        ignore_date: bool = Query(False, description="Ignore the date range"),
        just_adj_close: bool = Query(False, description="Show only the adjusted close price"),
        show_weekday: bool = Query(False, description="Show the weekday for each date"),
        double_date: bool = Query(False, description="Show both Gregorian and Jalali dates")
):
    """
    API endpoint to retrieve Sector Index history.
    """
    try:
        # Call the original function with the query parameters
        df = Get_SectorIndex_History(
            sector=sector,
            start_date=start_date,
            end_date=end_date,
            ignore_date=ignore_date,
            just_adj_close=just_adj_close,
            show_weekday=show_weekday,
            double_date=double_date
        )

        # If the result is a pandas DataFrame, convert it to a dictionary
        df.reset_index(inplace=True)  # Make sure the index (J-Date) is part of the JSON
        return df.to_dict(orient='records')

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/PricePanel", tags=["Price Panel"], responses={
    200: {
        "description": "Price Panel for Given Stocks",
        "content": {"application/json": {"example": [{
            "Stock": "StockName",
            "J-Date": "1400-12-29",
            "Adj Final": 12345.67,
            # Other fields as per the actual response
        }]}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_build_price_panel(
        stock_list: List[str] = Query(..., description="List of stock symbols"),
        param: str = Query('Adj Final', description="The type of price data to retrieve ('Final' or 'Adj Final')"),
        jalali_date: bool = Query(True, description="Show Jalali date instead of Gregorian"),
        save_excel: bool = Query(True, description="Save the result as an Excel file"),
        save_path: str = Query('D:/FinPy-TSE Data/Price Panel/', description="Path to save the Excel file")
):
    """
    API endpoint to build a price panel for a given list of stocks.
    """
    try:
        # Call the original Build_PricePanel function with the provided parameters
        df_panel = Build_PricePanel(
            stock_list=stock_list,
            param=param,
            jalali_date=jalali_date,
            save_excel=save_excel,
            save_path=save_path
        )

        # If the result is a pandas DataFrame, convert it to a dictionary for JSON response
        if df_panel is not None:
            return df_panel.reset_index().to_dict(orient='records')
        else:
            return {"message": "No data returned"}

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/shareholders-info", tags=["Shareholders"], responses={
    200: {
        "description": "Shareholder Information for the given ticker",
        "content": {"application/json": {"example": [{
            "Ticker": "خودرو",
            "Market": "TSE",
            "Name": "Company Name",
            "ShareNo": 1000000,
            "SharePct": 5.00,
            "Changes": 10000
        }]}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_shareholders_info(
        ticker: str = Query('خودرو', description="Ticker symbol in Persian (example: 'خودرو')")
):
    """
    API endpoint to retrieve the latest shareholder information for the given ticker.
    """
    try:
        # Call the original function with the ticker parameter
        df = Get_ShareHoldersInfo(ticker=ticker)

        # If the result is a pandas DataFrame, convert it to a dictionary
        df.reset_index(inplace=True)  # Make sure the index (Ticker, Market, Name) is part of the JSON
        return df.to_dict(orient='records')

    except Exception as e:
        # Return a 500 status code and error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))


# Example: API endpoint for get_notifications_data
@app.get("/GET/notifications-data", tags=["Notifications"], responses={
    200: {
        "description": "Notification data successfully fetched and processed",
        "content": {"application/json": {"example": {
            "column1": "value1",
            "column2": "value2",
            # Additional columns as per your actual data structure
        }}}
    },
    500: {"description": "Internal Server Error"}
})
async def api_get_notifications_data(
        instrument_code: str = Query(
            '33293588228706998', description="The code of the financial instrument to fetch notifications for")):
    """
    Fetch and return the notification data based on the provided instrument code.
    """
    try:
        # Call the provided get_notifications_data function

        # Return the result as a dictionary (JSON format)
        return get_notifications_data(instrument_code)

    except ConnectionError as e:
        # Handle connection errors and raise a 500 error
        raise HTTPException(status_code=500, detail=str(e))

    except ValueError as e:
        # Handle value-related errors and raise a 500 error
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        # Catch-all for other unexpected errors
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/GET/change-status-data", tags=["Market Data"], responses={
    200: {
        "description": "Returns processed notification data based on instrument code.",
        "content": {"application/json": {"example": {
            "key1": "value1",
            "key2": "value2",
            # Example of expected output
        }}}
    },
    500: {"description": "Internal Server Error. Check the details for more information."}
})
async def api_get_change_status_data(
        instrument_code: str = Query(
            '33293588228706998', description="The code of the financial instrument to fetch notifications for.")
):
    """
    API endpoint for fetching and processing notification data based on an instrument code.
    """

    try:
        # Call the function to get the change status data.
        # Return the processed data as JSON.
        return get_change_status_data(instrument_code)

    except ConnectionError as e:
        # Raise 500 if there is a connection issue with the API.
        raise HTTPException(status_code=500, detail="Connection Error: " + str(e))

    except ValueError as e:
        # Raise 500 if there is a value error in processing the data.
        raise HTTPException(status_code=500, detail="Data Processing Error: " + str(e))

    except Exception as e:
        # Catch any other errors and return a generic error response.
        raise HTTPException(status_code=500, detail="Unexpected Error: " + str(e))


@app.get("/GET/real-legal-data", tags=["Market Data"], responses={
    200: {
        "description": "Returns processed notification data based on instrument code.",
        "content": {"application/json": {"example": {
            "key1": "value1",
            "key2": "value2",
            # Example of expected output
        }}}
    },
    500: {"description": "Internal Server Error. Check the details for more information."}
})
async def api_get_realـlegal(
        instrument_code: str = Query(
            '33293588228706998', description="The code of the financial instrument to fetch notifications for.")
):
    """
    API endpoint for fetching and processing notification data based on an instrument code.
    """

    try:
        # Call the function to get the change status data.
        # Return the processed data as JSON.
        return get_realـlegal_data(instrument_code)

    except ConnectionError as e:
        # Raise 500 if there is a connection issue with the API.
        raise HTTPException(status_code=500, detail="Connection Error: " + str(e))

    except ValueError as e:
        # Raise 500 if there is a value error in processing the data.
        raise HTTPException(status_code=500, detail="Data Processing Error: " + str(e))

    except Exception as e:
        # Catch any other errors and return a generic error response.
        raise HTTPException(status_code=500, detail="Unexpected Error: " + str(e))


@app.get("/GET/shareholders-data", tags=["Shareholders Data"], responses={
    200: {
        "description": "Returns processed shareholders data based on the instrument code",
        "content": {"application/json": {"example": {
            "processed_data_key": "processed_data_value"
            # Example output based on expected structure
        }}}
    },
    500: {"description": "Internal Server Error"},
    404: {"description": "Instrument not found or invalid data"}
})
async def api_get_shareholders_data(
        instrument_code: str = Query(
            '33293588228706998', description="The code of the financial instrument")
):
    """
    API endpoint to fetch and process shareholders data for a given instrument code.
    """
    try:
        # Call the function to get shareholders data
        result = get_shareholders_data(instrument_code)

        # Return the processed data in JSON format
        return result

    # Handle connection errors and data processing errors
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/GET/introduction-data", tags=["Introduction Data"], responses={
    200: {
        "description": "Successfully fetched introduction data",
        "content": {"application/json": {"example": {
            "key1": "example_value1",
            "key2": "example_value2",
            # Provide more examples based on your expected data format
        }}}
    },
    500: {"description": "Internal Server Error"},
    400: {"description": "Invalid Request"}
})
async def api_get_introduction_data(
        instrument_code: str = Query(
            '%D8%B4%D9%BE%D9%86%D8%A7', description="The code of the financial instrument")
):
    """
    Fetches and processes notification data for a given instrument code.
    """
    try:
        # Call the get_introduction_data function with the provided instrument code.
        data = get_introduction_data(instrument_code)

        # Return the fetched and processed data as a JSON response.
        return data

    except ConnectionError:
        # Return a 500 status code for connection errors.
        raise HTTPException(status_code=500, detail="Failed to connect to the API. Please check your connection.")

    except ValueError as e:
        # Return a 400 status code for any issues with input or data processing.
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Return a 500 status code for any other unexpected errors.
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# @app.get("/GET/url", tags=[""], responses={
#     200: {
#         "description": "",
#         "content": {"application/json": {"example": [{
#             "tseMsgIdn": 196411,
#             "tseTitle": "text",
#             "tseDesc": "text",
#             "datetime": "2024-10-12T08:00:56"
#         }]}}
#     },
#     500: {"description": ""}})
# async def api_functionsnamed(
#         sample: str = Query(
#             '33293588228706998', description="cod of company"),):
#     try:
#         return functionsnamed(sample)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
