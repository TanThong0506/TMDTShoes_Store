import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def add_heading(doc, text, level):
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.name = 'Arial'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')

def create_doc():
    doc = Document()
    
    # Tiêu đề
    title = doc.add_heading('TỔNG HỢP BÀI TẬP QC MANUAL - TUẦN 2', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('Dự án: Hệ thống Thương mại Điện tử Shoes Store').alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('Bao gồm: 20 Test case đăng ký, Test Plan mẫu và Bài tập thiết kế test case.').alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # 1. Viết 20 Test Case cho Form Đăng ký
    add_heading(doc, '1. Viết 20 Test Case cho Form Đăng ký', 1)
    
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'ID'
    hdr_cells[1].text = 'Tiêu đề Test Case'
    hdr_cells[2].text = 'Tiền điều kiện'
    hdr_cells[3].text = 'Kết quả mong đợi'
    
    # Make header bold
    for cell in hdr_cells:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True

    test_cases = [
        ['TC_REG_01', 'Đăng ký thành công với dữ liệu hợp lệ', 'Chưa đăng nhập', 'Chuyển hướng sang trang đăng nhập, báo "Đăng ký thành công"'],
        ['TC_REG_02', 'Bỏ trống tất cả các trường', 'Chưa đăng nhập', 'Chặn không cho submit, báo "Vui lòng nhập đầy đủ"'],
        ['TC_REG_03', 'Bỏ trống trường Họ tên', 'Nhập đủ các trường khác', 'Chặn submit, báo "Vui lòng nhập họ tên"'],
        ['TC_REG_04', 'Bỏ trống trường Email', 'Nhập đủ các trường khác', 'Chặn submit, báo "Vui lòng nhập email"'],
        ['TC_REG_05', 'Bỏ trống trường Mật khẩu', 'Nhập đủ các trường khác', 'Chặn submit, báo "Vui lòng nhập mật khẩu"'],
        ['TC_REG_06', 'Bỏ trống trường Xác nhận mật khẩu', 'Nhập đủ các trường khác', 'Chặn submit, báo "Vui lòng xác nhận mật khẩu"'],
        ['TC_REG_07', 'Nhập khoảng trắng vào tất cả các trường', 'Chưa đăng nhập', 'Chặn submit, coi như bỏ trống'],
        ['TC_REG_08', 'Định dạng Email không hợp lệ (Thiếu @)', 'Nhập abcgmail.com', 'Báo lỗi email không đúng định dạng'],
        ['TC_REG_09', 'Định dạng Email không hợp lệ (Thiếu domain)', 'Nhập abc@', 'Báo lỗi email không đúng định dạng'],
        ['TC_REG_10', 'Email đã tồn tại trong hệ thống', 'Email đã có trong DB', 'Báo lỗi "Email này đã được sử dụng"'],
        ['TC_REG_11', 'Số điện thoại chứa chữ cái', 'Nhập 0901234abc', 'Báo lỗi "Số điện thoại chỉ được chứa chữ số"'],
        ['TC_REG_12', 'Số điện thoại quá ngắn', 'Nhập 090123', 'Báo lỗi "Số điện thoại không hợp lệ"'],
        ['TC_REG_13', 'Đăng ký với SĐT đã tồn tại', 'SĐT đã có trong DB', 'Báo lỗi "Số điện thoại đã được đăng ký"'],
        ['TC_REG_14', 'Mật khẩu quá ngắn (< 8 ký tự)', 'Nhập Pas@12', 'Báo lỗi "Mật khẩu phải có ít nhất 8 ký tự"'],
        ['TC_REG_15', 'Mật khẩu thiếu ký tự đặc biệt/số', 'Nhập matkhauthuong', 'Báo lỗi "Phải chứa chữ hoa, số và ký tự đặc biệt"'],
        ['TC_REG_16', 'Mật khẩu và Xác nhận mật khẩu không khớp', 'Pass: A@123, Confirm: A@1234', 'Báo lỗi "Mật khẩu xác nhận không khớp"'],
        ['TC_REG_17', 'Họ tên chứa ký tự đặc biệt', 'Nhập Nguyễn Văn A @', 'Báo lỗi "Họ tên không được chứa ký tự đặc biệt"'],
        ['TC_REG_18', 'Vượt giới hạn độ dài trường Họ tên', 'Nhập chuỗi > 50 ký tự', 'Form HTML chặn không cho gõ thêm, hoặc server báo lỗi'],
        ['TC_REG_19', 'Kiểm tra SQL Injection ở trường Email', "Nhập ' OR 1=1 --", 'Không bị lỗi database, báo lỗi định dạng email'],
        ['TC_REG_20', 'Click đúp (Double-click) vào nút Đăng ký', 'Điền thông tin hợp lệ', 'Hệ thống chỉ tạo 1 tài khoản, không báo lỗi duplicate']
    ]

    for tc in test_cases:
        row_cells = table.add_row().cells
        row_cells[0].text = tc[0]
        row_cells[1].text = tc[1]
        row_cells[2].text = tc[2]
        row_cells[3].text = tc[3]

    doc.add_page_break()
    
    # 2. Test Plan mẫu
    add_heading(doc, '2. Nộp Test Plan mẫu (BT 1.2: Viết Test Plan Đăng ký)', 1)
    plan_text = """TEST PLAN: MODULE ĐĂNG KÝ (SHOES STORE)

1. Giới thiệu: Kế hoạch này phác thảo chiến lược kiểm thử cho Module Đăng Ký Tài Khoản của hệ thống Shoes Store.

2. Phạm vi kiểm thử (Scope):
- In-scope: UI/UX của form đăng ký, Validate dữ liệu đầu vào (Email, Pass, SĐT, Tên), Chức năng lưu DB, Xử lý lỗi trùng lặp.
- Out-of-scope: Tính năng Quên mật khẩu, Tính năng Đăng nhập.

3. Chiến lược kiểm thử (Test Strategy):
- Functional Testing: Đảm bảo logic tạo tài khoản hoạt động.
- Security Testing: SQL Injection, XSS trên các field.
- Kỹ thuật thiết kế: BVA, EP, Decision Table, Error Guessing.

4. Môi trường: Trình duyệt Chrome/Edge (Desktop & Mobile view). URL: /users/register/.

5. Lịch trình & Nhân sự: 1 QA thực hiện thiết kế test case (2 giờ), thực thi test (2 giờ), log bug (1 giờ).

6. Tiêu chí Pass/Fail: Tính năng Pass khi 100% test case mức High/Critical pass. Không có bug crash hệ thống."""
    doc.add_paragraph(plan_text)

    # 3. Kỹ thuật thiết kế Test Case
    add_heading(doc, '3. Lời giải Các Kỹ Thuật Thiết Kế Test Case', 1)

    add_heading(doc, 'BT 3.1: Phân vùng tương đương - Equivalence Partition (EP)', 2)
    doc.add_paragraph('Áp dụng cho trường: Mật khẩu (Yêu cầu ≥ 8 ký tự, có chữ hoa, số, ký tự đặc biệt).\n'
                      '- Vùng hợp lệ (Valid): Chuỗi ≥ 8 ký tự, có đủ chữ hoa, số, ký tự đặc biệt (Vd: T@mkhaumanh123).\n'
                      '- Vùng không hợp lệ 1 (Invalid): Chuỗi < 8 ký tự (Vd: T@m12).\n'
                      '- Vùng không hợp lệ 2 (Invalid): Chuỗi ≥ 8 ký tự nhưng THIẾU 1 yếu tố (Vd: tamkhaumanh123 - thiếu chữ hoa/kí tự đặc biệt).')

    add_heading(doc, 'BT 3.2: Phân tích giá trị biên - Boundary Value Analysis (BVA)', 2)
    doc.add_paragraph('Áp dụng cho trường: Độ dài Họ Tên (Yêu cầu: 1 đến 50 ký tự).\n'
                      '- Biên dưới - 1 (Invalid): 0 ký tự (Rỗng) -> Lỗi.\n'
                      '- Biên dưới (Valid): 1 ký tự (Vd: A) -> Thành công.\n'
                      '- Biên trên (Valid): 50 ký tự -> Thành công.\n'
                      '- Biên trên + 1 (Invalid): 51 ký tự -> Báo lỗi hoặc không cho nhập.')

    add_heading(doc, 'BT 3.3: Bảng quyết định (Decision Table)', 2)
    dt_table = doc.add_table(rows=1, cols=5)
    dt_table.style = 'Table Grid'
    dt_hdr = dt_table.rows[0].cells
    dt_hdr[0].text = 'Điều kiện (Conditions)'
    dt_hdr[1].text = 'Rule 1'
    dt_hdr[2].text = 'Rule 2'
    dt_hdr[3].text = 'Rule 3'
    dt_hdr[4].text = 'Rule 4'
    for cell in dt_hdr:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                
    dt_data = [
        ['Nhập đủ tất cả các trường?', 'True', 'False', 'True', 'True'],
        ['Email chưa từng đăng ký?', 'True', '-', 'False', 'True'],
        ['Pass và Confirm Pass khớp?', 'True', '-', '-', 'False'],
        ['Hành động (Actions)', '', '', '', ''],
        ['Tạo tài khoản mới', 'X', '', '', ''],
        ['Hiện thông báo lỗi', '', 'X', 'X', 'X']
    ]
    for dt in dt_data:
        row_cells = dt_table.add_row().cells
        for i in range(5):
            row_cells[i].text = dt[i]

    add_heading(doc, 'BT 3.4: Chuyển đổi trạng thái (State Transition)', 2)
    doc.add_paragraph('Áp dụng cho: Trạng thái của một Email trong hệ thống.\n'
                      '- State 1 (Khách): Email chưa có trong DB -> Action: Nhấn Đăng ký -> State 2.\n'
                      '- State 2 (Thành viên): Tài khoản được tạo -> Action: Nhấn Đăng nhập -> State 3.\n'
                      '- State 3 (Active): Đăng nhập thành công, có quyền mua hàng.\n'
                      '- (Nếu nhập sai mật khẩu quá 5 lần ở State 2 -> Chuyển sang State 4: Bị khóa).')

    add_heading(doc, 'BT 3.5: Đoán lỗi (Error Guessing)', 2)
    doc.add_paragraph('Kỹ thuật này dùng kinh nghiệm của QC để đoán các lỗi Dev hay mắc phải.\n'
                      '1. Người dùng nhập vào toàn là phím Space (khoảng trắng) ở tất cả các trường.\n'
                      '2. Người dùng copy-paste một mã HTML/Javascript độc hại <script>alert(1)</script> vào trường Họ Tên (XSS).\n'
                      '3. Dev quên không disable nút "Đăng Ký", dẫn đến người dùng bấm đúp (Click 2 lần liên tục) tạo ra 2 user giống hệt nhau.')

    add_heading(doc, 'BT 4.1: Phân bổ Test Suite', 2)
    doc.add_paragraph('Gom 20 Test Cases thành các nhóm (Suites) để dễ quản lý:\n'
                      '- Suite 1: UI/UX & Field Validation (Kiểm tra giao diện & Ràng buộc field) -> Chứa các TC_02 đến TC_18.\n'
                      '- Suite 2: Functional Testing (Kiểm tra chức năng cốt lõi) -> Chứa TC_01.\n'
                      '- Suite 3: Security & Edge Cases (Kiểm tra bảo mật & Lỗi hiếm) -> Chứa TC_19 (SQLi), TC_20 (Double click).')

    add_heading(doc, 'BT 4.2: Review lỗi Test Case', 2)
    doc.add_paragraph('Tình huống: Một bạn QC viết Test Case như sau:\n'
                      'Tiêu đề: Đăng ký thành công.\n'
                      'Các bước: Nhập thông tin. Bấm Đăng ký.\n'
                      'Kết quả mong đợi: Web chạy tốt.\n\n'
                      'Đánh giá (Review) và sửa lại:\n'
                      'Test case trên bị sai ở điểm: KHÔNG RÕ RÀNG. Không ai biết "thông tin" là thông tin gì, và "chạy tốt" là như thế nào.\n'
                      'Sửa lại chuẩn chỉnh:\n'
                      '- Tiêu đề: Đăng ký tài khoản thành công với dữ liệu hợp lệ.\n'
                      '- Các bước: 1. Truy cập URL /register. 2. Nhập Tên: \'Nguyen A\', Email \'a@gmail.com\', Pass: \'A@123\', Confirm: \'A@123\'. 3. Click Submit.\n'
                      '- Kết quả mong đợi: Form submit thành công, DB lưu user \'a@gmail.com\'. Web chuyển sang trang Đăng nhập và hiển thị toast message màu xanh "Đăng ký thành công".')

    doc.save('QA_Exercises_Answers.docx')

if __name__ == "__main__":
    create_doc()
    print("File docx created successfully!")
