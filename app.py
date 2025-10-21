import os
import pandas as pd
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# Cấu hình Line Bot từ biến môi trường
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# Đường dẫn đến file Excel - FIXED
EXCEL_FILE = "Kho_nguyen_lieu.xlsx"

def search_material(keyword):
    """Tìm kiếm nguyên liệu theo từ khóa"""
    try:
        # KIỂM TRA FILE TỒN TẠI
        if not os.path.exists(EXCEL_FILE):
            return f"❌ Không tìm thấy file dữ liệu: {EXCEL_FILE}"
        
        # Đọc file Excel
        df = pd.read_excel(EXCEL_FILE, sheet_name='data')
        
        # Chuẩn hóa từ khóa tìm kiếm
        keyword = str(keyword).upper().strip()
        
        print(f"🔍 Đang tìm kiếm: {keyword}")
        
        # Tìm kiếm theo nhiều tiêu chí
        if keyword == "RBF":  # Mã đặc biệt cho cám gạo
            mask = df['Product Name'].str.contains('CÁM GẠO', case=False, na=False)
        elif keyword == "TEST":
            return "✅ Bot đang hoạt động bình thường!"
        else:
            # Tìm theo Product Code hoặc Product Name
            mask = (
                df['Product Code'].astype(str).str.contains(keyword, na=False) |
                df['Product Name'].str.upper().str.contains(keyword, na=False) |
                df['Location'].str.upper().str.contains(keyword, na=False)
            )
        
        results = df[mask]
        
        if results.empty:
            return "❌ Không tìm thấy nguyên liệu phù hợp với từ khóa: " + keyword
        
        # Format kết quả
        response = f"📦 KẾT QUẢ TÌM KIẾM: {keyword}\n"
        response += f"📊 Tổng số: {len(results)} kết quả\n\n"
        
        for i, (_, row) in enumerate(results.head(8).iterrows()):
            response += f"┌─ Mã: {row['Product Code']}\n"
            response += f"├─ Tên: {row['Product Name'][:30]}...\n"
            response += f"├─ Vị trí: {row['Location']}\n"
            response += f"├─ Số lượng: {row['Quantity']}\n"
            response += f"├─ Trọng lượng: {row['Weigh']} kg\n"
            response += f"├─ Tuổi kho: {row['RECEIVE_LIFE _AGE']} ngày\n"
            response += f"└─ Shelf Life: {row.get('SHELF LIFE (DAYS)', 'N/A')} ngày\n\n"
        
        if len(results) > 8:
            response += f"📋 ... và {len(results) - 8} kết quả khác"
            
        return response
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return f"⚠️ Lỗi khi đọc dữ liệu: {str(e)}"

# ... (phần còn lại giữ nguyên)
