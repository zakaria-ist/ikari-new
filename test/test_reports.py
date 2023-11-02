import time

from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from conftest import login
from conftest import move_and_click_to_element

def test_MonthPicker_ReportView(driver):
    login(driver)
    driver.get('http://ikari-tmp.c2sg.net/reports/view_report/')
    CategorySelect = Select(driver.find_element_by_xpath('//*[@id="report_category"]'))
    CategorySelect.select_by_index(5)   # Monthly report
    driver.set_page_load_timeout(5)
    time.sleep(1)
    InputMonthPicker = driver.find_element_by_xpath('//*[@id="divCurrentMonth"]/div/div/input')
    move_and_click_to_element(driver, InputMonthPicker)
    MonthPicker = driver.find_element_by_xpath('/html/body/div[5]/div[2]/table/tbody/tr/td/span[1]')
    move_and_click_to_element(driver, MonthPicker)
    # Check if the MonthPicker still appears
    try:
        (driver.find_element_by_xpath('/html/body/div[5]/div[2]/table/tbody/tr/td/span[1]'))
        assert 0
    except NoSuchElementException:
        return