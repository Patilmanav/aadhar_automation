from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
import time
import sys
import shutil
import requests
from selenium.webdriver.firefox.service import Service as FirefoxService


class AadharValidator:
    def __init__(self, headless=True):
        if not self._check_internet():
            raise Exception("[🚫] No internet connection inside container.")

        self.options = Options()
        if headless:
            self.options.add_argument("--headless")

        # Specify geckodriver path manually
        geckodriver_path = shutil.which("geckodriver")
        if not geckodriver_path:
            raise FileNotFoundError("Geckodriver not found in PATH!")

        service = FirefoxService(executable_path=geckodriver_path)
        self.driver = webdriver.Firefox(service=service, options=self.options)
        self.wait = WebDriverWait(self.driver, 15)

        print("[🌐] Navigating to UIDAI site...")
        self.driver.get("https://myaadhaar.uidai.gov.in/check-aadhaar-validity")

    def _check_internet(self, url="https://myaadhaar.uidai.gov.in"):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 301, 302]:
                print(f"[✅] Internet check passed: {response.status_code}")
                return True
            else:
                print(f"[⚠️] Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"[🚫] Internet check failed: {e}")
            return False


    def wait_and_find(self, by, identifier):
        return self.wait.until(EC.presence_of_element_located((by, identifier)))

    def wait_and_find_all(self, by, identifier):
        return self.wait.until(EC.presence_of_all_elements_located((by, identifier)))

    def save_captcha(self, path="captcha.png"):
        try:
            print("[INFO] Saving captcha image...")
            captcha_element = self.wait_and_find(By.CLASS_NAME, 'auth-form__captcha-box')
            time.sleep(1)
            captcha_element.screenshot(path)
            print(f"[INFO] CAPTCHA saved at '{path}'.")
        except Exception as e:
            print(f"[ERROR] CAPTCHA saving failed: {e}")
            raise

    def get_captcha_solution(self):
        return input("Enter CAPTCHA from image: ")

    def get_aadhar_number(self):
        return input("Enter Aadhar number: ")

    def submit_form(self, aadhar_number, captcha_text):
        try:
            print("[INFO] Filling form...")
            self.wait_and_find(By.NAME, 'uid').send_keys(aadhar_number)
            self.wait_and_find(By.NAME, 'captcha').send_keys(captcha_text)

            self.driver.execute_script("window.focus();")
            ActionChains(self.driver).move_by_offset(0, 0).click().perform()

            submit_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'button_btn__HeAxz')]")))
            self.driver.execute_script("arguments[0].click();", submit_btn)
            print("[INFO] Submit clicked.")
        except Exception as e:
            print(f"[ERROR] Form submission failed: {e}")
            raise

    def check_for_errors(self):
        try:
            toast = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='Toastify__toast-body' and @role='alert']")))
            if toast and 'captcha' in toast.text.lower():
                return "Invalid Captcha"
        except:
            pass

        try:
            error_spans = self.driver.find_elements(By.CSS_SELECTOR, 'span.sc-hCPjZK.ckTsJH')
            for span in error_spans:
                if "Please enter valid Aadhaar number" in span.text:
                    return "Invalid Aadhar"
        except:
            pass

        return None

    def extract_verification_result(self):
        print("[INFO] Extracting verification result...")
        result = {}
        try:
            divs = self.wait_and_find_all(By.CLASS_NAME, 'verify-display-field')
            for div in divs:
                spans = div.find_elements(By.TAG_NAME, 'span')
                if len(spans) >= 2:
                    result[spans[0].text.strip()] = spans[1].text.strip()
        except Exception as e:
            print(f"[ERROR] Failed to extract result: {e}")
        return result

    def validate_aadhar(self, aadhar_number, captcha_text, max_retries=2):
        attempt = 0
        while attempt <= max_retries:
            try:
                self.submit_form(aadhar_number, captcha_text)
                error = self.check_for_errors()
                if error == "Invalid Captcha":
                    print("[WARNING] Invalid captcha. Try again.")
                    return {"status": "ERROR - Invalid Captcha", "data": None, "isValid": None}
                elif error == "Invalid Aadhar":
                    return {"status": "Success", "data": None, "isValid": False}
                else:
                    data = self.extract_verification_result()
                    return {"status": "Success", "data": data, "isValid": True}
            except Exception as e:
                print(f"[ERROR] Attempt {attempt + 1} failed: {e}")
            attempt += 1

        return {"status": "ERROR - Max retries reached", "data": None, "isValid": None}

    def close_browser(self):
        print("[INFO] Closing browser.")
        self.driver.quit()


if __name__ == "__main__":
    validator = AadharValidator(headless=False)

    try:
        aadhar_number = validator.get_aadhar_number()
        validator.save_captcha("captcha.png")
        captcha_text = validator.get_captcha_solution()
        result = validator.validate_aadhar(aadhar_number, captcha_text)
        print("\n📄 Final Result:")
        print(result)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    except Exception as ex:
        print(f"[FATAL] Unexpected error: {ex}")
    finally:
        validator.close_browser()
