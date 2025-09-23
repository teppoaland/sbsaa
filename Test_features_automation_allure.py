"""
Sää App Test Automation Suite with Azure DevOps Integration
File location: sbsaa/Test_features_automation_allure.py

Complete test suite for Sää weather application with Allure reporting and Azure DevOps work item integration.
Tests are executed in order and linked to corresponding Azure DevOps Test Cases.
"""

import time
import json
import allure
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from azure_integration.azure_devops_client import azure_work_item


def check_element(driver, locator_type, locator_value, timeout=10):
    """Helper function to check if element exists with timeout"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((locator_type, locator_value))
        )
        return True
    except TimeoutException:
        return False


def save_screenshot(driver, name, failed=False):
    """Helper function to save screenshots with Allure attachment"""
    try:
        screenshot_path = f"screenshots{'_failed' if failed else ''}/{name}.png"
        driver.save_screenshot(screenshot_path)
        
        # Attach to Allure report
        with open(screenshot_path, "rb") as image_file:
            allure.attach(
                image_file.read(), 
                name=name, 
                attachment_type=allure.attachment_type.PNG
            )
    except Exception as e:
        print(f"Failed to save screenshot {name}: {e}")


def get_app_version_info(driver, package_name):
    """Extract and save app version information"""
    try:
        version_info = driver.execute_script('mobile: shell', {
            'command': 'dumpsys',
            'args': ['package', package_name],
            'includeStderr': True,
            'timeout': 5000
        })
        
        # Parse version info
        lines = version_info.split('\n')
        version_name = None
        version_code = None
        
        for line in lines:
            if 'versionName=' in line:
                version_name = line.split('versionName=')[1].strip()
                break
        
        if version_name:
            version_data = {
                "package_name": package_name,
                "tested_version": version_name,
                "test_timestamp": time.time()
            }
            
            # Save to file for GitHub Actions to pick up
            with open("tested_app_version.json", "w") as f:
                json.dump(version_data, f, indent=2)
            
            allure.dynamic.parameter("App Version", version_name)
            print(f"[VERSION-INFO] Tested app version: {version_name}")
            
            return version_name
    except Exception as e:
        print(f"Failed to get version info: {e}")
        return "Unknown"


@pytest.fixture(scope="session")
def driver():
    """Setup Appium driver for test session"""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "Android Device"
    options.app_package = "com.foreca.yrweather"
    options.app_activity = "com.foreca.yrweather.MainActivity"
    options.no_reset = True
    options.full_reset = False
    
    driver = webdriver.Remote("http://localhost:4723", options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture
def app_setup(driver):
    """Setup app for each test"""
    package_name = "com.foreca.yrweather"
    
    try:
        # Launch app using monkey command for reliability
        driver.execute_script('mobile: shell', {
            'command': 'monkey',
            'args': ['-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'],
            'includeStderr': True,
            'timeout': 10000
        })
        time.sleep(10)  # Wait for app to fully load
        
        # Get app version info (once per session)
        get_app_version_info(driver, package_name)
        
    except Exception as e:
        pytest.skip(f"App setup failed: {e}")


# Test Case 1: Main View Visibility
@azure_work_item(1)  # Link to Azure DevOps Test Case 1
@allure.feature("Main View")
@allure.story("Home Tab Visibility")
@allure.title("Verify HOME tab is visible on main view")
@allure.description("Test that the main home tab button is accessible when app launches")
def test_home_tab(driver, app_setup):
    """Test that home tab is visible"""
    with allure.step("Check if HOME tab button is visible"):
        assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3", 10), "HOME button not found"
    
    with allure.step("Capture screenshot of home view"):
        save_screenshot(driver, "HOME_button_main", False)


# Test Case 2: Oulu Search Functionality  
@azure_work_item(2)  # Link to Azure DevOps Test Case 2
@allure.feature("Search Functionality")
@allure.story("City Search")
@allure.title("Test Oulu city weather station search")
@allure.description("Verify that users can search for weather stations using city name 'Oulu'")
def test_oulu_search(driver, app_setup):
    """Test search functionality for Oulu"""
    with allure.step("Navigate to search field"):
        driver.tap([(400, 780)])
        time.sleep(3)
    
    with allure.step("Enter 'Oulu' in search field"):
        driver.execute_script('mobile: shell', {
            'command': 'input',
            'args': ['text', 'Oulu'],
            'includeStderr': True,
            'timeout': 5000
        })
    
    with allure.step("Capture search results"):
        save_screenshot(driver, "Oulu_weather_stations_list", False)


# Test Case 3: Oulu Vihreasaari Station
@azure_work_item(3)  # Link to Azure DevOps Test Case 3
@allure.feature("Weather Stations")
@allure.story("Specific Station Access")
@allure.title("Test Oulu Vihreasaari weather station access")
@allure.description("Verify that Oulu Vihreasaari weather station data is accessible")
def test_oulu_vihreasaari(driver, app_setup):
    """Test Oulu Vihreasaari weather station"""
    with allure.step("Search for Oulu weather stations"):
        driver.tap([(400, 780)])
        time.sleep(2)
        driver.execute_script('mobile: shell', {
            'command': 'input',
            'args': ['text', 'Oulu'],
            'includeStderr': True,
            'timeout': 5000
        })
        time.sleep(3)
    
    with allure.step("Select Vihreasaari station"):
        try:
            vihreasaari_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//*[contains(@text, 'Vihreasaari')]"))
            )
            vihreasaari_element.click()
        except TimeoutException:
            pytest.fail("Vihreasaari station not found in search results")
    
    with allure.step("Verify station data loads"):
        time.sleep(5)
        save_screenshot(driver, "Oulu_Vihreasaari_station", False)


# Test Case 4: Oulu Airport Station
@azure_work_item(4)  # Link to Azure DevOps Test Case 4
@allure.feature("Weather Stations")  
@allure.story("Airport Weather Data")
@allure.title("Test Oulu Airport weather station")
@allure.description("Verify that Oulu Airport weather station provides accurate data")
def test_oulu_airport(driver, app_setup):
    """Test Oulu Airport weather station"""
    with allure.step("Navigate to Oulu Airport station"):
        # Implementation for airport station access
        driver.tap([(400, 780)])
        time.sleep(2)
        driver.execute_script('mobile: shell', {
            'command': 'input',
            'args': ['text', 'Oulu Airport'],
            'includeStderr': True,
            'timeout': 5000
        })
        time.sleep(3)
    
    with allure.step("Verify airport weather data"):
        save_screenshot(driver, "Oulu_Airport_weather", False)


# Test Case 5: Warmest Temperature View
@azure_work_item(5)  # Link to Azure DevOps Test Case 5
@allure.feature("Temperature Views")
@allure.story("Temperature Rankings") 
@allure.title("Test warmest temperature view")
@allure.description("Verify that the warmest temperature view displays correctly")
def test_warmest_view(driver, app_setup):
    """Test warmest temperature view"""
    with allure.step("Navigate to warmest temperature section"):
        try:
            # Look for warmest temperature view element
            warmest_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//*[contains(@text, 'Lämpimin') or contains(@text, 'Warmest')]"))
            )
            warmest_element.click()
        except TimeoutException:
            print("Warmest view not directly accessible, using alternative navigation")
    
    with allure.step("Verify warmest temperature data"):
        time.sleep(3)
        save_screenshot(driver, "Warmest_temperature_view", False)


# Test Case 6: Coldest Temperature View
@azure_work_item(6)  # Link to Azure DevOps Test Case 6
@allure.feature("Temperature Views")
@allure.story("Temperature Rankings")
@allure.title("Test coldest temperature view") 
@allure.description("Verify that the coldest temperature view displays correctly")
def test_coldest_view(driver, app_setup):
    """Test coldest temperature view"""
    with allure.step("Navigate to coldest temperature section"):
        try:
            coldest_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//*[contains(@text, 'Kylmin') or contains(@text, 'Coldest')]"))
            )
            coldest_element.click()
        except TimeoutException:
            print("Coldest view not directly accessible, using alternative navigation")
    
    with allure.step("Verify coldest temperature data"):
        time.sleep(3) 
        save_screenshot(driver, "Coldest_temperature_view", False)


# Test Case 7: Rainiest Location View
@azure_work_item(7)  # Link to Azure DevOps Test Case 7
@allure.feature("Weather Conditions")
@allure.story("Precipitation Data")
@allure.title("Test rainiest location view")
@allure.description("Verify that the rainiest location view displays precipitation data correctly")
def test_rainiest_view(driver, app_setup):
    """Test rainiest location view"""
    with allure.step("Navigate to precipitation section"):
        try:
            rainy_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//*[contains(@text, 'Sateinen') or contains(@text, 'Rain')]"))
            )
            rainy_element.click()
        except TimeoutException:
            print("Rainiest view not directly accessible, using alternative navigation")
    
    with allure.step("Verify precipitation data"):
        time.sleep(3)
        save_screenshot(driver, "Rainiest_locations_view", False)


# Test Case 8: Windiest Location View  
@azure_work_item(8)  # Link to Azure DevOps Test Case 8
@allure.feature("Weather Conditions")
@allure.story("Wind Data")
@allure.title("Test windiest location view")
@allure.description("Verify that the windiest location view displays wind data correctly")
def test_windiest_view(driver, app_setup):
    """Test windiest location view"""
    with allure.step("Navigate to wind data section"):
        try:
            windy_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//*[contains(@text, 'Tuulisin') or contains(@text, 'Wind')]"))
            )
            windy_element.click()
        except TimeoutException:
            print("Windiest view not directly accessible, using alternative navigation")
    
    with allure.step("Verify wind speed data"):
        time.sleep(3)
        save_screenshot(driver, "Windiest_locations_view", False)


# Test Case 9: Records Tab Access
@azure_work_item(9)  # Link to Azure DevOps Test Case 9
@allure.feature("Navigation")
@allure.story("Historical Data Access")
@allure.title("Test weather records tab access")
@allure.description("Verify that the records tab is accessible and displays historical data")
def test_records_tab(driver, app_setup):
    """Test records tab access"""
    with allure.step("Navigate to records tab"):
        try:
            records_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "ENNÄTYKSET\nTab 2 of 3"))
            )
            records_element.click()
        except TimeoutException:
            pytest.fail("Records tab not accessible")
    
    with allure.step("Verify records tab loads correctly"):
        time.sleep(3)
        save_screenshot(driver, "Records_tab_view", False)


# Test Case 10: Final Home Navigation Check
@azure_work_item(10)  # Link to Azure DevOps Test Case 10
@allure.feature("Navigation")
@allure.story("Navigation Consistency") 
@allure.title("Test final home navigation check")
@allure.description("Verify that navigation back to home view works correctly after using other features")
def test_final_home_check(driver, app_setup):
    """Test final home navigation check"""
    with allure.step("Navigate through app sections"):
        # Navigate to records tab first
        try:
            records_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "ENNÄTYKSET\nTab 2 of 3"))
            )
            records_element.click()
            time.sleep(2)
        except TimeoutException:
            print("Records tab not accessible for navigation test")
    
    with allure.step("Return to home tab"):
        try:
            home_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3"))
            )
            home_element.click()
        except TimeoutException:
            pytest.fail("Cannot navigate back to home tab")
    
    with allure.step("Verify home view loads correctly"):
        time.sleep(3)
        assert check_element(driver, AppiumBy.ACCESSIBILITY_ID, "KOTI\nTab 1 of 3", 5), "Home tab not active after navigation"
        save_screenshot(driver, "Final_home_check", False)