import time

from selenium.webdriver.support.ui import Select

from conftest import login
from conftest import move_and_click_to_element

new_supplier = 'A'


def test_DeleteSupplier_SuppliersDelete(driver):
    login(driver)
    # Suppliers - List
    driver.get("http://ikari-tmp.c2sg.net/suppliers/list/")
    # flag = True
    # while flag:
    #     flag = False
    # Sort names in ascending order
    driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr/th[1]').click()
    for element in driver.find_elements_by_css_selector('tr.gradeX'):
        if element.find_element_by_xpath('td[1]').text == new_supplier:
            flag = True
            # Delete this element
            element.find_element_by_xpath('td[8]/a').click()
            print(driver.current_url)
            move_and_click_to_element(driver, driver.find_element_by_xpath(
                '//*[@id="supplier_tab"]/div/section/div/div[10]/div/a[1]'))
            move_and_click_to_element(driver, driver.find_element_by_xpath(
                '//*[@id="delete-dialog"]/div[2]/div/div[2]/form/button'))
            driver.set_page_load_timeout(5)
            time.sleep(1)
            break
    print('cleared all')


def test_AddNewSupplier_SuppliersNew(driver):
    login(driver)

    # Suppliers - List
    driver.get("http://ikari-tmp.c2sg.net/suppliers/list/")
    # Sort names in ascending order
    driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr/th[1]').click()
    driver.set_page_load_timeout(5)
    time.sleep(1)
    NameField = driver.find_elements_by_css_selector('tr.gradeX')
    if NameField is not None:
        for name in NameField:
            if new_supplier == name.find_element_by_xpath('td[1]').text:
                print('duplicate supplier')
                return

    AddNewButton = driver.find_element_by_xpath("//*[@id='main-content']/section/div/div/section/header/span/a[1]")
    AddNewButton.click()

    # Suppliers - Add New Form
    NameField = driver.find_element_by_xpath('//*[@id="name"]')
    CodeField = driver.find_element_by_xpath('//*[@id="code"]')
    TermSelect = Select(driver.find_element_by_xpath('//*[@id="term"]'))
    # Fill up some fields
    NameField.send_keys(new_supplier)
    CodeField.send_keys(new_supplier)
    TermSelect.select_by_index(1)  # 0 days

    # Save and redirect back to Suppliers List page
    SaveButton = driver.find_element_by_xpath('//*[@id="main-content"]/section/div/section/div/form/div[10]/div/button')
    move_and_click_to_element(driver, SaveButton)
    # Sort names in ascending order
    driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr/th[1]').click()
    driver.set_page_load_timeout(5)
    time.sleep(1)
    # Search for the newly added supplier
    for element in driver.find_elements_by_css_selector('tr.gradeX'):
        if element.find_element_by_xpath('td[1]').text == new_supplier:
            # Check term of this element
            element.find_element_by_xpath('td[8]/a').click()
            print(driver.current_url)
            if (str(Select(
                    driver.find_element_by_xpath('//*[@id="term"]')).first_selected_option.text).strip() == '0 days'):
                return
            break
    assert 0


def test_CancelNewSupplier_SuppliersNew(driver):
    login(driver)

    # Suppliers - List
    driver.get("http://ikari-tmp.c2sg.net/suppliers/list/")
    AddNewButton = driver.find_element_by_xpath("//*[@id='main-content']/section/div/div/section/header/span/a[1]")
    AddNewButton.click()

    # Search for Cancel button and click
    CancelButton = driver.find_element_by_xpath('//*[@id="main-content"]/section/div/section/div/form/div[10]/div/a')
    move_and_click_to_element(driver, CancelButton)



def test_EditSupplier_SuppliersEdit(driver):
    login(driver)

    # Suppliers - List
    driver.get("http://ikari-tmp.c2sg.net/suppliers/list/")
    EditButton = driver.find_element_by_xpath('//*[@id="dynamic-table"]/tbody/tr[1]/td[8]/a')
    EditButton.click()
    current_supplier_url = driver.current_url

    # Edit Name field
    NameField = driver.find_element_by_xpath('//*[@id="name"]')
    NameField.send_keys(' - Edit')
    TermSelect = Select(driver.find_element_by_xpath('//*[@id="term"]'))
    TermSelect.select_by_index(4)  # 90 days

    # Search for Save button and save
    SaveButton = driver.find_element_by_xpath('//*[@id="supplier_tab"]/div/section/div/div[10]/div/button')
    move_and_click_to_element(driver, SaveButton)

    # Check if this supplier's term get midified
    driver.get(current_supplier_url)
    TermSelect = Select(driver.find_element_by_xpath('//*[@id="term"]'))
    if str(TermSelect.first_selected_option.text).strip() == '90 days':
        return
    assert 0


def test_CancelEditSupplier_SuppliersEdit(driver):
    login(driver)

    # Suppliers - List
    driver.get("http://ikari-tmp.c2sg.net/suppliers/list/")
    CancelButton = driver.find_element_by_xpath('//*[@id="dynamic-table"]/tbody/tr[1]/td[8]/a')
    CancelButton.click()

    # Search for Cancel button and click
    CancelButton = driver.find_element_by_xpath('//*[@id="supplier_tab"]/div/section/div/div[10]/div/a[2]')
    move_and_click_to_element(driver, CancelButton)
