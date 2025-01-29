from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from foodbook_app.models import User
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FoodbookLiveTest(LiveServerTestCase):
    def setUp(self):
        # Set up the Selenium WebDriver
        self.browser = webdriver.Chrome()  # Or whichever browser driver you're using
        User.objects.create_user(username="testuser", password="password123")

    def tearDown(self):
        self.browser.quit()

    def test_login_request_flow(self):
        # Open the login page
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        
        # Use WebDriverWait to locate elements by id as observed in the screenshot
        username_input = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "id_username"))
        )
        username_input.send_keys("testuser")
        
        password_input = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "id_password"))
        )
        password_input.send_keys("password123")

        # Click the login button
        login_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "login-button"))
        )
        login_button.click()

        # Assert successful login
        WebDriverWait(self.browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Logout")
        )