# File location:  sbsaa/Test_features_automation_allure.py

import time
import os
import sys
import pytest
import allure
import json
import subprocess
from allure_commons.types import AttachmentType
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from appium.webdriver.common.appiumby import AppiumBy
from azure_integration.azure_devops_client import azure_work_item

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Set to False if need to have screenshots from all tested views - not working as expected. Keep False -value to get any image
SAVE_ONLY_FAILED_SCREENSHOTS = False

# Global variable to store app version.
tested_app_version = "Unknown"

def get_app_version(package_name="fi.sbweather.app"):
    """Get app version using ADB"""
    try:
        # Get app version using ADB
        result = subprocess.run([
            'adb', 'shell', 'dumpsys', 'package', package_name, '|', 
            'grep', '-E', 'versionCode|versionName'
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            version_name = "Unknown"
            version_code = "Unknown"
            
            for line in lines:
                if 'versionName=' in line:
                    version_name = line.split('versionName=')[1].strip()
                elif 'versionCode=' in line:
                    version_code = line.split('versionCode=')[1].split()[0]
            
            return f"{version_name} (build {version_code})"
        else:
            # Alternative method - use pm command
            result = subprocess.run([
                'adb', 'shell', 'pm', 'dump', package_name, '|', 
                'grep', 'versionName'
            ], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0 and result.stdout:
                version_line = result.stdout.strip().split('\n')[0]
                if 'versionName=' in version_line:
                    return version_line.split('versionName=')[1].strip()
    
    except Exception as e:
        print(f"Error getting app version: {e}")
    
    return "Unknown"

def save_version_info(version):
    """Save version info to a local file for workflow to use"""
    version_data = {
        "tested_version": version,
        "test_timestamp": datetime.now().isoformat(),
        "app_package": "fi.sbweather.app"
    }
    
    with open("tested_app_version.json", "w") as f:
        json.dump(version_data, f, indent=2)
    
    print(f"[VERSION-INFO] Tested app version: {version}")

# Pytest fixture for setup and teardown
@pytest.fixture(scope="function")
def driver():
    global tested_app_version
    
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "Android_test_device"  
    options.app_package = "fi.sbweather.app"
    options.app_activity = "fi.sbweather.app.MainActivity"
    options.automation_name = "UiAutomator2"
    options.no_reset = True
    options.full_reset = False

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    
    # Get app version on first test run
    if tested_app_version == "Unknown":
        tested_app_version = get_app_version()
        save_version_info(tested_app_version)
        
        # Add version to Allure environment info
        allure.dynamic.parameter("App Version", tested_app_version)
    
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

# Test functions for each feature
@allure.feature("Main View")
def test_home_tab(driver, app_setup):
    """Test that home tab is visible"""
    assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3", 10), "HOME button not found"
    save_screenshot(driver, "HOME_button_main", False)

@azure_work_item(2)  # Replace with actual work item ID after setup
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
    test_oulu_search(driver, app_setup)
    
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
    test_oulu_search(driver, app_setup)
    
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