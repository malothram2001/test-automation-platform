import time
from tests.utils.adb_ops import input_text_via_adb
from tests.utils.touch_utils import tap_at_coordinates
from tests.utils.wait_utils import scroll_to_find

def smart_click(driver, xpath, coordinates, element_name, timeout=5):
    """
    Tries to click via XPath (with Auto-Scroll). 
    If that fails, taps specific coordinates as a fallback.
    """
    # 1. Try finding via XPath (with Scrolling)
    if xpath:
        print(f"[{element_name}] Searching via XPath...")
        try:
            element = scroll_to_find(driver, xpath) 
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
            tap_at_coordinates(driver, x, y)
            return True
        except Exception as e:
            print(f"[{element_name}] Coordinate tap failed: {e}")
    
    return False

def smart_send_keys(driver, xpath, text, element_name, coordinates=None):
    """
    Robust text input: 
    1. Try Standard XPath (find -> clear -> send_keys)
    2. Fallback to Tapping coordinates + ADB Input
    """
    # Method 1: Standard XPath
    try:
        print(f"[{element_name}] Method 1: Trying standard XPath...")
        element = scroll_to_find(driver, xpath)
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

    # Method 2: Coordinate Tap + ADB
    if coordinates:
        try:
            x, y = coordinates
            print(f"[{element_name}] Method 2: Tapping {x},{y} and using ADB...")
            tap_at_coordinates(driver, x, y)
            time.sleep(1)
            input_text_via_adb(text)
            return True
        except Exception as e:
            print(f"[{element_name}] Method 2 failed: {e}")

    return False

def smart_select_dropdown(driver, dropdown_xpath, option_xpath, dropdown_coords, option_coords, name):
    """
    Helper to handle dropdown selection logic.
    Opens dropdown -> Waits -> Selects Option.
    """
    print(f"[{name}] Opening Dropdown...")
    if not smart_click(driver, dropdown_xpath, dropdown_coords, f"{name} Dropdown"):
         print(f"[{name}] Failed to open dropdown.")
         return False
    
    time.sleep(1)

    print(f"[{name}] Selecting Option...")
    if not smart_click(driver, option_xpath, option_coords, f"{name} Option"):
        print(f"[{name}] Failed to select option.")
        return False
        
    return True