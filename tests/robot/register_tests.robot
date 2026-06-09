*** Settings ***
Documentation     Test suite cho API Users - CRUD operations (Chuyển sang test form Đăng ký)
Library           SeleniumLibrary
Library           String
Library           DateTime

Suite Setup       Open Browser To Register Page
Suite Teardown    Close Browser
Test Setup        Go To Register Page

*** Variables ***
${BROWSER}        Chrome
${REGISTER_URL}   http://127.0.0.1:8000/users/register/
${DELAY}          0

*** Keywords ***
Open Browser To Register Page
    ${options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    # Call Method    ${options}    add_argument    --headless
    Call Method    ${options}    add_argument    --no-sandbox
    Call Method    ${options}    add_argument    --disable-dev-shm-usage
    Open Browser    ${REGISTER_URL}    ${BROWSER}    options=${options}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}

Go To Register Page
    Go To    ${REGISTER_URL}
    Wait Until Element Is Visible    id=full_name    timeout=5s

Fill Registration Form And Submit
    [Arguments]    ${fullname}    ${email}    ${phone}    ${password}    ${confirm_password}
    Clear Element Text    id=full_name
    Clear Element Text    id=email
    Clear Element Text    id=phone
    Clear Element Text    id=password
    Clear Element Text    id=confirm_password
    
    Run Keyword If    $fullname != ""    Input Text    id=full_name    ${fullname}
    Run Keyword If    $email != ""       Input Text    id=email        ${email}
    Run Keyword If    $phone != ""       Input Text    id=phone        ${phone}
    Run Keyword If    $password != ""    Input Text    id=password     ${password}
    Run Keyword If    $confirm_password != ""    Input Text    id=confirm_password    ${confirm_password}
    
    # Cuộn trang tới phần tử và dùng JS click để vượt qua lỗi ElementClickInterceptedException
    Scroll Element Into View    id=submitBtn
    Execute Javascript    document.getElementById('submitBtn').click()

Get Error Message
    ${is_visible}=    Run Keyword And Return Status    Wait Until Element Is Visible    css=.messages-container .premium-alert    timeout=3s
    Run Keyword If    ${is_visible}    Get Text    css=.messages-container .premium-alert
    ...    ELSE    Set Variable    ${EMPTY}
    ${msg}=    Run Keyword If    ${is_visible}    Get Text    css=.messages-container .premium-alert
    ...    ELSE    Set Variable    ${EMPTY}
    RETURN    ${msg}

*** Test Cases ***
TC-REG-001 Đăng ký thành công với dữ liệu hợp lệ
    [Documentation]    Xác nhận đăng ký thành công
    ${timestamp}=    Get Current Date    result_format=%Y%m%d%H%M%S
    ${unique_email}=    Set Variable    hople${timestamp}@gmail.com
    ${unique_phone}=    Set Variable    09${timestamp[6:14]}
    Fill Registration Form And Submit    Huỳnh Tỉnh    ${unique_email}    ${unique_phone}    Pass@123    Pass@123
    Wait Until Location Contains    /users/login/    timeout=5s
    Location Should Contain    /users/login
    ${msg}=    Get Error Message
    Should Be True    'Đăng ký thành công' in '${msg}' or 'thành công' in '${msg}'

TC-REG-002 Bỏ trống tất cả các trường
    [Documentation]    Bỏ trống toàn bộ form
    Fill Registration Form And Submit    ${EMPTY}    ${EMPTY}    ${EMPTY}    ${EMPTY}    ${EMPTY}
    ${msg}=    Get Error Message
    Should Not Be Empty    ${msg}

TC-REG-003 Bỏ trống trường Họ tên
    [Documentation]    Xác nhận báo lỗi khi thiếu họ tên
    Fill Registration Form And Submit    ${EMPTY}    hople@gmail.com    0901234567    Pass@123    Pass@123
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Contain    ${msg_lower}    họ tên

TC-REG-004 Bỏ trống trường Email
    [Documentation]    Xác nhận báo lỗi khi thiếu email
    Fill Registration Form And Submit    Huỳnh Tỉnh    ${EMPTY}    0901234567    Pass@123    Pass@123
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Contain    ${msg_lower}    email

