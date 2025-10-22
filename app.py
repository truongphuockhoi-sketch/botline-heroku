import os
import pandas as pd
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# Cấu hình Line Bot
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# URL Google Sheets của bạn
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1h4K0_GwNux1XDNJ0lnMhULqxekqjiV8HdUfBrhL3OoQ/gviz/tq?tqx=out:csv&sheet=Sheet1"

def search_material(keyword):
    """Tìm kiếm nguyên liệu theo MÃ"""
    try:
        # Đọc trực tiếp từ Google Sheets
        df = pd.read_csv(GOOGLE_SHEETS_URL)
        
        # Chuẩn hóa từ khóa
        keyword = str(keyword).strip().upper()
        
        print(f"🔍 Tìm kiếm mã: {keyword}")
        
        # Tìm kiếm THEO MÃ NGUYÊN LIỆU
        if keyword == "RBF":
            # Tìm tất cả các mã bắt đầu bằng 135114 (cám gạo)
            mask = df['Product Code'].astype(str).str.startswith('135114')
        elif keyword == "TEST":
            return "✅ Bot hoạt động tốt!"
        elif keyword == "HELP":
            return """📋 HƯỚNG DẪN:
• RBF - Xem cám gạo
• Mã số (135114, 135124,...) - Tìm theo mã
• TEST - Kiểm tra bot
• HELP - Hướng dẫn"""
        else:
            # Tìm theo MÃ chính xác hoặc bắt đầu bằng mã
            mask = (
                df['Product Code'].astype(str) == keyword |
                df['Product Code'].astype(str).str.startswith(keyword)
            )
        
        results = df[mask]
        
        if results.empty:
            return f"❌ Không tìm thấy mã '{keyword}'. Thử mã khác hoặc 'HELP'"
        
        # Format kết quả ĐƠN GIẢN
        response = f"📦 KẾT QUẢ MÃ: {keyword}\n"
        response += f"📊 Số lượng: {len(results)} kết quả\n\n"
        
        for i, (_, row) in enumerate(results.iterrows()):
            response += f"┌─ 🏷️ Mã: {row['Product Code']}\n"
            response += f"├─ 📛 Tên: {row['Product Name'][:30]}\n"
            response += f"├─ 📍 Vị trí: {row['Location']}\n"
            response += f"├─ 🔒 Lock: {row.get('Lock', 'N/A')}\n"
            response += f"├─ 🔢 Số lượng: {row.get('Quantity', 'N/A')}\n"
            response += f"├─ ⚖️ KL: {row.get('Weigh', 'N/A')}kg\n"
            response += f"└─ 📅 Storage: {row.get('Storage Age', 'N/A')} ngày\n\n"
            
        return response
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return f"⚠️ Lỗi: {str(e)}"

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
    return "✅ Kho Nguyen Lieu Bot"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
