import pandas as pd
import xml.etree.ElementTree as ET
content="<Root><Type Code=\"16\" Title=\"آگهی دعوت به مجمع عمومی عادی سالیانه دوره 12 ماهه منتهی به  1402/12/29(اصلاحیه)\" /><YearEndToDate>1403/04/31</YearEndToDate><PlaceAndDateTime><Date>1403/04/31</Date><Time>08:00</Time><Place>شهرک قدس (غرب) انتهاي بلوار شهيد دادمان پژوهشگاه نيرو سالن خليج فارس</Place></PlaceAndDateTime><Agenda><AgendaItem>استماع گزارش هیئت‌ مدیره و بازرس قانونی</AgendaItem><AgendaItem>تصویب صورت‌های مالی سال (دوره) مالی منتهی به</AgendaItem><AgendaItem>انتخاب حسابرس و بازرس قانونی</AgendaItem><AgendaItem>انتخاب روزنامه کثیر‌الانتشار</AgendaItem><AgendaItem>عیین حق حضور اعضای غیر موظف هیئت مدیره</AgendaItem><AgendaItem>تعیین پاداش هیئت مدیره</AgendaItem><AgendaItem>سایر موارد</AgendaItem><AgendaItem>توضیحات :ساير مواردي که قابل طرح  و از اختيارات مجمع عمومي عادي سالانه باشد. </AgendaItem><AgendaItem>شماره سریال شهر : 228</AgendaItem><AgendaItem>نام شهر : تهران</AgendaItem><AgendaItem>شماره سریال استان : 7</AgendaItem><AgendaItem>نام استان : تهران</AgendaItem><AgendaItem>نحوه دریافت برگ ورود به جلسه : بدينوسيله از کليه سهامداران محترم بانک پارسيان دعوت مي شود به منظور اخذ برگ ورود به جلسه از تاريخ 27 تير ماه لغايت 30 تير  ماه 1403 ، در روز و ساعات اداري با در دست داشتن مدارک مالکيت سهام و ارائه کارت شناسايي معتبر، به اداره سهام بانک واقع در تهران ، شهرک قدس (غرب)، بلوار شهيد فرحزادي، خيابان زرافشان غربي، پلاک 4  (باجه اداره سهام)  مراجعه فرمايند. ترتيبي داده شده است که بعد از مهلت فوق نيز، در روز و محل برگزاري مجمع عمومي، در فاصله ساعت 7 الي 8 با اخذ مدارک مربوطه برگ ورود به مجمع صادر گردد. همچنين پخش مستقيم و همزمان مراسم مجمع از طريق وب سايت بانک به آدرس www.parsian-bank.ir نيز انجام خواهد شد. ضروري است مستندات مؤيد نمايندگي و وکالت، ولايت يا قيوميت حداقل سه روز قبل از تاريخ تشکيل مجمع عمومي به اداره سهام بانک، در قبال اخذ رسيد تحويل شود. </AgendaItem><AgendaItem>دعوت کننده مجمع : هيات مديره بانک پارسيان</AgendaItem></Agenda></Root>"
# # content= "<Root><Type Code=\"17\" Title=\"آگهی دعوت به مجمع عمومی عادی بطور فوق العاده\" /><YearEndToDate>1403/04/31</YearEndToDate><PlaceAndDateTime><Date>1403/04/31</Date><Time>11:00</Time><Place>شهرک قدس (غرب) انتهاي بلوار شهيد دادمان پژوهشگاه نيرو سالن خليج فارس</Place></PlaceAndDateTime><Agenda><AgendaItem>انتخاب اعضای هیئت‌مدیره</AgendaItem><AgendaItem>سایر موارد</AgendaItem><AgendaItem>توضیحات :ساير مواردي که قابل طرح در مجمع عمومي عادي به طور فوق العاده باشد.</AgendaItem><AgendaItem>شماره سریال شهر : 228</AgendaItem><AgendaItem>نام شهر : تهران</AgendaItem><AgendaItem>شماره سریال استان : 7</AgendaItem><AgendaItem>نام استان : تهران</AgendaItem><AgendaItem>نحوه دریافت برگ ورود به جلسه : بدينوسيله از کليه سهامداران محترم بانک پارسيان دعوت مي شود به منظور اخذ برگ ورود به جلسه از تاريخ 27 تير ماه لغايت 30 تير  ماه 1403، در روز و ساعات اداري با در دست داشتن مدارک مالکيت سهام و ارائه کارت شناسايي معتبر، به اداره سهام بانک واقع در تهران ، شهرک قدس (غرب)، بلوار شهيد فرحزادي، خيابان زرافشان غربي، پلاک 4 (باجه اداره سهام) مراجعه فرمايند. ترتيبي داده شده است که بعد از مهلت فوق نيز، در روز و محل برگزاري مجمع عمومي، در فاصله ساعت 7 الي11 با اخذ مدارک مربوطه برگ ورود به مجمع صادر گردد. همچنين پخش مستقيم و همزمان مراسم مجمع از طريق وب سايت بانک به آدرس www.parsian-bank.ir نيز انجام خواهد شد. ضروري است مستندات مؤيد نمايندگي و وکالت، ولايت يا قيوميت حداقل سه روز قبل از تاريخ تشکيل مجمع عمومي به اداره سهام بانک، در قبال اخذ رسيد تحويل شود.</AgendaItem><AgendaItem>دعوت کننده مجمع : هيات مديره بانک پارسيان</AgendaItem></Agenda></Root>"
# # content= "<Root><Type Code=\"18\" Title=\"آگهی دعوت به مجمع عمومی فوق العاده\" /><PlaceAndDateTime><Date>1393/06/26</Date><Time>09:00</Time><Place>تهران - بزرگراه نيايش بعد از پل شهيدستاري جنب پمپ بنزين ايران پارس خيابان شقايق کوچه دهم سالن مجتمع فرهنگي آدينه</Place></PlaceAndDateTime><Agenda><AgendaItem>تطابق اساسنامه شرکت با نمونه اساسنامه سازمان بورس</AgendaItem><AgendaItem>امضا کننده: [Ali Soleymani Shayesteh] اطلاعات نمایش داده شده با اطلاعات امضا شده مطابقت دارد.</AgendaItem><AgendaItem>امضا کننده: [Ali Soleymani Shayesteh]</AgendaItem><AgendaItem>اطلاعات نمایش داده شده با اطلاعات امضا شده مطابقت دارد.</AgendaItem></Agenda></Root>"