TC-REG-005 Bỏ trống trường Mật khẩu
    [Documentation]    Xác nhận báo lỗi khi thiếu mật khẩu
    Fill Registration Form And Submit    Huỳnh Tỉnh    hople@gmail.com    0901234567    ${EMPTY}    Pass@123
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Contain    ${msg_lower}    mật khẩu

TC-REG-006 Bỏ trống trường Xác nhận mật khẩu
    [Documentation]    Xác nhận báo lỗi khi thiếu xác nhận mật khẩu
    Fill Registration Form And Submit    Huỳnh Tỉnh    hople@gmail.com    0901234567    Pass@123    ${EMPTY}
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Contain    ${msg_lower}    xác nhận

TC-REG-007 Định dạng Email không hợp lệ (thiếu @)
    [Documentation]    Xác nhận báo lỗi email sai định dạng
    Fill Registration Form And Submit    Huỳnh Tỉnh    hoplegmail.com    0901234567    Pass@123    Pass@123
    ${val_msg}=    Get Element Attribute    id=email    validationMessage
    ${msg}=    Get Error Message
    ${is_html5_block}=    Run Keyword And Return Status    Should Contain    ${val_msg}    @
    Run Keyword If    not ${is_html5_block}    Should Contain Any    ${msg}    định dạng    email    ignore_case=True

TC-REG-008 Định dạng Email không hợp lệ (thiếu domain)
    [Documentation]    Xác nhận báo lỗi email thiếu domain
    Fill Registration Form And Submit    Huỳnh Tỉnh    hople@    0901234567    Pass@123    Pass@123
    ${val_msg}=    Get Element Attribute    id=email    validationMessage
    ${msg}=    Get Error Message
    ${is_html5_block}=    Run Keyword And Return Status    Should Not Be Empty    ${val_msg}
    Run Keyword If    not ${is_html5_block}    Should Contain Any    ${msg}    định dạng    email    ignore_case=True

TC-REG-009 Email đã tồn tại trong hệ thống
    [Documentation]    Xác nhận báo lỗi email trùng
    ${timestamp}=    Get Current Date    result_format=%Y%m%d%H%M%S
    ${unique_phone}=    Set Variable    09${timestamp.replace("2026", "")[0:8]}
    Fill Registration Form And Submit    Huỳnh Tỉnh    admin@gmail.com    ${unique_phone}    Pass@123    Pass@123
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Be True    'tồn tại' in '${msg_lower}' or 'sử dụng' in '${msg_lower}'

TC-REG-010 Mật khẩu và Xác nhận mật khẩu không khớp
    [Documentation]    Xác nhận báo lỗi mật khẩu không khớp
    Fill Registration Form And Submit    Huỳnh Tỉnh    hople@gmail.com    0901234567    Pass@123    Pass@1234
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Contain    ${msg_lower}    không khớp

TC-REG-011 Mật khẩu quá ngắn (dưới 8 ký tự)
    [Documentation]    Xác nhận báo lỗi mật khẩu ngắn
    Fill Registration Form And Submit    Huỳnh Tỉnh    hople@gmail.com    0901234567    Pas@12    Pas@12
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Be True    'kí tự' in '${msg_lower}' or 'ký tự' in '${msg_lower}' or '8' in '${msg_lower}'

TC-REG-012 Mật khẩu thiếu ký tự đặc biệt/số
    [Documentation]    Xác nhận báo lỗi mật khẩu yếu
    Fill Registration Form And Submit    Huỳnh Tỉnh    hople@gmail.com    0901234567    matkhauthuong    matkhauthuong
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Be True    'chữ hoa' in '${msg_lower}' or 'số' in '${msg_lower}' or 'đặc biệt' in '${msg_lower}' or 'bảo mật' in '${msg_lower}'

