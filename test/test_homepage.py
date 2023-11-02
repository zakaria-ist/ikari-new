from conftest import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

delay = 3  # seconds


def test_AmountChart_HomePage(driver):
    login(driver)
    # driver.manage().timeouts().pageLoadTimeout(10, TimeUnit.SECONDS)
    driver.implicitly_wait(10)  # seconds
    # Check Current Month Purchase Amount
    try:

        PurchaseMonthAmount = driver.find_element_by_xpath(
            '//*[@id="main-content"]/section/form/div[1]/div[1]/section/div[2]/h1')
        SalesMonthAmount = driver.find_element_by_xpath(
            '//*[@id="main-content"]/section/form/div[1]/div[2]/section/div[2]/h1')
        PurchaseYearAmount = driver.find_element_by_xpath(
            '//*[@id="main-content"]/section/form/div[2]/div[1]/div/div[2]/span[2]')
        SalesYearAmount = driver.find_element_by_xpath(
            '//*[@id="main-content"]/section/form/div[2]/div[2]/div/div[2]/span[2]')
        WebDriverWait(driver, delay).until(EC.presence_of_element_located(
            (By.XPATH,'//*[@id="main-content"]/section/form/div[1]/div[1]/section/div[2]/h1')))
        WebDriverWait(driver, delay).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main-content"]/section/form/div[1]/div[2]/section/div[2]/h1')))
        WebDriverWait(driver, delay).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main-content"]/section/form/div[2]/div[1]/div/div[2]/span[2]')))
        WebDriverWait(driver, delay).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main-content"]/section/form/div[2]/div[2]/div/div[2]/span[2]')))
        print("Page is ready!")
        print ("PurchaseMonthAmount = " + PurchaseMonthAmount.text)
        print ("SalesMonthAmount = " + SalesMonthAmount.text)
        print ("PurchaseYearAmount = " + PurchaseYearAmount.text)
        print ("SalesYearAmount = " + SalesYearAmount.text)

    except TimeoutException:
        print("Loading took too much time!")

def GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath, Title_xpath = '//*[@id="main-content"]/section/div/div/section/header'):
    if (GroupMenu_xpath != ""):
        GroupMenu = driver.find_element_by_xpath(GroupMenu_xpath)
        move_and_click_to_element(driver, GroupMenu)

    time.sleep(0.5)
    Menu = driver.find_element_by_xpath(Menu_xpath)
    move_and_click_to_element(driver, Menu)

    time.sleep(0.8)
    reload_with_current_url(driver)
    Element = driver.find_element_by_xpath(Title_xpath)

    ElementTitle = Element.text

    if (GroupMenu_xpath != ""):
        GroupMenu = driver.find_element_by_xpath(GroupMenu_xpath)
        move_and_click_to_element(driver, GroupMenu)

    print("MenuTitle : " + ElementTitle)
    return ElementTitle


def test_Menu_Home(driver):
    login(driver)
    Menu_xpath = '//*[@id="nav-accordion"]/li[1]/a/span'
    Title_xpath = '//*[@id="main-content"]/section/form/div[2]/div[1]/div/div[1]/div/div[1]/span'
    assert 'Monthly Purchase' in GetMenuTitle(driver, "", Menu_xpath, Title_xpath)

def test_Menu_Staff(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[2]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[2]/ul/li[1]/a'
    assert 'Staff List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_PartGroup(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[4]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[4]/ul/li[6]/a'
    assert 'Category List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_CostCenter(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[2]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[2]/ul/li[2]/a'
    assert 'Cost Centers List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Bank(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[3]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[3]/ul/li[1]/a'
    assert 'Bank List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_TransactionType(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[3]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[3]/ul/li[2]/a'
    assert 'Transaction Type List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_PaymentMode(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[3]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[3]/ul/li[3]/a'
    assert 'Payment Mode List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_ExchangeRate(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[3]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[3]/ul/li[4]/a'
    assert 'Exchange Rate List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Customer(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[4]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[4]/ul/li[1]/a'
    assert 'Customer List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Supplier(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[4]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[4]/ul/li[2]/a'
    assert 'Supplier List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Contact(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[4]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[4]/ul/li[3]/a'
    assert 'Contact List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Location(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[4]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[4]/ul/li[4]/a'
    assert 'Location List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Item(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[4]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[4]/ul/li[5]/a'
    assert 'Item List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Delivery(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[4]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[4]/ul/li[7]/a'
    assert 'Delivery List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_SalesOrder(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[5]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[5]/ul/li[1]/a'
    Title_xpath = '//*[@id="main-content"]/section/div/div/section[2]/div/div/div/header'
    assert 'Sales Order List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath, Title_xpath)

def test_Menu_PurchaseOrder(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[5]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[5]/ul/li[2]/a'
    Title_xpath = '//*[@id="main-content"]/section/div/div/section[2]/div/div/div/header'
    assert 'Purchases Order List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath, Title_xpath)

def test_Menu_GoodOrder(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[5]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[5]/ul/li[3]/a'
    Title_xpath = '//*[@id="main-content"]/section/div/div/section[2]/div/div/div/header'
    assert 'Goods Receive List' in  GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath, Title_xpath)

def test_Menu_Invoice(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[5]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[5]/ul/li[4]/a'
    Title_xpath = '//*[@id="main-content"]/section/div/div/section[2]/div/div/div/header'
    assert 'Delivery Order/Invoice' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath, Title_xpath)

def test_Menu_Report(driver):
    login(driver)
    Menu_xpath = '//*[@id="nav-accordion"]/li[6]/a/span'
    Title_xpath = '//*[@id="main-content"]/section/div/div[1]/section[1]/header'
    assert 'Report List' in GetMenuTitle(driver, "", Menu_xpath, Title_xpath)

def test_Menu_Tax(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[7]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[7]/ul/li[1]/a'
    assert 'Tax List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Currency(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[7]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[7]/ul/li[2]/a'
    assert 'Currency List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Country(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[7]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[7]/ul/li[3]/a'
    assert 'Country List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Measure(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[7]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[7]/ul/li[4]/a'
    assert 'Unit Of Measure' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Account(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[7]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[7]/ul/li[5]/a'
    assert 'Account List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_AccountType(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[7]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[7]/ul/li[6]/a'
    assert 'Account Type List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)

def test_Menu_Group(driver):
    login(driver)
    GroupMenu_xpath = '//*[@id="nav-accordion"]/li[7]/a/span[1]'
    Menu_xpath = '//*[@id="nav-accordion"]/li[7]/ul/li[7]/a'
    assert 'Group List' in GetMenuTitle(driver, GroupMenu_xpath, Menu_xpath)




