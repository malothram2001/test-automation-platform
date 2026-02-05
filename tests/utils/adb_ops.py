import subprocess
import time

def input_text_via_adb(text):
    """
    Forces text input using Android ADB commands.
    Useful when SendKeys fails or keyboard doesn't appear.
    """
    try:
        print(f"   -> Attempting ADB input for '{text}'...")
        # Replace spaces with %s for ADB shell compatibility
        formatted_text = text.replace(" ", "%s")
        subprocess.run(f"adb shell input text {formatted_text}", shell=True)
        time.sleep(1)
        # Keyevent 111 is usually the 'Escape/Back' key to hide keyboard
        subprocess.run("adb shell input keyevent 111", shell=True) 
        return True
    except Exception as e:
        print(f"ADB Input failed: {e}")
        return False