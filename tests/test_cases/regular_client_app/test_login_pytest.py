import time
import allure
import pytest
import json
import os
import subprocess  # Required for ADB commands
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

@allure.epic("Login Flow")
@allure.feature("Authentication")
class TestLogin:

    permissions_to_handle = [
                ("allow_notifications_button", "Allow Notifications"),

            ]

    # --- CONFIGURATION ---
    # Set to "PHONE" or "EMAIL"
    LOGIN_METHOD = "PHONE" 

    # --- HELPER METHODS ---

    def input_text_via_adb(self, text):
        """Forces text input using Android ADB commands (Fixes emulator typing issues)"""
        try:
            print(f"   -> Attempting ADB input for '{text}'...")
            # ADB requires spaces to be escaped as %s
            formatted_text = text.replace(" ", "%s")
            # 1. Input the text
            subprocess.run(f"adb shell input text {formatted_text}", shell=True)
            time.sleep(1)
            # 2. Hide keyboard (Key code 111 is ESC/Back) so it doesn't block buttons
            subprocess.run("adb shell input keyevent 111", shell=True)
            return True
        except Exception as e:
            print(f"ADB Input failed: {e}")
            return False

    def tap_at_coordinates(self, driver, x, y):
        """Reliable tap using W3C Actions"""
        try:
            print(f"   -> Tapping coordinates: {x}, {y}")
            actions = ActionBuilder(driver)
            p = PointerInput(interaction.POINTER_TOUCH, "finger")
            actions.pointer_action.move_to_location(x, y)
            actions.pointer_action.pointer_down()
            actions.pointer_action.pause(0.2) # Short pause to register touch
            actions.pointer_action.pointer_up()
            actions.perform()
            return True
        except Exception as e:
            print(f"Coordinate tap failed: {e}")
            return False

    def smart_click(self, driver, xpath, coordinates, element_name, timeout=5):
        """
        Tries to click via XPath. If fails, taps specific coordinates.
        Args:
            timeout: How long to wait. For permissions, use a short timeout (e.g., 3s).
        """
        # 1. Try finding via XPath
        if xpath:
            try:
                # print(f"[{element_name}] Trying XPath...")
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, xpath))
                )
                element.click()
                print(f"[{element_name}] Clicked via XPath.")
                return True
            except:
                # Be silent about permissions failing, as they might not exist
                pass
        
        # 2. Try clicking via Coordinates (Fallback)
        if coordinates:
            try:
                x, y = coordinates
                print(f"[{element_name}] Fallback: Tapping at {x}, {y}")
                self.tap_at_coordinates(driver, x, y)
                return True
            except Exception as e:
                print(f"[{element_name}] Coordinate tap failed: {e}")
        
        return False

    def smart_send_keys(self, driver, xpath, text, element_name, coordinates=None):
        """
        Robust text input: XPath -> ADB Fallback
        """
        # METHOD 1: Standard XPath Interaction
        try:
            print(f"[{element_name}] Method 1: Trying standard XPath...")
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((AppiumBy.XPATH, xpath))
            )
            element.click()
            time.sleep(0.5)
            element.clear()
            element.send_keys(text)
            try: driver.hide_keyboard()
            except: pass
            return True
        except:
            print(f"[{element_name}] Method 1 failed.")

        # METHOD 2: Coordinate Tap + ADB Injection
        if coordinates:
            try:
                x, y = coordinates
                print(f"[{element_name}] Method 2: Tapping {x},{y} and using ADB...")
                self.tap_at_coordinates(driver, x, y)
                time.sleep(1)
                self.input_text_via_adb(text)
                return True
            except Exception as e:
                print(f"[{element_name}] Method 2 failed: {e}")

        return False

    # --- TEST FLOW ---

    @allure.story("Successful Login")
    @allure.title("Verify user can login with valid credentials")
    def test_login_success(self, driver):
        test_flow_steps = []

        # --- Load JSON (Robust Path) ---
        filename = 'regular_client.json'
        possible_paths = [
            os.path.join('locators', filename),
            os.path.join('tests', 'locators', filename),
            os.path.join(os.getcwd(), 'locators', filename),
        ]
        json_path = next((p for p in possible_paths if os.path.exists(p)), None)
        if not json_path: raise FileNotFoundError(f"Could not find '{filename}'")

        with open(json_path, 'r') as f: data = json.load(f)

        login_xpaths = data.get("login_screen", {})
        dashboard_xpaths = data.get("dashboard_screen", {})
        all_coords = data.get("coordinates", {}).get("login_screen", {})

        try:
            # ========================================================
            # PART 1: PRE-LOGIN STEPS (Language & Notifications)
            # ========================================================
            
            # 1. Language Next
            with allure.step("1. Language Selection"):
                key = "next_button_language_login"
                if not self.smart_click(driver, login_xpaths.get(key), all_coords.get(key), key):
                    raise Exception("Language Next button failed")

            # 2. Pre-Login Permission: Notifications
            # We use a short timeout (3s) because on some devices/Android versions, this might not appear yet.
            with allure.step("2. Allow Notifications (Pre-Login)"):
                key = "allow_notifications_button"
                self.smart_click(driver, login_xpaths.get(key), all_coords.get(key), key, timeout=3)

            # ========================================================
            # PART 2: LOGIN LOGIC (Phone or Email)
            # ========================================================
            
            # if self.LOGIN_METHOD == "PHONE":
            #     with allure.step("3a. Select Phone Tab"):
            #         self.smart_click(driver, login_xpaths.get("tab_phone_login"), all_coords.get("tab_phone_login"), "Phone Tab")

            #     with allure.step("3b. Enter Phone Number"):
            #         key = "phone_number_input"
            #         coords = all_coords.get(key, [540, 600]) # Default fallback
            #         success = self.smart_send_keys(driver, login_xpaths.get(key), "9618574550", "Phone Input", coords)
            #         if not success: print("WARNING: Phone input failed.")

            #     with allure.step("3c. Click Next"):
            #         key = "next_button_login"
            #         if not self.smart_click(driver, login_xpaths.get(key), all_coords.get(key), key):
            #             raise Exception("Login Next button failed")

            #     with allure.step("3d. Verify OTP"):
            #         print("Waiting for OTP...")
            #         time.sleep(8) 
            #         key = "verify_button_login"
            #         if not self.smart_click(driver, login_xpaths.get(key), all_coords.get(key), key):
            #             raise Exception("Verify OTP button failed")

            if self.LOGIN_METHOD == "EMAIL":
                with allure.step("3a. Select Email Tab"):
                    self.smart_click(driver, login_xpaths.get("tab_email_login"), all_coords.get("tab_email_login"), "Email Tab")

                with allure.step("3b. Enter Email"):
                    self.smart_send_keys(driver, login_xpaths.get("email_input"), "testteam@yopmail.com", "Email Input")

                with allure.step("3c. Enter Password"):
                    self.smart_send_keys(driver, login_xpaths.get("password_input"), "Test@2025", "Password Input")

                with allure.step("3d. Click Submit"):
                    key = "submit_login_button"
                    if not self.smart_click(driver, login_xpaths.get(key), all_coords.get(key), key):
                        raise Exception("Submit button failed")

            # ========================================================
            # PART 3: POST-LOGIN PERMISSIONS (Location, Picture, Audio)
            # ========================================================
            # These usually appear while the dashboard is loading
            
            permissions_to_handle = [
                ("allow_picture_button", "Allow Picture"),
                ("allow_location_button", "Allow Location"),
                ("allow_audio_button", "Allow Audio")
            ]

            for key, desc in permissions_to_handle:
                with allure.step(f"4. Post-Login Permission: {desc}"):
                    # We simply try to click them. If they aren't there, we move on.
                    # This prevents the test from failing if a permission was already granted or doesn't appear.
                    self.smart_click(
                        driver, 
                        login_xpaths.get(key), 
                        all_coords.get(key), 
                        key, 
                        timeout=3
                    )

            # ========================================================
            # PART 4: DASHBOARD VERIFICATION
            # ========================================================

            with allure.step("5. Verify Dashboard"):
                dashboard_title_xpath = dashboard_xpaths.get("dashboard_title")
                try:
                    # Wait up to 15 seconds for dashboard, as permissions might have slowed it down
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((AppiumBy.XPATH, dashboard_title_xpath))
                    )
                    allure.attach("Login successful", name="Result", attachment_type=allure.attachment_type.TEXT)
                    test_flow_steps.append({"step": "Dashboard Verified", "status": "Success"})
                    print("Dashboard found!")
                except:
                    print("Dashboard check timed out. Verify if app crashed or stuck on permissions.")
                    # Optional: Take screenshot on failure
                    try: allure.attach(driver.get_screenshot_as_png(), name="Failure_Screenshot", attachment_type=allure.attachment_type.PNG)
                    except: pass
                    raise Exception("Dashboard not found")

        finally:
            # Save the captured flow to a file
            os.makedirs("test-flows", exist_ok=True)
            with open("test-flows/login_flow_success.json", "w") as f:
                json.dump(test_flow_steps, f, indent=4)

        # try:
        #     with allure.step("1. Next button on language selection screen"):
        #         next_button_language_login, used_ocr = smart_find_element(
        #             driver, name="next_button_language_login", xpath=language_next_xpath, fallback_text="Next"
        #         )
        #         if next_button_language_login:
        #             next_button_language_login.click()
        #             test_flow_steps.append({"step": "Click Next on language screen", "status": "Success"})
        #         else:
        #             raise Exception("Next button in language selection not found")

        #     with allure.step("2. Allow picture"):
        #         allow_picture_button, used_ocr = smart_find_element(
        #             driver, name="allow_picture_button", xpath=allow_picture_button_xpath, fallback_text="While using the app"
        #         )
        #         if allow_picture_button:
        #             allow_picture_button.click()
        #             test_flow_steps.append({"step": "Allow picture permission", "status": "Success"})
        #         else:
        #             raise Exception("Allow picture button not found")

        #     with allure.step("3. Allow location"):
        #         allow_location_button, used_ocr = smart_find_element(
        #             driver, name="allow_location_button", xpath=allow_location_button_xpath, fallback_text="While using"
        #         )
        #         if allow_location_button:
        #             allow_location_button.click()
        #             test_flow_steps.append({"step": "Allow location permission", "status": "Success"})
        #         else:
        #             raise Exception("Allow Location button not found")
            
        #     with allure.step("4. Allow audio"):
        #         allow_audio_button, used_ocr = smart_find_element(
        #             driver, name="allow_audio_button", xpath=allow_audio_button_xpath, fallback_text="While using the app"
        #         )
        #         if allow_audio_button:
        #             allow_audio_button.click()
        #             test_flow_steps.append({"step": "Allow audio permission", "status": "Success"})
        #         else:
        #             raise Exception("Allow audio button not found")

        #     with allure.step("5. Allow notifications"):
        #         allow_notifications_button, used_ocr = smart_find_element(
        #             driver, name="allow_notifications_button", xpath=allow_notifications_button_xpath, fallback_text="Allow"
        #         )
        #         if allow_notifications_button:
        #             allow_notifications_button.click()
        #             test_flow_steps.append({"step": "Allow notifications permission", "status": "Success"})
        #         else:
        #             raise Exception("Allow Notifications button not found")

        #     with allure.step("6. Enter phone number"):
        #         phone_input, used_ocr = smart_find_element(
        #             driver, name="phone_number_input", xpath=phone_number_input_xpath, fallback_text="Phone"
        #         )
        #         if phone_input:
        #             phone_input.clear()
        #             phone_input.send_keys("7660852538")
        #             test_flow_steps.append({"step": "Enter valid phone number", "status": "Success", "value": "7660852538"})
        #         else:
        #             raise Exception("Phone input field not found")

        #     with allure.step("7. Tap next button"):
        #         next_button, used_ocr = smart_find_element(
        #             driver, name="next_button_login", xpath=next_button_login_xpath, fallback_text="Next"
        #         )
        #         if next_button:
        #             next_button.click()
        #             test_flow_steps.append({"step": "Click Next after entering phone number", "status": "Success"})
        #         else:
        #             raise Exception("Next button not found")

        #     with allure.step("8. Wait for OTP and verify"):
        #         time.sleep(10)  # Waiting for OTP
        #         verify_button, used_ocr = smart_find_element(
        #             driver, name="verify_button_login", xpath=verify_button_login_xpath, fallback_text="Verify"
        #         )
        #         if verify_button:
        #             verify_button.click()
        #             test_flow_steps.append({"step": "Click Verify OTP", "status": "Success"})
        #         else:
        #             raise Exception("Verify button not found")

        #     with allure.step("9. Verify dashboard appears"):
        #         dashboard, used_ocr = smart_find_element(
        #             driver, name="dashboard_title", xpath=dashboard_title_xpath, fallback_text="Dashboard"
        #         )
        #         assert dashboard is not None or used_ocr, "Dashboard not found after login"
        #         test_flow_steps.append({"step": "Verify dashboard is displayed", "status": "Success"})
        #         allure.attach("Login successful", name="Result", attachment_type=allure.attachment_type.TEXT)

        # finally:
        #     os.makedirs("test-flows", exist_ok=True)
        #     with open("test-flows/login_flow_success.json", "w") as f:
        #         json.dump(test_flow_steps, f, indent=4)