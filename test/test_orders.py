from selenium.webdriver.support.select import Select
from conftest import *
from conftest import move_and_click_to_element
from selenium.common.exceptions import NoSuchElementException
from decimal import Decimal


def test_CancelButton_SalesNew(driver):
    login(driver)

    # Sales - Order
    driver.get('http://ikari-tmp.c2sg.net/orders/list/1/')

    # Click on "Add New" button
    AddNewButton = driver.find_element_by_css_selector('a.btn.btn-success.start')
    AddNewButton.click()

    # Search for Cancel button
    CancelButton = driver.find_element_by_css_selector('a.btn.btn-default')
    move_and_click_to_element(driver, CancelButton)


def test_CancelButton_PurchaseNew(driver):
    login(driver)

    # Purchase - Order
    driver.get('http://ikari-tmp.c2sg.net/orders/list/2/')
    # Sort status in ascending order
    driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr/th[2]').click()
    for element in driver.find_elements_by_css_selector('tr.gradeX'):
        # Get order without empty orderitem
        if str(element.find_element_by_xpath('td[2]').text).strip() == 'Draft' \
                and '0.00' != element.find_element_by_xpath('td[8]').text.split()[0] \
                and 'None' not in element.find_element_by_xpath('td[8]').text.split()[0]:
            # Click on "Add New" button
            AddNewButton = driver.find_element_by_css_selector('a.btn.btn-success.start')
            AddNewButton.click()

            # Search for Cancel button
            CancelButton = driver.find_element_by_css_selector('a.btn.btn-default')
            move_and_click_to_element(driver, CancelButton)
            break


def test_CancelButton_SalesEdit(driver):
    login(driver)

    # Sales - Order
    driver.get('http://ikari-tmp.c2sg.net/orders/list/1/')
    # Sort status in ascending order
    driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr/th[2]').click()
    for element in driver.find_elements_by_css_selector('tr.gradeX'):
        # Get order without empty orderitem
        if str(element.find_element_by_xpath('td[2]').text).strip() == 'Draft' \
                and '0.00' != element.find_element_by_xpath('td[8]').text.split()[0] \
                        and 'None' not in element.find_element_by_xpath('td[8]').text.split()[0]:
            # Click on "Edit" button
            ActionButton = driver.find_element_by_css_selector('button.btn.btn-primary.btn-sm.dropdown-toggle')
            move_and_click_to_element(driver, ActionButton)
            EditButton = driver.find_element_by_xpath('//*[@id="dynamic-table"]/tbody/tr[1]/td[9]/div/ul/li[10]/a')
            move_and_click_to_element(driver, EditButton)

            # Search for Cancel button
            CancelButton = driver.find_element_by_css_selector('a.btn.btn-default')
            move_and_click_to_element(driver, CancelButton)
            break

def test_CancelButton_PurchaseEdit(driver):
    login(driver)

    # Purchase - Order
    driver.get('http://ikari-tmp.c2sg.net/orders/list/2/')
    # Sort status in ascending order
    driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr/th[2]').click()
    for element in driver.find_elements_by_css_selector('tr.gradeX'):
        # Get order without empty orderitem
        if str(element.find_element_by_xpath('td[2]').text).strip() == 'Draft' \
                and '0.00' != element.find_element_by_xpath('td[8]').text.split()[0] \
                and 'None' not in element.find_element_by_xpath('td[8]').text.split()[0]:
            # Click on "Edit" button
            ActionButton = driver.find_element_by_css_selector('button.btn.btn-primary.btn-sm.dropdown-toggle')
            move_and_click_to_element(driver, ActionButton)
            EditButton = driver.find_element_by_xpath('//*[@id="dynamic-table"]/tbody/tr[1]/td[9]/div/ul/li[10]/a')
            move_and_click_to_element(driver, EditButton)
            # Search for Cancel button
            CancelButton = driver.find_element_by_css_selector('a.btn.btn-default')
            move_and_click_to_element(driver, CancelButton)
            break