TC-REG-013 Số điện thoại chứa chữ cái
    [Documentation]    Xác nhận báo lỗi số điện thoại chứa chữ
    Fill Registration Form And Submit    Huỳnh Tỉnh    hople@gmail.com    0901234abc    Pass@123    Pass@123
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Be True    'điện thoại' in '${msg_lower}' or 'hợp lệ' in '${msg_lower}' or 'chữ số' in '${msg_lower}'

TC-REG-014 Số điện thoại quá ngắn
    [Documentation]    Xác nhận báo lỗi số điện thoại ngắn
    Fill Registration Form And Submit    Huỳnh Tỉnh    hople@gmail.com    090123    Pass@123    Pass@123
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Be True    'hợp lệ' in '${msg_lower}' or '10' in '${msg_lower}'

TC-REG-015 Tên chứa ký tự đặc biệt
    [Documentation]    Xác nhận báo lỗi tên không hợp lệ
    Fill Registration Form And Submit    Huỳnh Tỉnh @    hople@gmail.com    0901234567    Pass@123    Pass@123
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Be True    'đặc biệt' in '${msg_lower}' or 'hợp lệ' in '${msg_lower}'

TC-REG-016 Nhập khoảng trắng vào tất cả các trường
    [Documentation]    Xác nhận báo lỗi khi chỉ nhập khoảng trắng
    Fill Registration Form And Submit    ${SPACE}${SPACE}    ${SPACE}${SPACE}    ${SPACE}${SPACE}    ${SPACE}${SPACE}    ${SPACE}${SPACE}
    ${msg}=    Get Error Message
    Should Not Be Empty    ${msg}

TC-REG-017 Kiểm tra giới hạn độ dài trường Họ tên
    [Documentation]    Xác nhận input giới hạn maxlength
    ${long_name}=    Evaluate    "A" * 60
    Input Text    id=full_name    ${long_name}
    ${val}=    Get Element Attribute    id=full_name    value
    ${len}=    Get Length    ${val}
    Should Be True    ${len} <= 50

TC-REG-018 Đăng ký với SĐT đã tồn tại
    [Documentation]    Xác nhận báo lỗi SĐT trùng
    ${timestamp}=    Get Current Date    result_format=%Y%m%d%H%M%S
    ${unique_email}=    Set Variable    newemail${timestamp}@gmail.com
    Fill Registration Form And Submit    Huỳnh Tỉnh    ${unique_email}    0987654321    Pass@123    Pass@123
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Be True    'điện thoại' in '${msg_lower}' and ('tồn tại' in '${msg_lower}' or 'đăng ký' in '${msg_lower}')

TC-REG-019 Kiểm tra SQL Injection ở trường Email
    [Documentation]    Xác nhận báo lỗi injection
    Fill Registration Form And Submit    Huỳnh Tỉnh    ' OR 1=1 --    0901234567    Pass@123    Pass@123
    ${msg}=    Get Error Message
    ${msg_lower}=    Convert To Lower Case    ${msg}
    Should Be True    'định dạng' in '${msg_lower}' or 'email' in '${msg_lower}'

TC-REG-020 Click đúp (Double-click) vào nút Đăng ký
    [Documentation]    Xác nhận tạo 1 account khi double click
    ${timestamp}=    Get Current Date    result_format=%Y%m%d%H%M%S
    ${unique_email}=    Set Variable    double${timestamp}@gmail.com
    ${unique_phone}=    Set Variable    09${timestamp[6:14]}
    Input Text    id=full_name    Huỳnh Tỉnh
    Input Text    id=email        ${unique_email}
    Input Text    id=phone        ${unique_phone}
    Input Text    id=password     Pass@123
    Input Text    id=confirm_password    Pass@123
    
    # Cuộn trang tới phần tử và dùng JS click 2 lần liên tiếp an toàn
    Scroll Element Into View    id=submitBtn
    Execute Javascript    var btn = document.getElementById('submitBtn'); if(btn) { btn.click(); setTimeout(function(){if(document.getElementById('submitBtn')) document.getElementById('submitBtn').click();}, 50); }
    
    Wait Until Location Contains    /users/login/    timeout=5s
    Location Should Contain    /users/login
