"""
KỊCH BẢN KIỂM THỬ TỰ ĐỘNG BẰNG PYTHON + SELENIUM (Đáp ứng yêu cầu Tháng 2 / Tuần 3)
Yêu cầu:
1. Python: Biến, Kiểu dữ liệu, Vòng lặp, Hàm.
2. Selenium: WebDriver setup, Locator (ID, XPath, CSS Selector).
3. Actions: Click, Type, Submit.
4. Screenshots & Comments.
"""

import time
import os
import sys

# Ép console xuất ra UTF-8 trên Windows
sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# 1. BIẾN & KIỂU DỮ LIỆU (Variables & Data types)
# ==========================================
BASE_URL = "http://127.0.0.1:8000/users/login/"
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")

# List chứa các Dictionary dữ liệu test (Kiểu dữ liệu phức hợp)
test_data = [
    {"username": "invalid_user", "password": "WrongPassword123", "expected": "fail"},
    {"username": "testuser1", "password": "Test@1234", "expected": "pass"}
]

# Đảm bảo thư mục results tồn tại
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# ==========================================
# 2. HÀM KIỂM THỬ (Functions)
# ==========================================
def run_login_tests(url, data_list):
    """
    Hàm thực thi các kịch bản login.
    Sử dụng tham số để truyền url và list dữ liệu.
    """
    # Khởi tạo Selenium WebDriver (WebDriver setup)
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Bỏ comment nếu muốn chạy ngầm không hiện UI
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    
    print(">>> BẮT ĐẦU CHẠY TEST SCRIPT BẰNG SELENIUM PYTHON <<<")
    
    # ==========================================
    # 3. VÒNG LẶP (Loops)
    # ==========================================
    for index, test_case in enumerate(data_list):
        print(f"\nĐang chạy Test Case #{index + 1}: Username = '{test_case['username']}'")
        
        # Mở trang đăng nhập
        driver.get(url)
        time.sleep(1) # Chờ animation (nếu có)
        
        # ==========================================
        # 4. LOCATE ELEMENTS (ID, XPath, CSS Selector) & ACTIONS
        # ==========================================
        
        # Locate bằng ID và nhập liệu (Type / send_keys)
        username_field = driver.find_element(By.ID, "username")
        username_field.clear()
        username_field.send_keys(test_case['username'])
        
        # Locate bằng XPath và nhập liệu
        password_field = driver.find_element(By.XPATH, "//input[@name='password']")
        password_field.clear()
        password_field.send_keys(test_case['password'])
        
        # Locate bằng CSS Selector và cuộn trang tới đó để tránh lỗi Intercepted
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
        time.sleep(0.5)
        
        # Thực hiện Click bằng Javascript để đảm bảo không bị chặn bởi UI
        driver.execute_script("arguments[0].click();", submit_btn)
        
        # ==========================================
        # 5. CHỤP SCREENSHOT (Screenshot capture)
        # ==========================================
        time.sleep(2) # Đợi trang phản hồi
        
        # Tên file động theo status pass/fail
        screenshot_name = f"selenium_login_test_{index + 1}_{test_case['expected']}.png"
        screenshot_path = os.path.join(RESULTS_DIR, screenshot_name)
        
        # Lưu hình ảnh kết quả
        driver.save_screenshot(screenshot_path)
        print(f"[-] Đã chụp ảnh màn hình kết quả tại: {screenshot_path}")
        
        # Kiểm tra trạng thái hiện tại để in log
        current_url = driver.current_url
        if test_case['expected'] == 'pass':
            if current_url == "http://127.0.0.1:8000/":
                print("[+] PASS: Đăng nhập thành công và chuyển hướng về Trang chủ!")
            else:
                print("[-] FAIL: Chạy sai kịch bản mong đợi.")
        else:
            if "login" in current_url:
                print("[+] PASS: Đăng nhập thất bại (đúng như dự kiến), web giữ ở trang login.")
            else:
                print("[-] FAIL: Chạy sai kịch bản mong đợi.")
                
    # Đóng trình duyệt sau khi test xong
    driver.quit()
    print("\n>>> HOÀN THÀNH TEST SCRIPT <<<")

# Điểm bắt đầu của chương trình Python
if __name__ == "__main__":
    run_login_tests(BASE_URL, test_data)
