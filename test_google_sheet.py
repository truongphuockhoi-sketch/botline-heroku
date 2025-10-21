import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("kho_nguyen_lieu").worksheet("DATAAI")  # Thay Tên file Google Sheets bằng tên file bạn upload trên Google Drive

def get_stock(product_code):
    records = sheet.get_all_records()
    for r in records:
        if str(r['Product Code']).strip().lower() == product_code.strip().lower():
            return f"""Tên SP: {r['Product Name']}
Tồn kho: {r['Quantity']}
Vị trí: {r['Location']}
Ngày nhập: {r.get('Input date', '')}"""
    return "Không tìm thấy mã sản phẩm!"

print(get_stock('13541900000030'))  # Thay mã này bằng mã bạn muốn kiểm tra
