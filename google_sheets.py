import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config import GOOGLE_SHEETS_ID, GOOGLE_SERVICE_ACCOUNT_JSON


credentials = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_JSON, scopes=['https://www.googleapis.com/auth/spreadsheets'])
service = build('sheets', 'v4', credentials=credentials)

def append_row(data):
    sheets = service.spreadsheets()
    sheet = sheets.get(spreadsheetId=GOOGLE_SHEETS_ID).execute()['sheets'][0]
    sheet_name = sheet['properties']['title']

    entry_type = data.get('entry_type')
    currency = data.get('currency')
    amount = data.get('amount', 0)
    description = data.get('description', '')
    category = data.get('category', '')
    
    if entry_type == "spends":
        column_map = {"usd": "B", "rub": "C"}
    elif entry_type == "incomes":
        column_map = {"usd": "D", "rub": "E"}
    else:
        raise ValueError("invalid entry type")
    
    column = column_map.get(currency)
    
    categories_map = {
        "eating out": 2, "food": 3, "public transport": 4, "taxi": 5, 
        "chill": 6, "shopping": 7, "household": 8, "no category": 9, 
        "new category": 10, "salary": 2, "family": 3, "gifts": 4
    }
    
    row = categories_map.get(category)
    
    if row is None:
        raise ValueError("invalid category")
    
    cell_range = f"{sheet_name}!{column}{row}"
    current_value = sheets.values().get(spreadsheetId=GOOGLE_SHEETS_ID, range=cell_range).execute().get('values', [[0]])[0][0]
    new_value = float(current_value) + amount
    sheets.values().update(
        spreadsheetId=GOOGLE_SHEETS_ID,
        range=cell_range,
        valueInputOption="USER_ENTERED",
        body={"values": [[new_value]]}
    ).execute()

    next_row = get_next_empty_row(sheets, sheet_name)
    date_value = [[datetime.datetime.now().strftime('%d.%m')]]

    if currency == "usd" and entry_type == "spends":
        info_values = [amount, "/", "/", "/"]
    elif currency == "rub" and entry_type == "spends":
        info_values = ["/", amount, "/", "/"]
    elif currency == "usd" and entry_type == "incomes":
        info_values = ["/", "/", amount, "/"]
    elif currency == "rub" and entry_type == "incomes":
        info_values = ["/", "/", "/", amount]

    description_value = [[description]]
    
    sheets.values().update(
        spreadsheetId=GOOGLE_SHEETS_ID,
        range=f"{sheet_name}!A{next_row}",
        valueInputOption="USER_ENTERED",
        body={"values": date_value}
    ).execute()
    
    sheets.values().update(
        spreadsheetId=GOOGLE_SHEETS_ID,
        range=f"{sheet_name}!B{next_row}:E{next_row}",
        valueInputOption="USER_ENTERED",
        body={"values": [info_values]}
    ).execute()
    
    sheets.values().update(
        spreadsheetId=GOOGLE_SHEETS_ID,
        range=f"{sheet_name}!F{next_row}",
        valueInputOption="USER_ENTERED",
        body={"values": description_value}
    ).execute()


def get_next_empty_row(sheets, sheet_name):
    result = sheets.values().get(spreadsheetId=GOOGLE_SHEETS_ID, range=f"{sheet_name}!A:A").execute()
    values = result.get('values', [])
    return len(values) + 1