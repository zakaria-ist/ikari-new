import pytest
from selenium import webdriver
import os
import time

test_browser = 'chromewin'

def login(driver):
    # Login to web
    # print("Logging in!")
    driver.get('http://ikari-tmp.c2sg.net/login/')
    usernameElement = driver.find_element_by_name('username')
    usernameElement.send_keys('staff_1')
    passwordElement = driver.find_element_by_name('password')
    passwordElement.send_keys('Ad123456')
    buttonElement = driver.find_element_by_css_selector('button.btn.btn-lg.btn-login.btn-block')
    move_and_click_to_element(driver, buttonElement)
    driver.set_page_load_timeout(5)
    time.sleep(1)


def move_and_click_to_element(driver, element):
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element(element)
    action.click()
    action.perform()
    time.sleep(0.1)

def reload_with_current_url(driver):
    print(driver.current_url)
    driver.get(driver.current_url)

@pytest.fixture(scope = "session")
def driver(request):
    # Get current directory
    dir = os.path.dirname(__file__)

    if test_browser == 'firefox':
        driver = webdriver.Firefox()
    elif test_browser == 'chromewin':
        filename = dir + '/chromedriver.exe'
        driver = webdriver.Chrome(filename)
    elif test_browser == 'chromemac':
        filename = dir + '/chromedriver'
        driver = webdriver.Chrome(filename)
    else:
        raise Exception("Webdriver was not specified!")

    # tearDown
    request.addfinalizer(driver.quit)

    return driver