root = ET.fromstring(content)

# Extract relevant data
data = {
    "Type Code": root.find(".//Type").get("Code"),
    "Title": root.find(".//Type").get("Title"),
    "YearEndToDate": root.find(".//YearEndToDate").text,
    "Date": root.find(".//PlaceAndDateTime/Date").text,
    "Time": root.find(".//PlaceAndDateTime/Time").text,
    "Place": root.find(".//PlaceAndDateTime/Place").text,
    "Agenda": [item.text for item in root.findall(".//AgendaItem")]
}

# Convert to DataFrame
df = pd.DataFrame(data)
df.to_csv("./majed2.csv")
print(df)

from src.base_functions import make_url, get_data, data_to_js, js_to_df, add_datetime_column, remove_columns, df_to_js, \
    rename_columns


def get_assembly_announcement_data(instrument_code: str) -> dict:
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
    base_url = "https://cdn.tsetmc.com/api/Codal/GetStatementContentByInsCode/12/0/-1"

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
        data = get_data(api_url)

        # Step 3: Parse the raw data into a JSON format with the key 'preparedData'.
        data = data_to_js(data, 'statemetnContent')

        # Step 4: Convert the parsed JSON data into a Pandas DataFrame.
        data = js_to_df(data)
        # Step 6: Remove unnecessary columns from the DataFrame for better clarity.
        data = remove_columns(data, columns_to_remove)
        column_renames = {"sentDateTime_Gregorian": "DateTime"}
        data = rename_columns(data, column_renames)
        data.to_csv('./majed.csv')
        # Step 8: Convert the cleaned DataFrame back into JSON format.
        data = df_to_js(data)
        # Return the final JSON data after processing.
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
