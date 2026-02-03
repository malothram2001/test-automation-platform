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

@allure.epic("Login & Farmer Flow")
@allure.feature("Authentication & Data Entry")
class TestLogin:

    permissions_to_handle = [
        ("allow_notifications_button", "Allow Notifications"),
    ]

    # --- CONFIGURATION ---
    LOGIN_METHOD = "EMAIL" 

    # --- HELPER METHODS ---

    def input_text_via_adb(self, text):
        """Forces text input using Android ADB commands"""
        try:
            print(f"   -> Attempting ADB input for '{text}'...")
            formatted_text = text.replace(" ", "%s")
            subprocess.run(f"adb shell input text {formatted_text}", shell=True)
            time.sleep(1)
            subprocess.run("adb shell input keyevent 111", shell=True) # Hide Keyboard
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
            actions.pointer_action.pause(0.2)
            actions.pointer_action.pointer_up()
            actions.perform()
            return True
        except Exception as e:
            print(f"Coordinate tap failed: {e}")
            return False

    def perform_scroll(self, driver):
        """Performs a single swipe up (scroll down) gesture"""
        try:
            size = driver.get_window_size()
            start_x = size['width'] // 2
            start_y = int(size['height'] * 0.8) # Start near bottom
            end_y = int(size['height'] * 0.3)   # End near top
            
            print("   -> Scrolling down (Swipe Up)...")
            actions = ActionBuilder(driver)
            p = PointerInput(interaction.POINTER_TOUCH, "finger")
            
            actions.pointer_action.move_to_location(start_x, start_y)
            actions.pointer_action.pointer_down()
            actions.pointer_action.pause(0.2)
            actions.pointer_action.move_to_location(start_x, end_y, duration=600) 
            actions.pointer_action.pointer_up()
            actions.perform()
            time.sleep(1) 
            return True
        except Exception as e:
            print(f"Scroll gesture failed: {e}")
            return False
        

    def swipe_up(self, driver):
        """
        Swipes up on the screen to scroll down.
        Compatible with Appium Python Client v3+.
        """
        # Get screen size
        size = driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.8)
        end_y = int(size['height'] * 0.2)
    
        actions = ActionBuilder(driver)
        p = PointerInput(interaction.POINTER_TOUCH, "finger")
        
        actions.w3c_actions = p
        
        # Define the actions
        p.create_pointer_move(duration=0, x=start_x, y=start_y, origin=interaction.POINTER_VIEWPORT)
        p.create_pointer_down()
        
        # ⚠️ NOTE: The 'duration' arg is actually valid in create_pointer_move (part of PointerInput), 
        # but NOT in actions.pointer_action.move_to_location.
        # To be safe, use this sequence:
        
        p.create_pause(0.5) # Wait a bit before moving
        p.create_pointer_move(duration=600, x=start_x, y=end_y, origin=interaction.POINTER_VIEWPORT) # 600ms swipe
        p.create_pointer_up()
        
        actions.perform()    

    def scroll_to_find(self, driver, xpath, max_scrolls=3):
        """
        Tries to find an element. If not found, scrolls and tries again.
        """
        if not xpath: return None

        for i in range(max_scrolls + 1):
            try:
                element = WebDriverWait(driver, 1).until(
                    EC.visibility_of_element_located((AppiumBy.XPATH, xpath))
                )
                return element # Found it!
            except:
                if i < max_scrolls:
                    print(f"   -> Element not visible yet. Scrolling ({i+1}/{max_scrolls})...")
                    self.perform_scroll(driver)
                else:
                    pass 
        return None

    def smart_click(self, driver, xpath, coordinates, element_name, timeout=5):
        """Tries to click via XPath (with Auto-Scroll). If fails, taps specific coordinates."""
        
        # 1. Try finding via XPath (with Scrolling)
        if xpath:
            print(f"[{element_name}] Searching via XPath...")
            try:
                element = self.scroll_to_find(driver, xpath) # Uses helper to scroll if needed
                if element:
                    element.click()
                    print(f"[{element_name}] Clicked via XPath.")
                    return True
                else:
                    print(f"[{element_name}] Not found via XPath after scrolling.")
            except Exception as e:
                print(f"[{element_name}] XPath interaction failed: {e}")
        
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
        """Robust text input: XPath (Auto-Scroll) -> ADB Fallback"""
        try:
            print(f"[{element_name}] Method 1: Trying standard XPath...")
            element = self.scroll_to_find(driver, xpath) # Uses helper to scroll if needed
            if element:
                element.click()
                time.sleep(0.5)
                element.clear()
                element.send_keys(text)
                try: driver.hide_keyboard()
                except: pass
                return True
        except:
            print(f"[{element_name}] Method 1 failed.")

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

    def smart_select_dropdown(self, driver, dropdown_xpath, option_xpath, dropdown_coords, option_coords, name):
        """Helper to handle dropdown selection logic"""
        
        # NOTE: smart_click inside here will handle the scrolling to the dropdown itself
        print(f"[{name}] Opening Dropdown...")
        if not self.smart_click(driver, dropdown_xpath, dropdown_coords, f"{name} Dropdown"):
             print(f"[{name}] Failed to open dropdown.")
             return False
        
        time.sleep(1) 

        print(f"[{name}] Selecting Option...")
        if not self.smart_click(driver, option_xpath, option_coords, f"{name} Option"):
            print(f"[{name}] Failed to select option.")
            return False
            
        return True

    # --- TEST FLOW ---

    @allure.story("Login and Create Farmer")
    @allure.title("Verify user can login and add a new farmer")
    def test_login_and_add_farmer(self, driver):
        
        print(f"\n--- STARTING TEST WITH LOGIN_METHOD: {self.LOGIN_METHOD} ---\n")
        
        test_flow_steps = []

        # --- Load JSON ---
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
        farmer_xpaths = data.get("farmer_screen", {})
        
        login_coords = data.get("coordinates", {}).get("login_screen", {})
        dashboard_coords = data.get("coordinates", {}).get("dashboard_screen", {})
        farmer_coords = data.get("coordinates", {}).get("farmer_screen", {})

        try:
            # ========================================================
            # PART 1-3: LOGIN FLOW
            # ========================================================
            
            with allure.step("1. Language Selection"):
                key = "next_button_language_login"
                self.smart_click(driver, login_xpaths.get(key), login_coords.get(key), key)

            with allure.step("2. Allow Notifications"):
                key = "allow_notifications_button"
                self.smart_click(driver, login_xpaths.get(key), login_coords.get(key), key, timeout=3)

            login_performed = False
            if self.LOGIN_METHOD == "PHONE":
                login_performed = True
                # Phone Logic Omitted
                pass 

            elif self.LOGIN_METHOD == "EMAIL":
                login_performed = True
                with allure.step("3a. Select Email Tab"):
                    self.smart_click(driver, login_xpaths.get("tab_email_login"), login_coords.get("tab_email_login"), "Email Tab")
                with allure.step("3b. Enter Email"):
                    self.smart_send_keys(driver, login_xpaths.get("email_input"), "fa1@yopmail.com", "Email Input")
                with allure.step("3c. Enter Password"):
                    self.smart_send_keys(driver, login_xpaths.get("password_input"), "Fa1@2025", "Password Input")
                with allure.step("3d. Click Submit"):
                    key = "submit_login_button"
                    if not self.smart_click(driver, login_xpaths.get(key), login_coords.get(key), key):
                        raise Exception("Submit button failed")

            if not login_performed: raise ValueError("Login method not implemented")

            # 4. Post-Login Permissions
            permissions_to_handle = [
                ("allow_picture_button", "Allow Picture"),
                ("allow_location_button", "Allow Location"),
                ("allow_audio_button", "Allow Audio")
            ]
            for key, desc in permissions_to_handle:
                with allure.step(f"4. Post-Login Permission: {desc}"):
                    self.smart_click(driver, login_xpaths.get(key), login_coords.get(key), key, timeout=3)

            # # 5. Verify Dashboard
            # with allure.step("5. Verify Dashboard"):
            #     dashboard_title_xpath = dashboard_xpaths.get("dashboard_title")
            #     try:
            #         WebDriverWait(driver, 15).until(EC.presence_of_element_located((AppiumBy.XPATH, dashboard_title_xpath)))
            #         print("Dashboard found!")
            #         test_flow_steps.append({"step": "Dashboard Verified", "status": "Success"})
            #     except:
            #         raise Exception("Dashboard not found")

            # ========================================================
            # PART 5: ADD FARMER FLOW (With Explicit Scrolls)
            # ========================================================
            
            print("\n--- STARTING ADD FARMER FLOW ---\n")

            with allure.step("6. Click Add Button"):
                key = "add_button_dashboard" 
                if not self.smart_click(driver, dashboard_xpaths.get(key), dashboard_coords.get(key), "Add Button"):
                    raise Exception("Failed to click global Add button")

            with allure.step("7. Click 'Add New Farmer'"):
                key = "add_new_farmer_option"
                if not self.smart_click(driver, dashboard_xpaths.get(key), dashboard_coords.get(key), "Add New Farmer Option"):
                    raise Exception("Failed to click Add New Farmer option")

            with allure.step("8. Enter Farmer Name"):
                key = "farmer_name_input"
                farmer_name = "Test Farmer " + str(time.time())[-4:] 
                if not self.smart_send_keys(driver, farmer_xpaths.get(key), farmer_name, "Farmer Name Input", farmer_coords.get(key)):
                     raise Exception("Failed to enter Farmer Name")

            with allure.step("9. Enter Farmer Mobile"):
                key = "farmer_mobile_input"
                if not self.smart_send_keys(driver, farmer_xpaths.get(key), "1245125251", "Farmer Mobile Input", farmer_coords.get(key)):
                    raise Exception("Failed to enter Farmer Mobile")

            # UPDATED STEP 10: Select Business Unit (Based on Code 2)
            # # ---------------------------------------------------------
            # with allure.step("10. Select Business Unit"):
            #     dropdown_key = "business_unit_dropdown"
            #     option_key = "business_unit_option_1"
                
            #     print("   -> Explicitly scrolling to find Business Unit dropdown...")
            #     self.scroll_to_find(driver, farmer_xpaths.get(dropdown_key))
                
            #     # Click Dropdown
            #     if not self.smart_click(driver, farmer_xpaths.get(dropdown_key), farmer_coords.get(dropdown_key), "Business Unit Dropdown"):
            #         raise Exception("Failed to open Business Unit dropdown")
                
            #     time.sleep(2) # Wait for animation

            #     # Click Option (Agriculture)
            #     if not self.smart_click(driver, farmer_xpaths.get(option_key), farmer_coords.get(option_key), "Business Unit Option"):
            #         raise Exception("Failed to select Business Unit Option")

            # # ---------------------------------------------------------
            # # UPDATED STEP 11: Select Field Agent (Based on Code 2 Logic)
            # # ---------------------------------------------------------
            # with allure.step("11. Select Field Agent"):
            #     dropdown_key = "field_agent_dropdown"
            #     option_key = "field_agent_option_1" # FA1
                
            #     print("   -> Explicitly scrolling to find Field Agent dropdown...")
            #     self.scroll_to_find(driver, farmer_xpaths.get(dropdown_key))

            #     # 1. Open Dropdown
            #     if not self.smart_click(driver, farmer_xpaths.get(dropdown_key), farmer_coords.get(dropdown_key), "Field Agent Dropdown"):
            #         raise Exception("Failed to open Field Agent dropdown")
                
            #     time.sleep(2)

            #     # 2. Select Option (Click 1)
            #     print(f"   -> Selecting {option_key} (Click 1)...")
            #     if not self.smart_click(driver, farmer_xpaths.get(option_key), farmer_coords.get(option_key), "Field Agent Option (1st Click)"):
            #         raise Exception("Failed to select Field Agent Option")
                
            #     time.sleep(1)

            #     # 3. Confirm Selection (Click 2 - As per Code 2)
            #     print(f"   -> Confirming {option_key} (Click 2)...")
            #     self.smart_click(driver, farmer_xpaths.get(option_key), farmer_coords.get(option_key), "Field Agent Option (2nd Click)")
                
            #     time.sleep(3) # Allow UI to update

            #     # 4. Tap Outside to Close
            #     print("   -> Tapping outside (100, 100) to close dropdown...")
            #     self.tap_at_coordinates(driver, 100, 100)
            #     time.sleep(2)

            #     # 5. Verification (Optional but recommended based on Code 2)
            #     try:
            #         element = driver.find_element(AppiumBy.XPATH, farmer_xpaths.get(dropdown_key))
            #         if "FA1" not in element.text and "Field Agent" in element.text:
            #              print(f"Warning: Field Agent might not have been selected. Current text: {element.text}")
            #     except:
            #         pass

            with allure.step("12. Click Submit Farmer"):
                key = "submit_farmer_button"
                if not self.smart_click(driver, farmer_xpaths.get(key), farmer_coords.get(key), "Submit Farmer Button"):
                    raise Exception("Failed to click Submit Farmer button")
            
            allure.attach("Farmer Created Successfully", name="Result", attachment_type=allure.attachment_type.TEXT)
            test_flow_steps.append({"step": "Farmer Created", "status": "Success"})
            print("Farmer creation flow completed!")

            with allure.step("12. Click Submit Farmer"):
                key = "submit_farmer_button"
                # Smart click handles scroll for the button too
                if not self.smart_click(driver, farmer_xpaths.get(key), farmer_coords.get(key), "Submit Farmer Button"):
                    raise Exception("Failed to click Submit Farmer button")
            
            allure.attach("Farmer Created Successfully", name="Result", attachment_type=allure.attachment_type.TEXT)
            test_flow_steps.append({"step": "Farmer Created", "status": "Success"})
            print("Farmer creation flow completed!")
            time.sleep(3)

                # ========================================================
            # PART 3: ADD FARM FLOW (New Logic)
            # ========================================================
            
            print("\n--- STARTING ADD FARM FLOW ---\n")

            with allure.step("13. Click Draw on Map (Initiate Farm)"):
                # As per prompt: "here after submit -- click on draw on map"
                key = "draw_on_map_button"
                # Using None for coords as we are relying on the injected XPaths
                if not self.smart_click(driver, farmer_xpaths.get(key), None, "Draw on Map (Initial)"):
                    raise Exception("Failed to click initial Draw on Map button")

            # with allure.step("14. Enter Farm Name"):
            #     key = "farm_name_input"
            #     if not self.smart_send_keys(driver, farmer_xpaths.get(key), "My New Farm", "Farm Name Input"):
            #         raise Exception("Failed to enter Farm Name")

            with allure.step("15. Submit Farm Name"):
                key = "farm_submit_button"
                if not self.smart_click(driver, farmer_xpaths.get(key), None, "Farm Submit Button"):
                    raise Exception("Failed to click Farm Submit")
            time.sleep(5)

            # ========================================================
            # PART 4: ADD CROP DETAILS
            # ========================================================
            
            print("\n--- STARTING ADD CROP FLOW ---\n")
            
            with allure.step("16. Select Crop Name"):
                # Click Dropdown
                if not self.smart_click(driver, farmer_xpaths.get("crop_name_input"), None, "Crop Name Dropdown"):
                    raise Exception("Failed to click Crop Name Dropdown")
                # Click Option
                if not self.smart_click(driver, farmer_xpaths.get("crop_name_item"), None, "Crop Name Option (Black Gram)"):
                    raise Exception("Failed to select Black Gram")

            with allure.step("17. Select Crop Duration (Short)"):
                # 3. Click the "Short" button directly
                # logic: The buttons (Short/Medium/Long) appear automatically after selecting the crop.
                
                key = "short_duration_button"
                
                # Check if the button exists and click it
                if not self.smart_click(driver, crop_xpaths.get(key), None, "Short Duration Button"):
                    # Optional: Add logic here if you want to fall back to Medium/Long if Short isn't available
                    raise Exception("Failed to select Short Duration button (Buttons might not have loaded or crop has no duration)")

            with allure.step("18. Select Sowing Type"):
                if not self.smart_click(driver, farmer_xpaths.get("sowing_type_dropdown"), None, "Sowing Type Dropdown"):
                    raise Exception("Failed to click Sowing Type Dropdown")
                if not self.smart_click(driver, farmer_xpaths.get("sowing_type_option"), None, "Sowing Type Option"):
                    raise Exception("Failed to select Direct Sowing")

            with allure.step("19. Select Dates"):
                # Open Sowing Date Picker
                if not self.smart_click(driver, farmer_xpaths.get("sowing_date_picker"), None, "Sowing Date Picker"):
                    raise Exception("Failed to click Sowing Date picker")
                
                # Wait for Calendar & Select Date
                # Note: This is specific to the "03 March 2025" logic in your request
                if not self.smart_click(driver, farmer_xpaths.get("calendar_date_select"), None, "Select Date in Calendar"):
                    print("Warning: Specific date not found, attempting to pick default/today if available or fail.")
                
                # Click OK
                if not self.smart_click(driver, farmer_xpaths.get("calendar_ok_button"), None, "Calendar OK Button"):
                    raise Exception("Failed to click OK on calendar")
                
                # Assuming Harvest Date selection logic follows the same pattern or is auto-calculated.
                # If manual selection is needed, repeat the logic above.

            with allure.step("20. Submit Crop Details"):
                key = "crop_submit_button"
                if not self.smart_click(driver, farmer_xpaths.get(key), None, "Crop Submit Button"):
                    raise Exception("Failed to click Crop Submit")
            time.sleep(5)

            # ========================================================
            # PART 5: DRAW BOUNDARY (Polygon)
            # ========================================================
            
            print("\n--- STARTING BOUNDARY DRAWING ---\n")

            with allure.step("21. Click Add Boundary"):
                # Prompt: "then click on add bounday map will vissible"
                # If the button is "Draw on map" again, update the key below
                key = "add_boundary_button" 
                # Fallback to the initial draw button if 'Add Boundary' isn't the text
                xpath = farmer_xpaths.get(key) or farmer_xpaths.get("draw_on_map_initial")
                
                if not self.smart_click(driver, xpath, None, "Add Boundary Button"):
                    raise Exception("Failed to click Add Boundary button")

            with allure.step("22. Draw Polygon on Map"):
                print("Waiting for map to load...")
                time.sleep(5) # Wait for map tiles

                # Define the polygon coordinates (screen relative)
                # Ensure these coords are valid for your device screen size
                polygon_coords = [(400, 800), (600, 1000), (800, 900), (700, 700), (400, 800)]
                
                actions = ActionBuilder(driver)
                p = PointerInput(interaction.POINTER_TOUCH, "finger")
                
                for idx, (x, y) in enumerate(polygon_coords):
                    print(f"Drawing point {idx+1} at ({x}, {y})...")
                    actions.pointer_action.move_to_location(x, y)
                    actions.pointer_action.pointer_down()
                    actions.pointer_action.pause(0.5)
                    actions.pointer_action.pointer_up()
                    actions.perform()
                    time.sleep(0.5)

            with allure.step("23. Save Boundary"):
                key = "save_boundary_button"
                if not self.smart_click(driver, farmer_xpaths.get(key), None, "Save Boundary Button"):
                    raise Exception("Failed to click Save & Approve")

            # Final Success
            allure.attach("Farm and Crop Added Successfully", name="Final_Result", attachment_type=allure.attachment_type.TEXT)
            test_flow_steps.append({"step": "Farm & Boundary Added", "status": "Success"})
            time.sleep(5)

        except Exception as e:
            try: allure.attach(driver.get_screenshot_as_png(), name="Failure_Screenshot", attachment_type=allure.attachment_type.PNG)
            except: pass
            raise e

        finally:
            os.makedirs("test-flows", exist_ok=True)
            with open("test-flows/farmer_flow_success.json", "w") as f:
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