def SalesEdit(driver, amount, flag):
    login(driver)
    # Sale orders
    driver.get('http://ikari-tmp.c2sg.net/orders/list/1/')
    # Sort status in ascending order
    driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr/th[2]').click()
    # for element in driver.find_elements_by_xpath("//*[contains(text(), 'Draft')]"):
    #     print(element.text)
    for element in driver.find_elements_by_css_selector('tr.gradeX'):
        # Get order without empty orderitem
        if str(element.find_element_by_xpath('td[2]').text).strip() == 'Draft' \
                and '0.00' != element.find_element_by_xpath('td[8]').text.split()[0] \
                and 'None' not in element.find_element_by_xpath('td[8]').text.split()[0]:
            move_and_click_to_element(driver, element.find_element_by_xpath('td[9]/div/button[2]'))
            return SalesEditPage(driver, amount, element, flag)
    assert 1


def SalesEditPage(driver, amount, element, flag):
    # Click Edit
    move_and_click_to_element(driver, element.find_element_by_xpath('td[9]/div/ul/li[10]'))
    try:
        # Change amount
        AmountInput = driver.find_element_by_xpath('//*[@id="id_formset_item-0-amount"]')
        move_and_click_to_element(driver, AmountInput)
        AmountInput.clear()
        AmountInput.send_keys(str(amount))
        SaveButton = driver.find_element_by_xpath('//*[@id="btnSave"]')
        if SaveButton.is_displayed() and SaveButton.is_enabled():
            SaveButton.click()  # Back to orders list
            assert flag
        return driver.current_url
    except NoSuchElementException:
        assert 0


def test_SaveNegativeAmount_SalesEdit(driver):
    SalesEdit(driver, -1, False)


def test_SaveChangeAmount_SalesEdit(driver):
    edited_order_url = SalesEdit(driver, 0.01, True)
    # Check if the order's amount gets modified
    driver.get(edited_order_url)
    # Sum all Amount fields
    SubTotalField = driver.find_element_by_xpath('//*[@id="id_subtotal"]')
    move_and_click_to_element(driver, SubTotalField)
    SubTotal = 0
    AmountInputs = driver.find_elements_by_xpath('//*[@id="dynamic-table"]/tbody/tr')
    for input in AmountInputs:
        # print('-' + input.find_element_by_xpath('//td[11]//input').get_attribute('value').strip())
        SubTotal += round(Decimal(input.find_element_by_xpath('//td[13]//input').get_attribute('value').strip()), 2)
    driver.set_page_load_timeout(5)
    time.sleep(1)
    # print('SubTotal = ' + SubTotalField.get_attribute('value').strip())
    print(str(SubTotal) + ' AND ' + SubTotalField.get_attribute('value').strip())
    assert (round(Decimal(SubTotalField.get_attribute('value').strip()), 2) + Decimal(0.1)) >= SubTotal >=\
           (round(Decimal(SubTotalField.get_attribute('value').strip()), 2) - Decimal(0.1))


