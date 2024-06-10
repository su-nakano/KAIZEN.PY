import gspread
from oauth2client.service_account import ServiceAccountCredentials
from injector import inject, Module, singleton, provider, Injector

class SpreadsheetReader:
    def read_cells(self, sheet, range_name):
        raise NotImplementedError

class GSpreadSheetReader(SpreadsheetReader):
    def __init__(self, creds_file):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        self.client = gspread.authorize(creds)

    def read_cells(self, sheet_id, range_name):
        sheet = self.client.open_by_key(sheet_id).sheet1
        return sheet.get(range_name)

class SpreadsheetService:
    @inject
    def __init__(self, reader: SpreadsheetReader):
        self.reader = reader

    def read_all_cells(self, sheet_id, range_name):
        return self.reader.read_cells(sheet_id, range_name)

class SpreadsheetModule(Module):
    def __init__(self, creds_file):
        self.creds_file = creds_file

    @singleton
    @provider
    def provide_spreadsheet_reader(self) -> SpreadsheetReader:
        return GSpreadSheetReader(self.creds_file)

def main():
    creds_file = 'service_account_credentials.json'
    injector = Injector([SpreadsheetModule(creds_file)])
    service = injector.get(SpreadsheetService)
    sheet_id = '1ckjc-K8Q4FbvDI1cs-efTWVAdGcIF9rHN2zJ699ew9I' # whole url is https://docs.google.com/spreadsheets/d/1ckjc-K8Q4FbvDI1cs-efTWVAdGcIF9rHN2zJ699ew9I/edit#gid=620293082 .
    range_name = 'B11:H12'
    data = service.read_all_cells(sheet_id, range_name)
    for row in data:
        print(row)

if __name__ == "__main__":
    main()
