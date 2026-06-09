*** Settings ***
Documentation     Suite kiểm thử tự động cho chức năng Đăng nhập (Smoke Test)
Library           SeleniumLibrary
Test Setup        Open Browser To Login Page
Test Teardown     Close Browser

*** Variables ***
${LOGIN_URL}        http://127.0.0.1:8000/users/login/
${BROWSER}          Chrome
${VALID_USER}       testuser1
${VALID_PASSWORD}   Test@1234
${INVALID_USER}     invaliduser
${INVALID_PASSWORD}  wrongpass

*** Test Cases ***
Valid Login
    [Documentation]    Đăng nhập thành công với thông tin hợp lệ
    [Tags]             Smoke    Auth
    Input Username    ${VALID_USER}
    Input Password    ${VALID_PASSWORD}
    Submit Credentials
    Welcome Page Should Be Open
    Capture Page Screenshot    filename=login_success.png

Invalid Login
    [Documentation]    Đăng nhập thất bại do sai tài khoản
    [Tags]             Auth
    Input Username    ${INVALID_USER}
    Input Password    ${INVALID_PASSWORD}
    Submit Credentials
    Error Message Should Be Shown
    Capture Page Screenshot    filename=login_fail.png

*** Keywords ***
Open Browser To Login Page
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Maximize Browser Window
    Login Page Should Be Open

Login Page Should Be Open
    Title Should Be    Shoe Store - Premium

Input Username
    [Arguments]    ${username}
    Input Text    name=username    ${username}

Input Password
    [Arguments]    ${password}
    Input Text    name=password    ${password}

Submit Credentials
    Scroll Element Into View    css=button[type="submit"]
    Click Button    css=button[type="submit"]

Welcome Page Should Be Open
    Wait Until Location Is    http://127.0.0.1:8000/    timeout=5s
    Location Should Be    http://127.0.0.1:8000/

Error Message Should Be Shown
    Wait Until Page Contains Element    css=.alert-error    timeout=5s
    Page Should Contain    không chính xác