def test_EmptyAddSaleOrder_SalesNew(driver):
    login(driver)
    driver.get('http://ikari-tmp.c2sg.net/orders/list/1/')
    # Click Add New Order
    move_and_click_to_element(driver,driver.find_element_by_xpath(
        '//*[@id="main-content"]/section/div/div/section[2]/div/div/div/header/span/a[1]'))
    # Add new OrderItem
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="dynamic-table"]/tfoot/tr/td/a'))
    driver.set_page_load_timeout(5)
    time.sleep(1)
    # Get first item
    SearchInput = driver.find_element_by_xpath('//*[@id="search"]')
    move_and_click_to_element(driver, SearchInput)
    SearchInput.send_keys(' ')

    current_amount = driver.find_element_by_xpath('//*[@id="tblData"]/tbody/tr[1]/td[8]').text
    # Select this item
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="tblData"]/tbody/tr[1]/td[13]/input'))
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="btnAddItems"]'))
    # Try to save this order
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="btnSave"]'))
    # Add another order to see if the orderitem's stock gets deducted
    driver.get('http://ikari-tmp.c2sg.net/orders/list/1/')
    # Click Add New Order
    move_and_click_to_element(driver, driver.find_element_by_xpath(
        '//*[@id="main-content"]/section/div/div/section[2]/div/div/div/header/span/a[1]'))
    # Add new OrderItem
    driver.set_page_load_timeout(5)
    time.sleep(1)
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="dynamic-table"]/tfoot/tr/td/a'))
    driver.set_page_load_timeout(5)
    time.sleep(1)
    # Compare with the stock quantity
    # Get first item
    SearchInput = driver.find_element_by_xpath('//*[@id="search"]')
    move_and_click_to_element(driver, SearchInput)
    SearchInput.send_keys(' ')
    assert current_amount == driver.find_element_by_xpath('//*[@id="tblData"]/tbody/tr[1]/td[8]').text


def test_SendButton_SalesOrder(driver):
    login(driver)
    # Sale orders
    driver.get('http://ikari-tmp.c2sg.net/orders/list/1/')
    # Sort status in ascending order
    driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr/th[2]').click()
    # Check each row (each sales order)
    for element in driver.find_elements_by_xpath('//*[@id="dynamic-table"]/tbody/tr'):
        # Get draft order without empty orderitem
        if str(element.find_element_by_xpath('td[2]').text).strip() == 'Draft' \
                and '0.00' != element.find_element_by_xpath('td[8]').text.split()[0] \
                and 'None' not in element.find_element_by_xpath('td[8]').text.split()[0]:
            move_and_click_to_element(driver, element.find_element_by_xpath('td[9]/div/button[2]'))
            # Click Edit
            move_and_click_to_element(driver, element.find_element_by_xpath('td[9]/div/ul/li[10]'))
            # Send button
            SendButton = driver.find_element_by_xpath('//*[@id="btnSendForEdit"]')
            # Check if all required fields are filled
            TitleField = driver.find_element_by_xpath('//*[@id="id_label"]')
            SubTitleField = driver.find_element_by_xpath('//*[@id="id_value"]')
            OrderNoField = driver.find_element_by_xpath('//*[@id="id_number"]')
            SONoField = driver.find_element_by_xpath('//*[@id="id_order_code"]')
            assert (TitleField.get_attribute('value') and SubTitleField.get_attribute('value')
                    and OrderNoField.get_attribute('value') and SONoField.get_attribute('value'))
            # Get all Purchase Code
            PurchaseCodeList = driver.find_elements_by_xpath('//*[@id="dynamic-table"]/tbody/tr/td[5]')
            for code in PurchaseCodeList:
                assert (code.find_element_by_xpath('.//input').get_attribute('value'))
            # Check all validation
            StockError = driver.find_element_by_xpath('//*[@id="items_error"]')
            MinError = driver.find_element_by_xpath('//*[@id="minimum_order_error"]')
            CurrencyError = driver.find_element_by_xpath('//*[@id="currency_error"]')
            ValidateError = driver.find_element_by_xpath('//*[@id="validate_error"]')
            if ((StockError.text is None) and (MinError.text is None)
                and (CurrencyError.text is None) and (ValidateError.text is None)
                and TitleField.get_attribute('value') and SubTitleField.get_attribute('value') and
                    OrderNoField.get_attribute('value') and SONoField.get_attribute('value')):
                # print(str(StockError.text is None) + ' - ' + str(SendButton.is_enabled()))
                assert (SendButton.is_displayed() and SendButton.is_enabled())
                # assert 0
            else:
                assert not (SendButton.is_displayed() and SendButton.is_enabled())
            break


