import time
import allure
import pytest
import json
import os
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

# --- IMPORT CUSTOM UTILITIES ---
from tests.utils.touch_utils import tap_at_coordinates, perform_scroll
from tests.utils.wait_utils import scroll_to_find
from tests.utils.ui_actions import smart_click, smart_send_keys, smart_select_dropdown

@allure.epic("Onboarding Flow")
@allure.feature("Farmer, Farm, Crop & Boundary Creation")
class TestOnboarding:

    @allure.story("Create Farmer, Farm, Crop, and Boundary")
    @allure.title("Verify user can add a new farmer and complete farm onboarding")
    def test_add_farmer_and_details(self, driver):
        
        print("\n--- STARTING ONBOARDING TEST ---\n")
        
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

        dashboard_xpaths = data.get("dashboard_screen", {})
        farmer_xpaths = data.get("farmer_screen", {})
        
        dashboard_coords = data.get("coordinates", {}).get("dashboard_screen", {})
        farmer_coords = data.get("coordinates", {}).get("farmer_screen", {})

        try:
            # ========================================================
            # PART 1: ADD FARMER FLOW
            # ========================================================
            
            print("\n--- STARTING ADD FARMER FLOW ---\n")

            with allure.step("1. Click Add Button"):
                key = "add_button_dashboard"
                if not smart_click(driver, dashboard_xpaths.get(key), dashboard_coords.get(key), "Add Button"):
                    raise Exception("Failed to click global Add button")

            with allure.step("2. Click 'Add New Farmer'"):
                key = "add_new_farmer_option"
                if not smart_click(driver, dashboard_xpaths.get(key), dashboard_coords.get(key), "Add New Farmer Option"):
                    raise Exception("Failed to click Add New Farmer option")

            with allure.step("3. Enter Farmer Name"):
                key = "farmer_name_input"
                farmer_name = "Test Farmer " + str(time.time())[-4:]
                if not smart_send_keys(driver, farmer_xpaths.get(key), farmer_name, "Farmer Name Input", farmer_coords.get(key)):
                     raise Exception("Failed to enter Farmer Name")

            with allure.step("4. Enter Farmer Mobile"):
                key = "farmer_mobile_input"
                if not smart_send_keys(driver, farmer_xpaths.get(key), "1245125251", "Farmer Mobile Input", farmer_coords.get(key)):
                    raise Exception("Failed to enter Farmer Mobile")
                
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


            with allure.step("5. Click Submit Farmer"):
                key = "submit_farmer_button"
                if not smart_click(driver, farmer_xpaths.get(key), farmer_coords.get(key), "Submit Farmer Button"):
                    raise Exception("Failed to click Submit Farmer button")
            
            allure.attach("Farmer Created Successfully", name="Result", attachment_type=allure.attachment_type.TEXT)
            test_flow_steps.append({"step": "Farmer Created", "status": "Success"})
            print("Farmer creation flow completed!")
            time.sleep(3)

            # ========================================================
            # PART 2: ADD FARM FLOW
            # ========================================================
            
            print("\n--- STARTING ADD FARM FLOW ---\n")

            with allure.step("6. Click Draw on Map (Initiate Farm)"):
                key = "draw_on_map_button"
                if not smart_click(driver, farmer_xpaths.get(key), None, "Draw on Map (Initial)"):
                    raise Exception("Failed to click initial Draw on Map button")
                time.sleep(5) 

            with allure.step("14. Enter Farm Name"):
                key = "farm_name_input"
                if not self.smart_send_keys(driver, farmer_xpaths.get(key), "My New Farm", "Farm Name Input"):
                    raise Exception("Failed to enter Farm Name")
                    

            with allure.step("7. Submit Farm Name"):
                key = "farm_submit_button"
                if not smart_click(driver, farmer_xpaths.get(key), None, "Farm Submit Button"):
                    raise Exception("Failed to click Farm Submit")
            time.sleep(10)

            # ========================================================
            # PART 3: ADD CROP DETAILS
            # ========================================================
            
            print("\n--- STARTING ADD CROP FLOW ---\n")
            
            try:
                print("   -> Hiding keyboard before Crop selection...")
                driver.hide_keyboard()
            except:
                pass

            with allure.step("8. Select Crop Name"):
                print("   -> Waiting for Crop Name Dropdown to appear...")
                time.sleep(3)
                
                # Try specific scroll
                scroll_to_find(driver, farmer_xpaths.get("crop_name_input"))

                # 1. Click Dropdown
                if not smart_click(driver, farmer_xpaths.get("crop_name_input"), None, "Crop Name Dropdown"):
                    print("   -> XPath failed for Dropdown. Trying coordinate fallback...")
                    # Coordinate fallback hardcoded as per original
                    if not tap_at_coordinates(driver, 540, 1200):
                        raise Exception("Failed to click Crop Name Dropdown via XPath and Coordinates")
                
                time.sleep(2) 
                
                # 2. Select "Black Gram"
                if not smart_click(driver, farmer_xpaths.get("crop_name_item"), None, "Black Gram Option"):
                    raise Exception("Failed to select Black Gram from the list")

            with allure.step("9. Select Crop Duration (Flexible)"):
                duration_key = "short_duration_button"
                duration_xpath = farmer_xpaths.get(duration_key)
                
                print(f"[Crop Duration] Attempting to find: {duration_key}")
                if not smart_click(driver, duration_xpath, None, "Short Duration"):
                    print("   -> Short button not found. Trying 'Medium' as fallback...")
                    fallback_xpath = farmer_xpaths.get("medium_duration_button")
                    if not smart_click(driver, fallback_xpath, None, "Medium Duration"):
                        print("   -> No duration buttons found. The app might have auto-selected duration.")

            with allure.step("10. Select Sowing Type"):
                if not smart_click(driver, farmer_xpaths.get("sowing_type_dropdown"), None, "Sowing Type Dropdown"):
                    raise Exception("Failed to click Sowing Type Dropdown")
                if not smart_click(driver, farmer_xpaths.get("sowing_type_option"), None, "Direct Sowing Option"):
                    raise Exception("Failed to select Sowing Type Option")

            with allure.step("11. Select Dates"):
                if not smart_click(driver, farmer_xpaths.get("sowing_date_picker"), None, "Sowing Date Picker"):
                    raise Exception("Failed to click Sowing Date picker")
                
                if not smart_click(driver, farmer_xpaths.get("calendar_date_select"), None, "Select Date"):
                    print("Warning: Specific date not found, attempting to proceed with default date.")
                
                if not smart_click(driver, farmer_xpaths.get("calendar_ok_button"), None, "Calendar OK Button"):
                    raise Exception("Failed to click OK on calendar")

            with allure.step("12. Submit Crop Details"):
                submit_key = "crop_submit_button"
                if not smart_click(driver, farmer_xpaths.get(submit_key), None, "Crop Submit Button"):
                    raise Exception("Failed to click Crop Submit")
            
            print("Crop details submission completed!")
            time.sleep(5)
            
            # ========================================================
            # PART 4: DRAW BOUNDARY (Polygon)
            # ========================================================
            
            print("\n--- STARTING BOUNDARY DRAWING ---\n")

            with allure.step("13. Click Add Boundary"):
                key = "add_boundary_button"
                xpath = farmer_xpaths.get(key) or farmer_xpaths.get("draw_on_map_initial")
                
                if not smart_click(driver, xpath, None, "Add Boundary Button"):
                    raise Exception("Failed to click Add Boundary button")

            with allure.step("14. Draw Polygon on Map"):
                print("Waiting for map to load...")
                time.sleep(5) 

                # Define the polygon coordinates (screen relative)
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

            with allure.step("15. Save Boundary"):
                key = "save_boundary_button"
                if not smart_click(driver, farmer_xpaths.get(key), None, "Save Boundary Button"):
                    raise Exception("Failed to click Save & Approve")

            # Final Success
            allure.attach("Farm and Crop Added Successfully", name="Final_Result", attachment_type=allure.attachment_type.TEXT)
            test_flow_steps.append({"step": "Farm & Boundary Added", "status": "Success"})
            time.sleep(5)

        except Exception as e:
            try: allure.attach(driver.get_screenshot_as_png(), name="Onboarding_Failure_Screenshot", attachment_type=allure.attachment_type.PNG)
            except: pass
            raise e

        finally:
            os.makedirs("test-flows", exist_ok=True)
            with open("test-flows/onboarding_flow_success.json", "w") as f:
                json.dump(test_flow_steps, f, indent=4)