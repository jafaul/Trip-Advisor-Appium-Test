import json
import os
from typing import Optional

from appium.webdriver import WebElement
from appium.webdriver.appium_service import AppiumService
from appium.webdriver.common.appiumby import AppiumBy
from appium import webdriver

import time

from appium.webdriver.common.touch_action import TouchAction
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app_testing.config import device_name
from app_testing.date_helper import DateHelper

DATES = [
    ('2023-09-27', '2023-09-28'), ('2023-09-01', '2023-09-02'), ('2023-09-03', '2023-09-04'),
    ('2023-09-10', '2023-09-11'), ('2023-09-04', '2023-09-05'),
]


class TripAdvisorTest:
    def __init__(self, input_dates: list[tuple[str, str]], hotel_name: str):
        self.appium_service = None
        self.driver = None
        self.input_dates = input_dates
        self.hotel_name = hotel_name
        self.dates_to_search = DateHelper.format_dates(input_dates=self.input_dates)

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
            "automationName": "UiAutomator2"
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

    def open_tripadvisor(self):
        wait = WebDriverWait(self.driver, 30)
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
        wait = WebDriverWait(self.driver, 5)
        try:
            ok_button = wait.until(
                EC.element_to_be_clickable((AppiumBy.ID, "android:id/button1"))
            )
            ok_button.click()
        except TimeoutException:
            pass

        wait = WebDriverWait(self.driver, 30)
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
        try:
            hotel_name_elements[1].click()
        except IndexError:
            hotel_name_elements[0].click()

    def click_get_dates_button(self):
        wait = WebDriverWait(self.driver, 30)
        get_dates_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.tripadvisor.tripadvisor:id/txtDate"))
        )
        get_dates_button.click()
        time.sleep(2)

    def scroll_calendar_up(self):
        action = TouchAction(self.driver)
        action.press(x=500, y=1988).move_to(x=500, y=1266).release().perform()

    def scroll_calendar_down(self):
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

    @staticmethod
    def __find_date_element(month_container: WebElement, month_year: str) -> WebElement:
        date_element = month_container.find_element(
            AppiumBy.XPATH, f".//android.widget.TextView[@text='{month_year}']"
        )
        return date_element

    def __find_month_container(self, container_id: int) -> Optional[WebElement]:
        month_container = self.__find_element_or_none(
            AppiumBy.XPATH,
            f"(//android.view.ViewGroup[@resource-id='com.tripadvisor.tripadvisor:id/monthView'])[{container_id}]"
        )
        return month_container

    def __find_current_month_container(self, container_id) -> None:
        current_month_year = DateHelper.get_current_month_and_year()
        while True:
            current_month_container = self.__find_month_container(container_id=container_id)
            if current_month_container is None:
                print("Scrolled down -- current month container is not found")
                self.scroll_calendar_down()
                continue
            try:
                self.__find_date_element(month_container=current_month_container, month_year=current_month_year)
                break
            except NoSuchElementException:
                print("Scrolled down -- current date element is not found in month container")
                self.scroll_calendar_down()
                time.sleep(1)

    def find_month_container_by_date(self, month_year) -> WebElement:
        container_id = 1
        self.__find_current_month_container(container_id=container_id)

        while True:
            month_container = self.__find_month_container(container_id=container_id)
            if month_container is None:
                print("Scrolled up -- month container is not found")
                self.scroll_calendar_up()
                time.sleep(1)
                container_id += 1
            try:
                self.__find_date_element(month_container=month_container, month_year=month_year)
                return month_container
            except NoSuchElementException:
                print("Scrolled up -- date element is not found in month container")
                self.scroll_calendar_up()
                time.sleep(1)
                container_id += 1

    def click_date(self, date_text, integer_text) -> None:
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
                print("scrolled up - integer_element is not found")
                self.scroll_calendar_up()

    def __check_input_dates(self, dates: list[tuple[str, str]]) -> Optional[bool]:
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
        time.sleep(1)
        self.click_date(departure_month_and_year, departure_day)
        time.sleep(1)

    def click_apply(self):
        apply_button = self.driver.find_element(AppiumBy.ID, "com.tripadvisor.tripadvisor:id/btnPrimary")
        apply_button.click()

    def click_view_all_deals(self):
        while True:
            try:
                view_all_deals_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((AppiumBy.ID, "com.tripadvisor.tripadvisor:id/btnAllDeals"))
                )
                view_all_deals_button.click()
                time.sleep(6)
                break
            except TimeoutException:
                try:
                    reload_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((AppiumBy.ID, "com.tripadvisor.tripadvisor:id/btnReload"))
                    )
                    reload_button.click()
                except TimeoutException:
                    actions = ActionChains(self.driver)
                    actions.w3c_actions = ActionBuilder(
                        self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch")
                    )
                    actions.w3c_actions.pointer_action.move_to_location(588, 1817)
                    actions.w3c_actions.pointer_action.pointer_down()
                    actions.w3c_actions.pointer_action.move_to_location(588, 1389)
                    actions.w3c_actions.pointer_action.release()
                    actions.perform()

    def __scroll_deals_page_up(self):
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(374, 1800)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(414, 800)
        actions.w3c_actions.pointer_action.release()
        actions.perform()
        time.sleep(3)

    def __get_top_deal(self) -> tuple[str, int]:
        top_deal_provider = self.driver.find_element(
            AppiumBy.ID, "com.tripadvisor.tripadvisor:id/imgProviderLogo"
        )
        top_deal_price_xpath = \
            "(//androidx.recyclerview.widget.RecyclerView/androidx.cardview.widget.CardView)[1]//android.widget.TextView[contains(@resource-id, 'txtPriceTopDeal')]"
        top_deal_price = self.driver.find_element(AppiumBy.XPATH, top_deal_price_xpath)
        return top_deal_provider.get_attribute("content-desc"), int(top_deal_price.text.replace("$", ""))

    def __get_providers_and_prices(self) -> tuple[list[WebElement], list[WebElement]]:
        providers = self.driver.find_elements(
            AppiumBy.XPATH, "//android.widget.TextView[@resource-id='com.tripadvisor.tripadvisor:id/txtProviderName']"
        )
        prices_xpath = "//android.widget.TextView[@resource-id='com.tripadvisor.tripadvisor:id/txtPriceTopDeal']"
        prices = self.driver.find_elements(AppiumBy.XPATH, prices_xpath)
        return providers, prices

    def __check_deals_page_if_is_finished(self) -> Optional[bool]:
        try:
            self.driver.find_element(AppiumBy.ID, "com.tripadvisor.tripadvisor:id/txtContent")
            return True
        except NoSuchElementException:
            return None

    def get_prices_by_providers(self) -> dict[str, str | int]:
        top_deal_provider, top_deal_price = self.__get_top_deal()
        prices_by_providers = {top_deal_provider: top_deal_price}
        providers_from_single_page, prices_from_single_page = self.__get_providers_and_prices()
        prices_from_single_page = prices_from_single_page[1:]
        prices = []
        while True:
            for provider, price in zip(providers_from_single_page, prices_from_single_page):
                price: WebElement
                if price not in prices:
                    prices_by_providers[provider.text] = int(price.text.replace("$", ""))
                    prices.append(price)
            if self.__check_deals_page_if_is_finished():
                return prices_by_providers
            else:
                self.__scroll_deals_page_up()
                providers_from_single_page, prices_from_single_page = self.__get_providers_and_prices()
                if len(providers_from_single_page) > len(prices_from_single_page):
                    delta = len(providers_from_single_page) - len(prices_from_single_page)
                    providers_from_single_page = providers_from_single_page[:-delta]

    def return_to_main_hotel_page(self):
        self.driver.find_element(AppiumBy.ID, "com.tripadvisor.tripadvisor:id/imgCircularBtnIcon").click()
        time.sleep(2)

    def __create_screenshot_name(self, dates: str) -> str:
        activity_name = self.driver.current_activity
        return activity_name + dates + ".png"

    def save_screenshot(self, dates: str):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        screenshots_directory = os.path.join(script_directory, "screenshots")

        filename = self.__create_screenshot_name(dates)

        if not os.path.exists(screenshots_directory):
            os.makedirs(screenshots_directory)

        screenshot_path = os.path.join(screenshots_directory, filename)
        self.driver.get_screenshot_as_file(screenshot_path)

    def save_to_json(self, data):
        with open("prices.json", "w") as json_file:
            json.dump({self.hotel_name: data}, json_file, indent=2)

    def run_test(self):
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
            screenshot_name = self.__create_screenshot_name(output_dates)
            self.save_screenshot(screenshot_name)
            prices_by_provider = self.get_prices_by_providers()
            prices_by_provider["screenshot"] = screenshot_name
            hotel_data[output_dates] = prices_by_provider

            self.return_to_main_hotel_page()

        self.save_to_json(hotel_data)
        self.driver.quit()
        self.appium_service.stop()


def test_run():
    test_scenario = TripAdvisorTest(hotel_name="The Grosvenor Hotel", input_dates=DATES)
    test_scenario.run_test()
