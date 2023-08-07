import json
import os
from typing import Optional
from datetime import datetime

from appium.webdriver import WebElement
from appium.webdriver.appium_service import AppiumService
from appium.webdriver.common.appiumby import AppiumBy
from appium import webdriver

import time

from appium.webdriver.common.touch_action import TouchAction
from selenium.common import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app_testing.config import device_name
from app_testing.date_helper import DateHelper

DATES = [
    ('2023-09-01', '2023-09-02'), ('2023-09-03', '2023-09-04'),
    ('2023-09-10', '2023-09-11'), ('2023-09-04', '2023-09-05'),
    ('2023-09-28', '2023-09-29')
]


class TripAdvisorTest:
    def __init__(self, input_dates: list[tuple[str, str]], hotel_name: str):
        self.appium_service = None
        self.driver = None
        self.input_dates = input_dates
        self.hotel_name = hotel_name
        self.dates_to_search = []
        self.format_dates()

    def start_appium_service(self):
        self.appium_service = AppiumService()
        self.appium_service.start(timeout_ms=100)

    def start_driver(self):
        desired_caps = {
            "platformName": "Android",
            "platformVersion": "12",
            "deviceName": device_name,
            "appPackage": "com.tripadvisor.tripadvisor",
            "appActivity": "com.tripadvisor.android.ui.launcher.LauncherActivity",
            'automationName': 'UiAutomator2',
            "noReload": True
        }
        try:
            appium_server_url = "http://localhost:4723"
            self.driver = webdriver.Remote(appium_server_url, desired_caps)
            time.sleep(5)
        except Exception as e:
            if self.driver is not None:
                self.driver.quit()
            return e
        return self.driver

    def set_up_web_driver_wait(self):
        return WebDriverWait(self.driver, 30)

    def open_tripadvisor(self):
        wait = self.set_up_web_driver_wait()
        try:
            self.driver.get("https://www.tripadvisor.com/")
        except Exception as e:
            print(e)
        time.sleep(10)
        try:
            privacy_notice = wait.until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.tripadvisor.tripadvisor:id/btn_accept_cookies"))
            )
            privacy_notice.click()
        except NoSuchElementException:
            pass

    def search_hotel(self):
        wait = self.set_up_web_driver_wait()
        hotel_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.Button[@content-desc='Hotels']"))
        )
        hotel_button.click()
        searching_line = wait.until(
            EC.visibility_of_element_located((AppiumBy.ID, "com.tripadvisor.tripadvisor:id/edtSearchString"))
        )
        searching_line.send_keys(self.hotel_name)

        hotel_name_elements = wait.until(EC.presence_of_all_elements_located(
            (AppiumBy.XPATH, f"//android.widget.TextView[@text='{self.hotel_name}']")
        ))
        hotel_name_elements[1].click()

    def click_get_dates_button(self):
        wait = self.set_up_web_driver_wait()
        get_dates_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.tripadvisor.tripadvisor:id/txtDate"))
        )
        get_dates_button.click()

    def scroll_up(self):
        action = TouchAction(self.driver)
        action.press(x=500, y=1988).move_to(x=500, y=1266).release().perform()

    def scroll_down(self):
        action = TouchAction(self.driver)
        action.press(x=300, y=1250).move_to(x=300, y=2000).release().perform()

    def __find_element_or_none(
            self, by, value, parent_element: Optional[WebElement] = None) -> Optional[WebElement]:
        if parent_element:
            try:
                element = parent_element.find_element(by, value)
                time.sleep(5)
                return element
            except NoSuchElementException:
                return None
        try:
            element = self.driver.find_element(by, value)
            time.sleep(5)
            return element
        except NoSuchElementException:
            return None

    def __find_elements_or_none(
            self, by, value, parent_element: Optional[WebElement] = None) -> Optional[list[WebElement]]:
        if parent_element:
            try:
                return parent_element.find_elements(by, value)
            except NoSuchElementException:
                return None
        try:
            return self.driver.find_elements(by, value)
        except NoSuchElementException:
            return None

    def find_month_container_by_date(self, date_text):
        container_id = 1
        current_month_year = DateHelper.get_current_month_and_year()
        while True:
            current_month_container = self.__find_element_or_none(
                AppiumBy.XPATH,
                f"(//android.view.ViewGroup[@resource-id='com.tripadvisor.tripadvisor:id/monthView'])[{container_id}]"
            )
            if current_month_container is None:
                self.scroll_down()
                continue
            try:
                date_element = current_month_container.find_element(
                    AppiumBy.XPATH, f".//android.widget.TextView[@text='{current_month_year}']"
                )
                break
            except NoSuchElementException:
                self.scroll_down()
                time.sleep(4)

        while True:
            month_container = self.__find_element_or_none(
                AppiumBy.XPATH,
                f"(//android.view.ViewGroup[@resource-id='com.tripadvisor.tripadvisor:id/monthView'])[{container_id}]"
            )
            if month_container is None:
                self.scroll_up()
                time.sleep(2)
                container_id += 1

            try:
                date_element = month_container.find_element(
                    AppiumBy.XPATH, f".//android.widget.TextView[@text='{date_text}']"
                )
                return month_container
            except NoSuchElementException:
                self.scroll_up()
                time.sleep(2)
                container_id += 1

    def click_date(self, date_text, integer_text):
        while True:
            month_container = self.find_month_container_by_date(date_text)

            integer_element = self.__find_element_or_none(
                AppiumBy.XPATH,
                f".//android.widget.TextView[@text='{integer_text}']",
                parent_element=month_container
            )

            if integer_element:
                integer_element.click()
                return
            else:
                self.scroll_up()

    def __check_input_dates(self, dates: list[tuple[str, str]]):
        if len(dates) != 2:
            self.driver.quit()
            self.appium_service.stop()
            return None
        return True

    def click_dates(self, dates: list[tuple[str, str]]):
        if self.__check_input_dates(dates) is None:
            return self.__check_input_dates(dates)
        arrival_month_and_year, arrival_day = dates[0]
        departure_month_and_year, departure_day = dates[1]

        self.click_date(arrival_month_and_year, arrival_day)
        time.sleep(3)
        self.click_date(departure_month_and_year, departure_day)
        time.sleep(3)

    def click_apply(self):
        apply_button = self.driver.find_element(AppiumBy.ID, "com.tripadvisor.tripadvisor:id/btnPrimary")
        apply_button.click()

    def click_view_all_deals(self):
        while True:
            try:
                time.sleep(10)
                self.driver.find_element(AppiumBy.ID, "com.tripadvisor.tripadvisor:id/btnAllDeals").click()
                time.sleep(5)
                break
            except NoSuchElementException:
                self.driver.find_element(AppiumBy.ID, "com.tripadvisor.tripadvisor:id/btnReload").click()

    def get_prices_by_providers(self) -> dict[str, int | str]:
        prices_by_provides = {}
        providers = self.driver.find_elements(
            AppiumBy.XPATH, "//android.widget.TextView[@resource-id='com.tripadvisor.tripadvisor:id/txtProviderName']"
        )
        prices = self.driver.find_elements(
            AppiumBy.XPATH, "//android.widget.TextView[@resource-id='com.tripadvisor.tripadvisor:id/txtPriceTopDeal']"
        )
        top_deal_provider = self.driver.find_element(
            AppiumBy.ID, "com.tripadvisor.tripadvisor:id/imgProviderLogo"
        )

        top_deal_price_xpath = \
            "(//androidx.recyclerview.widget.RecyclerView/androidx.cardview.widget.CardView)[1]//android.widget.TextView[contains(@resource-id, 'txtPriceTopDeal')]"

        top_deal_price = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((AppiumBy.XPATH, top_deal_price_xpath))
        )

        prices_by_provides[top_deal_provider.get_attribute("content-desc")] = int(top_deal_price.text.replace("$", ""))

        for provider, price in zip(providers, prices):
            provider_name = provider.text
            price = price.text
            prices_by_provides[provider_name] = int(price.replace("$", ""))
        return prices_by_provides

    def return_to_main_hotel_page(self):
        self.driver.find_element(AppiumBy.ID, "com.tripadvisor.tripadvisor:id/imgCircularBtnIcon").click()
        time.sleep(2)

    def format_dates(self) -> list[list[tuple[str, str]]]:
        for start_date, end_date in self.input_dates:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

            month = start_date_obj.strftime("%B %Y")

            start_day = start_date_obj.strftime("%d").lstrip("0")
            end_day = end_date_obj.strftime("%d").lstrip("0")

            self.dates_to_search.append([(month, start_day), (month, end_day)])

        return self.dates_to_search

    def save_screenshot(self, dates: str):
        screenshots_directory = "C:\\Users\\aooli\\PycharmProjects\\TestTaskAndroid\\app_testing\\screenshots"

        activity_name = self.driver.current_activity
        filename = activity_name + dates + ".png"

        if not os.path.exists(screenshots_directory):
            os.makedirs(screenshots_directory)

        screenshot_path = os.path.join(screenshots_directory, filename)
        self.driver.get_screenshot_as_file(screenshot_path)

    def save_to_json(self, data):
        with open("prices.json", "w") as json_file:
            json.dump({self.hotel_name: data}, json_file, indent=2)

    def run_test(self):
        prices_data = {}
        self.start_appium_service()
        self.start_driver()
        self.open_tripadvisor()
        self.search_hotel()

        hotel_data = {}
        for date in self.dates_to_search:
            self.click_get_dates_button()
            self.click_dates(date)
            self.click_apply()
            self.click_view_all_deals()
            output_dates = DateHelper.get_output_dates(date)
            screenshot_name = f"screenshot_{output_dates}.png"
            self.save_screenshot(screenshot_name)
            prices_by_provider = self.get_prices_by_providers()
            prices_by_provider["screenshot"] = screenshot_name
            hotel_data[output_dates] = prices_by_provider

            self.return_to_main_hotel_page()

        prices_data["hotel_name"] = hotel_data

        self.save_to_json(prices_data)
        self.driver.quit()
        self.appium_service.stop()


def test_run():
    test_scenario = TripAdvisorTest(hotel_name="The Grosvenor Hotel", input_dates=DATES)
    test_scenario.run_test()