# def test_SendButton_PurchaseOrder(driver):
#     login(driver)
#     # Sale orders List
#     driver.get('http://ikari-tmp.c2sg.net/orders/list/2/')
#     # Sort purchase orders by status
#     move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr/th[2]'))
#     # Check each row (each purchase order)
#     for element in driver.find_elements_by_xpath('//*[@id="dynamic-table"]/tbody/tr'):
#         # Get draft order without empty orderitem
#         if str(element.find_element_by_xpath('td[2]').text).strip() == 'Draft' \
#                 and '0.00' != element.find_element_by_xpath('td[8]').text.split()[0] \
#                 and 'None' not in element.find_element_by_xpath('td[8]').text.split()[0]:
#             move_and_click_to_element(driver, element.find_element_by_xpath('td[9]/div/button[2]'))
#             # Click Edit
#             move_and_click_to_element(driver, element.find_element_by_xpath('td[9]/div/ul/li[9]'))


def test_DeliveryInfo_Customers(driver):
    login(driver)
    # Go to customers page
    driver.get('http://ikari-tmp.c2sg.net/customers/list/')
    try:
        EditButton = driver.find_element_by_xpath('//*[@id="dynamic-table"]/tbody/tr[1]/td[8]/a')
    except NoSuchElementException:
        print('No Customer')
        return
    move_and_click_to_element(driver, EditButton)
    # Delivery Info tab
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="tabs"]/li[4]/a'))
    try:
        DeliInfo = driver.find_element_by_xpath("//*[contains(text(), 'If I die young')]")
        print('OK')
    except NoSuchElementException:
        # Click button Add a Delivery Info
        move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="delivery-table"]/tfoot/tr/td/a'))
        add_delivery_info_url = driver.current_url
        # Try to add with all fields empty
        move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="main-content"]/section/div/section/'
                                                                       'div/form/div[10]/div/button'))
        driver.set_page_load_timeout(5)
        time.sleep(0.1)
        assert (driver.current_url == add_delivery_info_url)
        # Fill name field as required
        NameField = driver.find_element_by_xpath('//*[@id="id_name"]')
        move_and_click_to_element(driver, NameField)
        NameField.send_keys('If I die young')
        # Save this deli info
        move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="main-content"]/section/div/section/'
                                                                       'div/form/div[10]/div/button'))
        driver.set_page_load_timeout(5)
        time.sleep(0.5)
    finally:
        # Search for the deli info
        DeliRows = driver.find_elements_by_xpath('//*[@id="delivery-table"]/tbody/tr')
        for deli in DeliRows:
            print(deli.find_element_by_xpath('td[1]').text)
            if deli.find_element_by_xpath('td[1]').text == 'If I die young':
                for i in range(2, 6):
                    print('-'+deli.find_element_by_xpath('td[' + str(i) + ']').text)
                    assert deli.find_element_by_xpath('td[' + str(i) + ']').text != 'None'
                break


def test_OrderItemTable_PurchaseList(driver):
    login(driver)
    # Order Purchase list
    driver.get('http://ikari-tmp.c2sg.net/orders/list/2/')
    # Get row header
    RowHeaders = driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr')
    print(RowHeaders.text)
    for e in RowHeaders.find_elements_by_xpath('.//th'):
        print(e.text)
        assert ('Sale Code'.lower() != e.text.lower() and 'Sale Price'.lower() != e.text.lower()
                or 'Exchange Rate'.lower() == e.text.lower())


