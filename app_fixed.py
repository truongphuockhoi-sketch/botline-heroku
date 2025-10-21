def find_materials_by_keyword(keyword: str):
    """Tìm tất cả nguyên liệu có chứa keyword trong Product Name"""
    if not sheet:
        return []

    keyword = keyword.strip().lower()
    records = sheet.get_all_records()
    matched = [r for r in records if keyword in str(r.get("Product Name", "")).lower()]
    return matched


def calculate_storage_age(date_str):
    """Tính tuổi lưu kho (ngày) từ Date In"""
    try:
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                date_in = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        delta = datetime.now() - date_in
        return f"{delta.days} ngày"
    except Exception:
        return "Không xác định"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    matches = find_materials_by_keyword(text)

    if matches:
        reply_lines = [f"🔹 Danh sách nguyên liệu có chứa “{text}”:\n"]
        for i, r in enumerate(matches, start=1):
            code = r.get("Item Code", "")
            name = r.get("Product Name", "")
            qty = r.get("Weight", "") or r.get("Quantity", "")
            date_in = str(r.get("Date In", "")).strip()
            tuoi_kho = calculate_storage_age(date_in) if date_in else "Không có dữ liệu ngày nhập"

            reply_lines.append(
                f"{i}️⃣ {code} - {name}\n"
                f"   Số lượng tồn: {qty}\n"
                f"   Ngày nhập: {date_in}\n"
                f"   Tuổi lưu kho: {tuoi_kho}\n"
            )

        reply_text = "\n".join(reply_lines)
    else:
        reply_text = f"Không tìm thấy nguyên liệu có chứa '{text}'.\n(Vui lòng nhập đúng từ khóa trong cột Product Name)"

    line_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
