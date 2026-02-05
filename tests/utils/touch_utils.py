import allure
import time
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

def tap_at_coordinates(driver, x, y):
    """
    Performs a tap action at the specified x and y coordinates on the screen.
    This function uses the W3C Actions API, which is compatible with the latest
    Appium Python Client (v3+).

    Args:
        driver: The Appium driver instance.
        x (int): The x-coordinate for the tap.
        y (int): The y-coordinate for the tap.
    """
    try:
        print(f"Attempting to tap at coordinates: (x={x}, y={y})")
        
        # 1. Create an ActionBuilder object, which is the entry point for all actions.
        actions = ActionBuilder(driver)
        
        # 2. Get a reference to the 'pointer' (i.e., your finger on the screen).
        finger = actions.pointer_action
        
        # 3. Define the sequence of actions for a tap:
        #    - Move the pointer to the target coordinates.
        #    - Press the pointer down (touch the screen).
        #    - Pause briefly to ensure the tap registers reliably.
        #    - Lift the pointer up (release the touch).
        finger.move_to_location(x, y)
        finger.pointer_down()
        finger.pause(0.1)
        finger.pointer_up()
        
        # 4. Execute the entire sequence of actions.
        actions.perform()
        
        print(f"Successfully tapped at (x={x}, y={y}).")
        allure.attach(f"Tapped at coordinates (x={x}, y={y})", name="Coordinate Tap", attachment_type=allure.attachment_type.TEXT)
        return True
    except Exception as e:
        print(f"Failed to tap at coordinates: {e}")
        allure.attach(f"Failed to tap at (x={x}, y={y}): {e}", name="Coordinate Tap Error", attachment_type=allure.attachment_type.TEXT)
        return False
    
def tap_at_coordinates(driver, x, y):
    """Reliable tap using W3C Actions."""
    try:
        actions = ActionBuilder(driver)
        p = PointerInput(interaction.POINTER_TOUCH, "finger")
        actions.pointer_action.move_to_location(x, y)
        actions.pointer_action.pointer_down()
        actions.pointer_action.pause(0.1)
        actions.pointer_action.pointer_up()
        actions.perform()
        return True
    except Exception as e:
        print(f"Coordinate tap failed: {e}")
        return False

def perform_scroll(driver):
    """Performs a single swipe up (scroll down) gesture."""
    try:
        size = driver.get_window_size()
        start_x = size['width'] // 2
        start_y = int(size['height'] * 0.8)
        end_y = int(size['height'] * 0.3)
        
        print("   -> Scrolling down (Swipe Up)...")
        actions = ActionBuilder(driver)
        p = PointerInput(interaction.POINTER_TOUCH, "finger")
        
        # Correct W3C sequence: move -> down -> move (with duration) -> up
        actions.pointer_action.move_to_location(start_x, start_y)
        actions.pointer_action.pointer_down()
        # Duration is handled by the move_to_location implicitly or via specific pause logic
        # For scrolling, we move the finger to the end location
        actions.pointer_action.move_to_location(start_x, end_y)
        actions.pointer_action.pointer_up()
        actions.perform()
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Scroll gesture failed: {e}")
        return False

def swipe_up(driver):
    """
    Alternative swipe up method.
    Compatible with Appium Python Client v3+.
    """
    size = driver.get_window_size()
    start_x = size['width'] // 2
    start_y = int(size['height'] * 0.8)
    end_y = int(size['height'] * 0.2)
   
    actions = ActionBuilder(driver)
    p = PointerInput(interaction.POINTER_TOUCH, "finger")
    actions.w3c_actions = p
    
    p.create_pause(0.5)
    p.create_pointer_move(duration=600, x=start_x, y=end_y, origin=interaction.POINTER_VIEWPORT)
    p.create_pointer_up()
    
    actions.perform()
