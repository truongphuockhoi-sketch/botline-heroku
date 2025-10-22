import os
import pandas as pd
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# ==================== KHỞI TẠO FLASK APP ====================
app = Flask(__name__)

# ==================== CẤU HÌNH LINE BOT ====================
# Lấy thông tin từ biến môi trường trên Render
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

# ==================== HÀM ĐỌC VÀ XỬ LÝ EXCEL ====================
def read_excel_data():
    """Đọc dữ liệu từ file Excel"""
    try:
        file_path = 'Kho_nguyen_lieu.xlsx'
        
        if not os.path.exists(file_path):
            return None, "❌ File Excel không tồn tại. Vui lòng kiểm tra lại."
        
        df = pd.read_excel(file_path)
        
        # Kiểm tra cấu trúc file
        required_columns = ['CODE', 'PRODUCT', 'LOCK', 'Quantity', 'Weight', 'Date In', 'Storage Age', 'Remark']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"❌ Thiếu các cột: {', '.join(missing_columns)}"
        
        return df, None
        
    except Exception as e:
        return None, f"❌ Lỗi khi đọc file Excel: {str(e)}"

def search_material(search_code):
    """Tìm kiếm nguyên liệu theo CODE"""
    df, error = read_excel_data()
    
    if error:
        return error
    
    # Chuẩn hóa mã tìm kiếm
    search_code = str(search_code).strip().upper()
    
    # Tìm kiếm chính xác
    results = df[df['CODE'].astype(str).str.upper() == search_code]
    
    if results.empty:
        # Tìm kiếm gần đúng để gợi ý
        all_codes = df['CODE'].astype(str).unique()
        suggestions = [code for code in all_codes if search_code in code.upper()]
        suggestion_text = f" Gợi ý: {', '.join(suggestions[:3])}" if suggestions else ""
        return f"❌ Không tìm thấy mã '{search_code}'.{suggestion_text} Thử mã khác hoặc 'HELP'"
    
    # Format kết quả
    return format_search_results(results, search_code)

def format_search_results(results, search_code):
    """Định dạng kết quả tìm kiếm"""
    response = f"📦 KẾT QUẢ MÃ: {search_code}\n"
    response += f"📊 Số lượng: {len(results)} kết quả\n\n"
    
    for idx, row in results.iterrows():
        response += f"┌─ 🏷️ Mã: {row['CODE']}\n"
        response += f"├─ 📛 Tên: {row['PRODUCT']}\n"
        response += f"├─ 📍 Vị trí: {row['LOCK']}\n"
        response += f"├─ 🔢 Số lượng: {float(row['Quantity']):,.2f}\n"
        response += f"├─ ⚖️ KL: {float(row['Weight'])}kg\n"
        response += f"├─ 📅 Ngày nhập: {row['Date In']}\n"
        response += f"├─ ⏳ Thời gian lưu: {row['Storage Age']} ngày\n"
        
        # Hiển thị Remark nếu có
        if pd.notna(row['Remark']) and str(row['Remark']).strip():
            response += f"└─ 💬 Ghi chú: {row['Remark']}\n"
        else:
            response += "└─ 💬 Ghi chú: Không có\n"
        
        if idx < len(results) - 1:
            response += "\n"  # Khoảng cách giữa các kết quả
    
    return response

def list_all_codes():
    """Liệt kê tất cả mã có trong kho"""
    df, error = read_excel_data()
    
    if error:
        return error
    
    unique_codes = df['CODE'].astype(str).unique()
    codes_list = "\n".join([f"• {code}" for code in sorted(unique_codes)])
    
    return f"📋 DANH SÁCH MÃ ({len(unique_codes)} mã):\n{codes_list}\n\n💡 Gõ mã để xem chi tiết"

def show_help():
    """Hiển thị trợ giúp"""
    help_text = """
🤖 **HƯỚNG DẪN SỬ DỤNG KHO NGUYÊN LIỆU**

🔍 **Tìm kiếm theo mã**: 
   - Gõ mã sản phẩm (ví dụ: FS, LS, RBF)
   - Tìm kiếm chính xác, phân biệt hoa thường

📋 **Lệnh khác**:
   - `HELP`: Hiển thị hướng dẫn
   - `LIST`: Danh sách tất cả mã

💡 **Thông tin hiển thị**:
   - Mã, tên sản phẩm, vị trí kho
   - Số lượng, khối lượng, ngày nhập
   - Thời gian lưu kho, ghi chú
   - Mỗi vị trí LOCK hiển thị riêng
    """
    return help_text

# ==================== ROUTES CHO FLASK APP ====================
@app.route("/")
def home():
    return "🤖 Line Bot for Material Warehouse is Running!"

@app.route("/webhook", methods=['POST'])
def webhook():
    # Xác thực signature
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

# ==================== XỬ LÝ TIN NHẮN TỪ LINE ====================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    
    if user_message.upper() == 'HELP':
        reply_text = show_help()
    elif user_message.upper() == 'LIST':
        reply_text = list_all_codes()
    else:
        reply_text = search_material(user_message)
    
    # Gửi phản hồi
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# ==================== KHỞI ĐỘNG APP ====================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
