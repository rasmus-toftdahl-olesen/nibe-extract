from datetime import timedelta
from pathlib import Path

import gspread

from extract import get_credentials, get_items

# Add sheety-data library - expected to be checked out in ../sheety-data/
import sys
sys.path.append(str(Path(__file__).parent.parent / 'sheety-data'))

from sheety.timeseries import Timeseries


def get_or_create(spreadsheet: gspread.Spreadsheet, name: str) -> gspread.Worksheet:
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(name, 1000, 3)


VALUES_FOR_SHEET = {"outdoor temp.", "return temp.", "addition temperature"}

if __name__ == "__main__":
    gc = gspread.service_account()
    spreadsheet = gc.open("Heatingpump Stats")
    heating_pump_creds = get_credentials()
    heating_pump_items = get_items(*heating_pump_creds)

    for name, (value, fvalue) in heating_pump_items.items():
        if name in VALUES_FOR_SHEET:
            spread_sheet = get_or_create(spreadsheet, name)
            spread_sheet_series = Timeseries(spread_sheet, interval=timedelta(hours=1))
            spread_sheet_series.update(fvalue)
