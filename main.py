from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from FinpyClassic import (
    get_tse_webid,
    get_price_history,
    get_ri_history,
    Get_RI_History,
    Get_CWI_History,
    Get_EWI_History,
    Get_IntradayTrades_History,
    Get_USD_RIAL,
    Build_Market_StockList,
    Get_MarketWatch,
    Get_60D_PriceHistory,
)

app = FastAPI()


class PriceHistoryRequest(BaseModel):
    stock_list: List[str]
    adjust_price: Optional[bool] = True
    show_progress: Optional[bool] = True
    save_excel: Optional[bool] = False
    save_path: Optional[str] = 'D:/FinPy-TSE Data/MarketWatch'
#!error


@app.get("/get_ri_history_alt", tags=["History"], responses={
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
                            ignore_date, show_weekday, double_date, alt)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#!error


@app.get("/get_marketwatch", tags=["Market"], responses={
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

        # ob = ob.replace([float('inf'), -float('inf')], None)
        ob = ob.fillna(value=None, method="ffill")
        print(df, ob)

        final_df = {}
        final_df['final'] = df.to_dict(orient='records')
        final_df['orderbook'] = ob.to_dict(orient='records')
        return final_df
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#! error


@app.post("/get_60d_price_history", tags=["History"], responses={
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
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_tse_webid", tags=["Market"], responses={
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
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/build_market_stocklist", tags=["Market"], responses={
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
            bourse, farabourse, payeh, detailed_list, show_progress, save_excel, save_csv, save_path)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_price_history", tags=["History"], responses={
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


@app.get("/get_ri_history", tags=["History"], responses={
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
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_cwi_history", tags=["History"], responses={
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
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_ewi_history", tags=["History"], responses={
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
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_intraday_trades_history", tags=["Trades"], responses={
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
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_usd_rial", tags=["Currency"], responses={
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
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
