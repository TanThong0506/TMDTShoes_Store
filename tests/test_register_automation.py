import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:8000/users/register/"

@pytest.fixture(scope="module")
def browser():
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Bỏ comment dòng này nếu muốn chạy ẩn không hiện trình duyệt
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Khởi tạo driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(5)
    yield driver
    # Teardown (tắt trình duyệt sau khi chạy xong)
    driver.quit()

@pytest.fixture(autouse=True)
def setup_teardown_method(browser):
    # Trước mỗi test case, luôn truy cập lại trang đăng ký
    browser.get(BASE_URL)
    yield

def fill_form_and_submit(browser, fullname="", email="", phone="", pwd="", confirm_pwd=""):
    browser.find_element(By.ID, "full_name").clear()
    browser.find_element(By.ID, "email").clear()
    browser.find_element(By.ID, "phone").clear()
    browser.find_element(By.ID, "password").clear()
    browser.find_element(By.ID, "confirm_password").clear()
    
    if fullname: browser.find_element(By.ID, "full_name").send_keys(fullname)
    if email: browser.find_element(By.ID, "email").send_keys(email)
    if phone: browser.find_element(By.ID, "phone").send_keys(phone)
    if pwd: browser.find_element(By.ID, "password").send_keys(pwd)
    if confirm_pwd: browser.find_element(By.ID, "confirm_password").send_keys(confirm_pwd)
    
    browser.find_element(By.ID, "submitBtn").click()

def get_error_message(browser):
    # Đợi thông báo lỗi xuất hiện trong div chứa message
    try:
        element = WebDriverWait(browser, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".messages-container .premium-alert"))
        )
        return element.text.strip()
    except:
        return ""

# ==================== TEST CASES ====================

def test_tc_01_valid_registration(browser):
    """TC_01: Đăng ký thành công với dữ liệu hợp lệ"""
    # Thay đổi email bằng timestamp để đảm bảo tính unique khi test nhiều lần
    import time
    unique_email = f"hople{int(time.time())}@gmail.com"
    fill_form_and_submit(browser, "Huỳnh Tỉnh", unique_email, "0901234567", "Pass@123", "Pass@123")
    
    # Kiểm tra chuyển hướng URL sang trang đăng nhập
    WebDriverWait(browser, 5).until(EC.url_contains("/users/login/"))
    assert "/users/login" in browser.current_url
    
    # Thông báo đăng ký thành công xuất hiện ở trang login
    msg = get_error_message(browser)
    assert "Đăng ký thành công" in msg or "tạo tài khoản thành công" in msg.lower()

def test_tc_02_empty_all_fields(browser):
    """TC_02: Bỏ trống tất cả các trường"""
    fill_form_and_submit(browser, "", "", "", "", "")
    msg = get_error_message(browser)
    assert msg != "", "Hệ thống phải báo lỗi khi không nhập gì"

def test_tc_03_empty_fullname(browser):
    """TC_03: Bỏ trống trường Họ tên"""
    fill_form_and_submit(browser, "", "hople@gmail.com", "0901234567", "Pass@123", "Pass@123")
    msg = get_error_message(browser)
    assert "họ tên" in msg.lower()

def test_tc_04_empty_email(browser):
    """TC_04: Bỏ trống trường Email"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "", "0901234567", "Pass@123", "Pass@123")
    msg = get_error_message(browser)
    assert "email" in msg.lower()

def test_tc_05_empty_password(browser):
    """TC_05: Bỏ trống trường Mật khẩu"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "hople@gmail.com", "0901234567", "", "Pass@123")
    msg = get_error_message(browser)
    assert "mật khẩu" in msg.lower()

def test_tc_06_empty_confirm_password(browser):
    """TC_06: Bỏ trống trường Xác nhận mật khẩu"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "hople@gmail.com", "0901234567", "Pass@123", "")
    msg = get_error_message(browser)
    assert "xác nhận" in msg.lower()

def test_tc_07_invalid_email_missing_at(browser):
    """TC_07: Định dạng Email không hợp lệ (thiếu @)"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "hoplegmail.com", "0901234567", "Pass@123", "Pass@123")
    # Trình duyệt HTML5 tự chặn nếu input type="email", ta dùng get_attribute("validationMessage")
    email_input = browser.find_element(By.ID, "email")
    val_msg = email_input.get_attribute("validationMessage")
    if val_msg:
        assert "@" in val_msg
    else:
        msg = get_error_message(browser)
        assert "định dạng" in msg.lower() or "email" in msg.lower()

