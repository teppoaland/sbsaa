# config.py
from appium import webdriver
from appium.options.android import UiAutomator2Options

def create_appium_driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "Android_test_device"  
    options.app_package = "fi.sbweather.app"
    options.app_activity = "fi.sbweather.app.MainActivity"
    options.automation_name = "UiAutomator2"
    options.no_reset = True
    options.full_reset = False
    
    return webdriver.Remote("http://127.0.0.1:4723", options=options)