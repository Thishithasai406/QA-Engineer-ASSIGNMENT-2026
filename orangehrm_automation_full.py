from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# ── Page Object Model ──

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
        self.username_field = (By.NAME, "username")
        self.password_field = (By.NAME, "password")
        self.login_button = (By.XPATH, "//button[@type='submit']")

    def open(self):
        self.driver.get(self.url)

    def login(self, username, password):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located(
            self.username_field)).send_keys(username)
        self.driver.find_element(*self.password_field).send_keys(password)
        self.driver.find_element(*self.login_button).click()
        print("Step 1: Login successful")


class PIMPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def wait_for_loader_to_disappear(self):
        try:
            self.wait.until(EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".oxd-form-loader")))
        except Exception:
            pass

    def navigate_to_pim(self):
        pim = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//span[text()='PIM']")))
        ActionChains(self.driver).move_to_element(pim).click().perform()
        time.sleep(2)
        print("Step 2: Navigated to PIM module")

    def add_employee(self, first, last):
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[text()='Add Employee']"))).click()
        self.wait_for_loader_to_disappear()
        time.sleep(1)

        first_field = self.wait.until(EC.presence_of_element_located(
            (By.NAME, "firstName")))
        first_field.clear()
        first_field.send_keys(first)

        last_field = self.driver.find_element(By.NAME, "lastName")
        last_field.clear()
        last_field.send_keys(last)

        submit_button = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")))
        self.wait_for_loader_to_disappear()
        submit_button.click()
        time.sleep(3)
        print(f"Step 3: Added employee — {first} {last}")

    def go_to_employee_list(self):
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[text()='Employee List']"))).click()
        time.sleep(3)
        print("Step 4: Navigated to Employee List")

    def verify_employees(self, names):
        for name in names:
            try:
                self.driver.get(
                    "https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList"
                )
                self.wait_for_loader_to_disappear()

                name_input = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//label[normalize-space()='Employee Name']/ancestor::div[contains(@class,'oxd-input-group')]//input")))
                name_input.clear()
                name_input.send_keys(name)
                time.sleep(1.5)

                options = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class,'oxd-autocomplete-option')] | //div[contains(@class,'oxd-autocomplete-dropdown')]//span"
                )
                found_in_autocomplete = any(name.lower() in option.text.lower() for option in options)

                if found_in_autocomplete:
                    print(f"Name Verified: {name}")
                    continue

                search_button = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[normalize-space()='Search']")))
                search_button.click()
                self.wait_for_loader_to_disappear()
                time.sleep(2)

                rows = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class,'oxd-table-card')] | //div[contains(@class,'oxd-table-row')]"
                )
                found_in_table = any(name.lower() in row.text.lower() for row in rows)

                if found_in_table:
                    print(f"Name Verified: {name}")
                else:
                    print(f"Name NOT found: {name}")

            except Exception as e:
                print(f"Name check ERROR for {name}: {type(e).__name__} - {e}")


class DashboardPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def logout(self):
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//li[@class='oxd-userdropdown']"))).click()
        time.sleep(1)
        self.driver.find_element(
            By.XPATH, "//a[text()='Logout']").click()
        print("Step 5: Logged out successfully")


# ── Main Test Runner ──

def main():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    employees = [
        ("Thishitha", "Sai"),
        ("bellamkonda", "T"),
        ("sri", "lakshmi"),
    ]

    try:
        # Step 1: Login
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("Admin", "admin123")
        time.sleep(3)

        # Step 2: Navigate to PIM
        pim = PIMPage(driver)
        pim.navigate_to_pim()

        # Step 3: Add Employees
        for first, last in employees:
            pim.navigate_to_pim()
            pim.add_employee(first, last)

        # Step 4: Verify Employees
        names = [f"{f} {l}" for f, l in employees]
        pim.verify_employees(names)

        # Step 5: Logout
        dashboard = DashboardPage(driver)
        dashboard.logout()

    finally:
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    main()
