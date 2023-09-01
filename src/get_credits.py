from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import os

options = webdriver.FirefoxOptions() 
options.headless = True 
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
url = "https://platform.openai.com/account/billing/overview" 
driver.get(url)
username = os.getenv('OPENAI_USERNAME')
password = os.getenv('OPENAI_PASSWORD')
 
def regex_to_be_present_in_element(locator, regexp):
    """ An expectation for checking if the given text is present in the
    specified element, extended to allow and return a regex match
    locator, text
    """
    def _predicate(driver):
        try:
            element_text = driver.find_element(*locator).text
            return re.search(regexp, element_text)
        except Exception:
            return False
    return _predicate

def login():
    username_field=driver.find_element(By.ID, "username")
    username_field.send_keys(username)
    continueButton=driver.find_element(By.NAME, "action")
    continueButton.click()
    password_field=driver.find_element(By.ID, "password")
    password_field.send_keys(password)
    WebDriverWait(driver, 10)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(("xpath", "/html/body/div/main/section/div/div/div/form/div[3]/button"))).click()

def extract_remaining_credits():
    driver.refresh
    WebDriverWait(driver, 20).until(regex_to_be_present_in_element(("xpath", "/html/body/div[1]/div[1]/div/div[2]/div[2]/div/div[1]/div/div[1]/div[2]"), r"^\$.*"))
    credits=driver.find_element(By.CSS_SELECTOR, ".billing-credit-balance-value")
    return credits.text

def get_remaing_credits():
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(("xpath", "/html/body/div[1]/div[1]/div/div[2]/div/p/button[1]/span/span"))).click()
        login()
    except Exception:
        print("Already connected to openAI website.")
    return extract_remaining_credits()
