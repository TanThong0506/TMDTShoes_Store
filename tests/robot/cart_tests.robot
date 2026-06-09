*** Settings ***
Documentation     Suite kiểm thử tự động cho chức năng Thêm vào giỏ hàng (Regression Test)
Library           SeleniumLibrary
Test Setup        Open Browser To Home Page
Test Teardown     Close Browser

*** Variables ***
${HOME_URL}       http://127.0.0.1:8000/
${BROWSER}        Chrome

*** Test Cases ***
Add Product To Cart
    [Documentation]    Kiểm tra luồng người dùng truy cập trang chủ, chọn sản phẩm và thêm vào giỏ hàng
    [Tags]             Regression    Cart
    
    # Bước 1: Đăng nhập và mở trang chủ
    Go To    http://127.0.0.1:8000/users/login/
    Input Text    name=username    testuser1
    Input Text    name=password    Test@1234
    Scroll Element Into View    css=button[type="submit"]
    Click Button    css=button[type="submit"]
    Wait Until Location Is    http://127.0.0.1:8000/    timeout=5s
    Home Page Should Be Open
    
    # Bước 2: Click vào sản phẩm đầu tiên
    Scroll Element Into View    xpath=(//div[contains(@class, 'premium-product-card')]//ancestor::a)[1]
    Click Element    xpath=(//div[contains(@class, 'premium-product-card')]//ancestor::a)[1]
    Wait Until Page Contains Element    css=.product-title
    
    # Bước 3: Chọn size (Click vào label size đầu tiên chưa disabled)
    Scroll Element Into View    xpath=(//input[@name="size" and not(@disabled)]/following-sibling::label)[1]
    Click Element    xpath=(//input[@name="size" and not(@disabled)]/following-sibling::label)[1]
    
    # Bước 4: Click nút thêm vào giỏ
    Scroll Element Into View    css=button.product-cart-btn
    Click Button    css=button.product-cart-btn
    
    # Bước 5: Xác nhận số lượng giỏ hàng trên Navbar thay đổi hoặc hiện modal báo thành công
    Wait Until Element Contains    id=cart-count    1    timeout=5s

*** Keywords ***
Open Browser To Home Page
    Open Browser    ${HOME_URL}    ${BROWSER}
    Maximize Browser Window

Home Page Should Be Open
    Title Should Be    Shoe Store - Premium
    Wait Until Page Contains Element    css=.premium-product-card