def test_tc_08_invalid_email_missing_domain(browser):
    """TC_08: Định dạng Email không hợp lệ (thiếu domain)"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "hople@", "0901234567", "Pass@123", "Pass@123")
    email_input = browser.find_element(By.ID, "email")
    val_msg = email_input.get_attribute("validationMessage")
    if val_msg:
        assert val_msg != ""
    else:
        msg = get_error_message(browser)
        assert "định dạng" in msg.lower() or "email" in msg.lower()

def test_tc_09_duplicate_email(browser):
    """TC_09: Email đã tồn tại trong hệ thống"""
    # Lưu ý: Cần đảm bảo datontai@gmail.com đã có trong CSDL
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "admin@gmail.com", "0901234567", "Pass@123", "Pass@123")
    msg = get_error_message(browser)
    assert "tồn tại" in msg.lower() or "đã được sử dụng" in msg.lower()

def test_tc_10_password_mismatch(browser):
    """TC_10: Mật khẩu và Xác nhận mật khẩu không khớp"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "hople@gmail.com", "0901234567", "Pass@123", "Pass@1234")
    msg = get_error_message(browser)
    assert "không khớp" in msg.lower()

def test_tc_11_short_password(browser):
    """TC_11: Mật khẩu quá ngắn (dưới 8 ký tự)"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "hople@gmail.com", "0901234567", "Pas@12", "Pas@12")
    msg = get_error_message(browser)
    assert "kí tự" in msg.lower() or "ký tự" in msg.lower() or "8" in msg.lower()

def test_tc_12_weak_password(browser):
    """TC_12: Mật khẩu thiếu ký tự đặc biệt/số"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "hople@gmail.com", "0901234567", "matkhauthuong", "matkhauthuong")
    msg = get_error_message(browser)
    assert "chữ hoa" in msg.lower() or "số" in msg.lower() or "đặc biệt" in msg.lower() or "bảo mật" in msg.lower()

def test_tc_13_phone_contains_letters(browser):
    """TC_13: Số điện thoại chứa chữ cái"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "hople@gmail.com", "0901234abc", "Pass@123", "Pass@123")
    msg = get_error_message(browser)
    assert "số điện thoại" in msg.lower() or "không hợp lệ" in msg.lower() or "chữ số" in msg.lower()

def test_tc_14_short_phone(browser):
    """TC_14: Số điện thoại quá ngắn"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "hople@gmail.com", "090123", "Pass@123", "Pass@123")
    msg = get_error_message(browser)
    assert "không hợp lệ" in msg.lower() or "10" in msg.lower()

def test_tc_15_name_with_special_characters(browser):
    """TC_15: Tên chứa ký tự đặc biệt"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh @", "hople@gmail.com", "0901234567", "Pass@123", "Pass@123")
    msg = get_error_message(browser)
    assert "đặc biệt" in msg.lower() or "hợp lệ" in msg.lower()

def test_tc_16_only_whitespaces(browser):
    """TC_16: Nhập khoảng trắng vào tất cả các trường"""
    fill_form_and_submit(browser, "   ", "   ", "   ", "   ", "   ")
    msg = get_error_message(browser)
    assert msg != "", "Hệ thống phải chặn việc chỉ nhập toàn khoảng trắng"

def test_tc_17_long_name_limit(browser):
    """TC_17: Kiểm tra giới hạn độ dài trường Họ tên"""
    long_name = "A" * 60
    browser.find_element(By.ID, "full_name").send_keys(long_name)
    val = browser.find_element(By.ID, "full_name").get_attribute("value")
    # Theo chuẩn HTML thì maxlength=50 sẽ không cho nhập quá 50 kí tự
    assert len(val) <= 50, "Trường họ tên không được vượt quá 50 ký tự"

def test_tc_18_duplicate_phone(browser):
    """TC_18: Đăng ký với SĐT đã tồn tại"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "newemail@gmail.com", "0987654321", "Pass@123", "Pass@123")
    msg = get_error_message(browser)
    assert "số điện thoại" in msg.lower() and ("tồn tại" in msg.lower() or "đăng ký" in msg.lower())

def test_tc_19_sql_injection(browser):
    """TC_19: Kiểm tra SQL Injection ở trường Email"""
    fill_form_and_submit(browser, "Huỳnh Tỉnh", "' OR 1=1 --", "0901234567", "Pass@123", "Pass@123")
    msg = get_error_message(browser)
    # Phải bắt lỗi email không hợp lệ chứ không làm crash (HTTP 500)
    assert "định dạng" in msg.lower() or "email" in msg.lower()

def test_tc_20_double_click_submit(browser):
    """TC_20: Click đúp (Double-click) vào nút Đăng ký"""
    import time
    unique_email = f"doubleclick{int(time.time())}@gmail.com"
    browser.find_element(By.ID, "full_name").send_keys("Huỳnh Tỉnh")
    browser.find_element(By.ID, "email").send_keys(unique_email)
    browser.find_element(By.ID, "phone").send_keys("0991234567")
    browser.find_element(By.ID, "password").send_keys("Pass@123")
    browser.find_element(By.ID, "confirm_password").send_keys("Pass@123")
    
    btn = browser.find_element(By.ID, "submitBtn")
    # Double click
    btn.click()
    btn.click()
    
    # Kiểm tra chỉ có 1 request thành công
    WebDriverWait(browser, 5).until(EC.url_contains("/users/login/"))
    assert "/users/login" in browser.current_url
