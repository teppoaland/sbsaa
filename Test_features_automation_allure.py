import time
import os
import sys
import pytest
import allure
from allure_commons.types import AttachmentType
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from appium.webdriver.common.appiumby import AppiumBy

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Set to False if need to have screenshots from all tested views - not working as expected. Keep False -value to get any image
SAVE_ONLY_FAILED_SCREENSHOTS = False

# Pytest fixture for setup and teardown
@pytest.fixture(scope="function")
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "Android_test_device"  
    options.app_package = "fi.sbweather.app"
    options.app_activity = "fi.sbweather.app.MainActivity"
    options.automation_name = "UiAutomator2"
    options.no_reset = True
    options.full_reset = False

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def app_setup(driver):
    """Setup and teardown for each test function"""
    driver.terminate_app("fi.sbweather.app")
    time.sleep(2)
    driver.activate_app("fi.sbweather.app")
    time.sleep(5)
    yield

def save_screenshot(driver, filename_prefix, failed=False):
    """
    Save screenshot based on settings.
    - Always save failed screenshots.
    - Save successful screenshots only if SAVE_ONLY_FAILED_SCREENSHOTS is False.
    """
    if failed or not SAVE_ONLY_FAILED_SCREENSHOTS:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"{filename_prefix}_{'failed' if failed else 'success'}",
            attachment_type=AttachmentType.PNG
        )

def check_element(driver, by, value, timeout=10):
    """Check if element exists and return True/False."""
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return True
    except TimeoutException:
        return False

# Selkeät, erilliset testifunktiot jokaiselle testitapaukselle
@allure.feature("Main View")
def test_home_tab(driver, app_setup):
    """Test that home tab is visible"""
    assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3", 10), "HOME button not found"
    save_screenshot(driver, "HOME_button_main", False)

@allure.feature("Search Functionality")
def test_oulu_search(driver, app_setup):
    """Test search functionality for Oulu"""
    driver.tap([(400, 780)])  
    time.sleep(3) 
    driver.execute_script('mobile: shell', {
        'command': 'input', 'args': ['text', 'Oulu'], 'includeStderr': True, 'timeout': 5000
    })
    save_screenshot(driver, "Oulu_weather_stations_list", False)

@allure.feature("Location Tests")
def test_oulu_vihreasaari(driver, app_setup):
    """Test Oulu Vihreäsaari location"""
    test_oulu_search(driver, app_setup)  # Kutsu hakutoiminnallisuus
    
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Oulu Vihreäsaari"))
    )
    element.click()
    time.sleep(10)
    
    assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "LÄMPÖTILA", 10), "Weather data not loaded for Vihreäsaari"
    save_screenshot(driver, "Weather_oulu_vihreasaari", False)

@allure.feature("Location Tests") 
def test_oulu_airport(driver, app_setup):
    """Test Oulu airport location"""
    test_oulu_search(driver, app_setup)  # Kutsu hakutoiminnallisuus
    
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Oulu lentoasema"))
    )
    element.click()
    time.sleep(10)
    
    assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "LÄMPÖTILA", 10), "Weather data not loaded for airport"
    save_screenshot(driver, "Weather_oulu_airport", False)

@allure.feature("Weather Views")
def test_warmest_view(driver, app_setup):
    """Test warmest weather view"""
    driver.tap([(300, 1150)])
    time.sleep(6)
    
    assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "Lämpimimmät", 10), "Warmest view not found"
    save_screenshot(driver, "Max_Temp", False)
    
    driver.back()
    time.sleep(3)

@allure.feature("Weather Views")
def test_coldest_view(driver, app_setup):
    """Test coldest weather view"""
    driver.tap([(790, 1150)])
    time.sleep(6)
    
    assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "Kylmimmät", 10), "Coldest view not found"
    save_screenshot(driver, "Low_Temp", False)
    
    driver.back()
    time.sleep(3)

@allure.feature("Weather Views")
def test_rainiest_view(driver, app_setup):
    """Test rainiest weather view"""
    driver.tap([(300, 1480)])
    time.sleep(6)
    
    assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "Sateisimmat", 10), "Rainiest view not found"
    save_screenshot(driver, "Most_Rain", False)
    
    driver.back()
    time.sleep(3)

@allure.feature("Weather Views")
def test_windiest_view(driver, app_setup):
    """Test windiest weather view"""
    driver.tap([(790, 1480)])
    time.sleep(6)
    
    assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "Tuulisimmat", 10), "Windiest view not found"
    save_screenshot(driver, "Most_Windy", False)
    
    driver.back()
    time.sleep(3)

@allure.feature("Records Tab")
def test_records_tab(driver, app_setup):
    """Test records tab functionality"""
    records_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "ENNÄTYKSET\nTab 2 of 3"))
    )
    records_tab.click()
    time.sleep(3)
    
    assert check_element(driver, AppiumBy.CLASS_NAME, "android.widget.ImageView", 10), "Records tab widget not found"
    save_screenshot(driver, "Records_widget", False)

@allure.feature("Final Verification")
def test_final_home_check(driver, app_setup):
    """Final verification that home tab is still visible"""
    assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3", 10), "Final HOME button check failed"
    save_screenshot(driver, "HOME_button_final", False)
    
    driver.terminate_app("fi.sbweather.app")