def test_OrderItemTable_PurchaseNew(driver):
    login(driver)
    # Order Purchase list
    driver.get('http://ikari-tmp.c2sg.net/orders/list/2/')
    # Add new button
    move_and_click_to_element(driver, driver.find_element_by_xpath(
        '//*[@id="main-content"]/section/div/div/section[2]/div/div/div/header/span/a[1]'))
    # Get orderitem row header
    RowHeaders = driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr')
    print(RowHeaders.text)
    for e in RowHeaders.find_elements_by_xpath('.//th'):
        print(e.text)
        assert ('Sale Code'.lower() != e.text.lower() and 'Sale Price'.lower() != e.text.lower()
                or 'Exchange Rate'.lower() == e.text.lower())
    # Add new Item
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="dynamic-table"]/tfoot/tr/td/a'))
    time.sleep(0.5)
    # Search box
    SearchBox = driver.find_element_by_xpath('//*[@id="search"]')
    move_and_click_to_element(driver, SearchBox)
    SearchBox.send_keys(' ')
    RowHeaders = driver.find_element_by_xpath('//*[@id="tblData"]/thead/tr')
    print(RowHeaders.text)
    for e in RowHeaders.find_elements_by_xpath('.//th'):
        print(e.text)
        assert ('Sale Code'.lower() != e.text.lower() and 'Sale Price'.lower() != e.text.lower()
                or 'Exchange Rate'.lower() == e.text.lower())


def test_OrderItemTable_PurchaseEdit(driver):
    login(driver)
    # Order Purchase list
    driver.get('http://ikari-tmp.c2sg.net/orders/list/2/')
    # Click on edit
    ActionButton = driver.find_element_by_xpath('//*[@id="dynamic-table"]/tbody/tr[1]/td[9]/div/button[2]')
    move_and_click_to_element(driver, ActionButton)
    EditButton = driver.find_element_by_xpath('//*[@id="dynamic-table"]/tbody/tr[1]/td[9]/div/ul/li[11]/a')
    move_and_click_to_element(driver, EditButton)
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="id_formset_item-0-quantity"]'))
    RowHeaders = driver.find_element_by_xpath('//*[@id="dynamic-table"]/thead/tr')
    print(RowHeaders.text)
    for e in RowHeaders.find_elements_by_xpath('.//th'):
        print(e.text)
        assert ('Sale Code'.lower() != e.text.lower() and 'Sale Price'.lower() != e.text.lower()
                or 'Exchange Rate'.lower() == e.text.lower())
    # Add new Item
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="dynamic-table"]/tfoot/tr/td/a'))
    RowHeaders = driver.find_element_by_xpath('//*[@id="tblData"]/thead/tr').text.strip()
    print('- ' + RowHeaders)
    assert ('Sale Code' not in RowHeaders and 'Sale Price' not in RowHeaders)


def test_CustomerAddr_SalesEdit(driver):
    login(driver)
    # Sales Order list page
    driver.get('http://ikari-tmp.c2sg.net/orders/list/1/')
    ActionButton = driver.find_element_by_xpath('//*[@id="dynamic-table"]/tbody/tr[1]/td[9]/div/button[2]')
    move_and_click_to_element(driver, ActionButton)
    EditButton = driver.find_element_by_xpath('//*[@id="dynamic-table"]/tbody/tr[1]/td[9]/div/ul/li[11]')
    move_and_click_to_element(driver, EditButton)
    move_and_click_to_element(driver, driver.find_element_by_xpath('//*[@id="id_customer_address"]'))
    DeliAddr = Select(driver.find_element_by_xpath('//*[@id="id_customer_address"]'))
    DeliAddr.select_by_index(1)
    assert 'Customer Address' in DeliAddr.first_selected_option.text


def test_CustomerAddr_SalesNew(driver):
    login(driver)
    # Sales Order list page
    driver.get('http://ikari-tmp.c2sg.net/orders/list/1/')
    AddNewButton = driver.find_element_by_xpath(
        '//*[@id="main-content"]/section/div/div/section[2]/div/div/div/header/span/a[1]')
    move_and_click_to_element(driver, AddNewButton)
    DeliAddr = Select(driver.find_element_by_xpath('//*[@id="id_customer_address"]'))
    DeliAddr.select_by_index(1)
    assert 'Customer Address' in DeliAddr.first_selected_option.text
