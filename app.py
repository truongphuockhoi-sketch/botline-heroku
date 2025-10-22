import os
import pandas as pd
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# Cấu hình Line Bot
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 🔥 URL GOOGLE SHEETS CỦA BẠN - ĐÃ UPDATE
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1h4K0_GwNux1XDNJ0lnMhULqxekqjiV8HdUfBrhL3OoQ/gviz/tq?tqx=out:csv&sheet=Sheet1"

def search_material(keyword):
    """Tìm kiếm nguyên liệu từ Google Sheets"""
    try:
        # Đọc trực tiếp từ Google Sheets
        df = pd.read_csv(GOOGLE_SHEETS_URL)
        
        # Chuẩn hóa từ khóa
        keyword = str(keyword).upper().strip()
        
        print(f"🔍 Tìm kiếm: {keyword}")
        print(f"📊 Tổng số dòng dữ liệu: {len(df)}")
        
        # Tìm kiếm thông minh
        if keyword == "RBF":
            mask = df['Product Name'].str.contains('CÁM GẠO', case=False, na=False)
        elif keyword == "TEST":
            return "✅ Bot hoạt động tốt! Đang đọc từ Google Sheets"
        elif keyword == "HELP":
            return """📋 HƯỚNG DẪN SỬ DỤNG:
• RBF - Xem cám gạo
• Mã số (135114) - Tìm theo mã
• Tên nguyên liệu - Tìm theo tên
• Vị trí - Tìm theo kho
• TEST - Kiểm tra bot"""
        else:
            mask = (
                df['Product Code'].astype(str).str.contains(keyword, na=False) |
                df['Product Name'].str.upper().str.contains(keyword, na=False) |
                df['Location'].str.upper().str.contains(keyword, na=False)
            )
        
        results = df[mask]
        
        if results.empty:
            return f"❌ Không tìm thấy '{keyword}'. Thử mã khác hoặc 'HELP'"
        
        # Format kết quả đẹp
        response = f"📦 KẾT QUẢ: {keyword}\n"
        response += f"📊 Tìm thấy: {len(results)} kết quả\n\n"
        
        for i, (_, row) in enumerate(results.head(5).iterrows()):
            response += f"┌─ 🏷️ Mã: {row['Product Code']}\n"
            response += f"├─ 📛 Tên: {row['Product Name'][:20]}...\n"
            response += f"├─ 📍 Vị trí: {row['Location']}\n"
            response += f"├─ 🔢 Số lượng: {row['Quantity']}\n"
            response += f"├─ ⚖️ Trọng lượng: {row['Weigh']}kg\n"
            response += f"├─ 📅 Tuổi kho: {row['RECEIVE_LIFE _AGE']} ngày\n"
            response += f"└─ ⏳ Shelf Life: {row.get('SHELF LIFE (DAYS)', 'N/A')} ngày\n\n"
        
        if len(results) > 5:
            response += f"📋 ... và {len(results) - 5} kết quả khác"
            
        return response
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return f"⚠️ Lỗi hệ thống: {str(e)}\n📞 Liên hệ IT để được hỗ trợ"

# Webhook handler
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    print(f"📨 Tin nhắn: {user_message}")
    reply_text = search_material(user_message)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

@app.route("/")
def home():
    return "✅ Kho Nguyen Lieu Bot - Google Sheets Version"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
