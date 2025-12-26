# import os
# import pytest
# import subprocess
# from utils.ai_agent import AIAgent
# from dotenv import load_dotenv

# load_dotenv()
# def run_tests_and_get_suggestions():
#     """
#     Main function to execute tests, and if they pass,
#     invoke the AI agent to suggest new test flows.
#     """
#     # Create necessary directories
#     os.makedirs("allure-results", exist_ok=True)
#     os.makedirs("screenshots", exist_ok=True)
#     os.makedirs("test-flows", exist_ok=True)

#     # Define paths
#     test_files = [
#         "tests/test_login_pytest.py",
#         "tests/test_onboarding_pytest.py"
#     ]    
#     allure_dir = "allure-results"
    
#     # Run pytest with Allure options
#     result = pytest.main([
#         *test_files,
#         f"--alluredir={allure_dir}",
#         "--clean-alluredir",
#         "-v",
#         "-n=4"
#     ])

#     # If tests passed, run the AI agent
#     if result == pytest.ExitCode.OK:
#         print("\n" + "="*80)
#         print("✅ All tests passed. Asking AI for new test case suggestions...")
#         print("="*80 + "\n")

#         # Ensure you have your OpenAI API key in an environment variable
#         api_key = os.getenv("OPENAI_API_KEY")
#         if not api_key:
#             print("🛑 Error: OPENAI_API_KEY environment variable not set.")
#             return

#         ai_agent = AIAgent(key=api_key)
        
#         flow_file = "test-flows/login_flow_success.json"
        
#         suggestions = ai_agent.suggest_new_tests(flow_file, test_files)
        
#         print("🤖 AI-Generated Test Suggestions:\n")
#         print(suggestions)
        
#         # Optionally, save suggestions to a file
#         with open("ai_test_suggestions.md", "w") as f:
#             f.write(suggestions)
#         print(f"\n💡 Suggestions also saved to 'ai_test_suggestions.md'")

#     else:
#         print("\n" + "="*80)
#         print("❌ Tests failed. Skipping AI suggestion step.")
#         print("="*80 + "\n")
        
#     # To view the report, run: allure serve allure-results
#     print(f"\nTo view the detailed test report, run: allure serve {allure_dir}")

# if __name__ == "__main__":
#     run_tests_and_get_suggestions()
import os
import shutil
# Disable auto-loading of 3rd-party pytest plugins (like browserstack)
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

import pytest
import allure_pytest  # pip install allure-pytest
import requests
import subprocess
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CURRENT_PROC: Optional[subprocess.Popen] = None

def send_log(message: str, status: str = "INFO") -> None:
    """Send one log line to the frontend via /api/log-step."""
    try:
        requests.post(
            f"{BACKEND_URL}/api/log-step",
            json={"message": message, "status": status},
            timeout=3,
        )
    except Exception:
        # Don't break tests if backend logging fails
        pass

def run_pytest_with_logs(pytest_args, module_name: str) -> bool:
  """
  Run pytest in a subprocess and stream all stdout lines
  into the WebSocket log console.
  """
  send_module_status(module_name, "running", f"Starting {module_name} tests")
  send_log(f"==== Running {module_name} tests ====", "INFO")

  # Build command: python -m pytest <args>
  cmd = [os.sys.executable, "-m", "pytest"] + pytest_args

  proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    cwd=os.path.dirname(os.path.dirname(__file__)),  # project root
  )

  # Stream each line to frontend
  assert proc.stdout is not None
  for line in proc.stdout:
    send_log(line.rstrip("\n"), "INFO")

  proc.wait()
  success = (proc.returncode == 0)

  if success:
    send_module_status(module_name, "completed", f"{module_name} tests passed")
    send_log(f"{module_name} tests passed", "SUCCESS")
  else:
    send_module_status(module_name, "failed", f"{module_name} tests failed")
    send_log(f"{module_name} tests failed", "FAILED")

  return success

def send_module_status(module: str, status: str, message: str = ""):
    """Notify backend which module is running/completed."""
    try:
        requests.post(
            f"{BACKEND_URL}/api/module-status",
            json={"module": module, "status": status, "message": message},
            timeout=3,
        )
    except Exception:
        # Do not break tests if backend is down
        pass

def stop_current_tests() -> bool:
    """
    Try to stop the currently running pytest process.
    Returns True if a process was stopped, False otherwise.
    """
    global CURRENT_PROC
    if CURRENT_PROC is None:
        return False

    try:
        send_log("Stopping tests on user request...", "FAILED")
        CURRENT_PROC.terminate()
        try:
            CURRENT_PROC.wait(timeout=5)
        except subprocess.TimeoutExpired:
            CURRENT_PROC.kill()
        send_log("Test process terminated.", "FAILED")
    except Exception as e:
        send_log(f"Error while stopping tests: {e}", "FAILED")
    finally:
        CURRENT_PROC = None

    return True

def run_pytest_streaming(pytest_args: list[str], module_name: str) -> bool:
    global CURRENT_PROC
    """
    Run pytest in a subprocess and stream ALL stdout lines
    to the frontend log console.
    """
    project_root = os.path.dirname(os.path.dirname(__file__))
    cmd = ["pytest", "-s", "-vv"] + pytest_args

    send_module_status(module_name, "running", f"Starting {module_name} tests")
    send_log(f"==== Running {module_name} tests ====", "INFO")

    # cmd = [os.sys.executable, "-m", "pytest"] + pytest_args

    CURRENT_PROC = subprocess.Popen(
        cmd,
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    proc = CURRENT_PROC
    assert proc.stdout is not None
    for line in proc.stdout:
        # Mirror exactly what you see in the terminal
        send_log(line.rstrip("\n"), "INFO")

    proc.wait()
    ok = proc.returncode == 0

    # Clear global when done
    CURRENT_PROC = None

    if ok:
        send_module_status(module_name, "completed", f"{module_name} tests passed")
        send_log(f"{module_name} tests passed", "SUCCESS")
    else:
        send_module_status(module_name, "failed", f"{module_name} tests failed")
        send_log(f"{module_name} tests failed", "FAILED")

    return ok

def run_tests_and_get_suggestions(apk_path: str) -> None:
    """
    Entry point called from FastAPI (background task).
    Streams full pytest output to the frontend.
    """
    if not os.path.exists(apk_path):
        send_log(f"APK not found at {apk_path}", "FAILED")
        return

    send_log(f"Running tests for APK: {apk_path}", "INFO")

    overall_ok = True

    # Adjust test paths to match your repo
    login_ok = run_pytest_streaming(
        ["tests/test_cases/test_login_pytest.py", f"--apk={apk_path}", "-v"],
        module_name="Login",
    )
    overall_ok = overall_ok and login_ok

    # Example second module – change path/name if you have different modules
    # onboarding_ok = run_pytest_streaming(
    #     ["tests/test_cases/test_onboarding_pytest.py", f"--apk={apk_path}", "-v"],
    #     module_name="Onboarding",
    # )
    # overall_ok = overall_ok and onboarding_ok

    if overall_ok:
        send_log("All modules passed", "SUCCESS")
    else:
        send_log("Some modules failed", "FAILED")

    # Define paths
    # test_files = [
    #     "tests/test_cases/test_login_pytest.py",
    #     # "tests/test_cases/test_onboarding_pytest.py"
    # ]    
    # IMPORTANT: no --alluredir / --clean-alluredir here
    # result = pytest.main([
    #     *test_files,
    #     f"--apk={apk_path}",
    #     "-v",
    # ])
    
    # Run pytest with Allure options
    # result = pytest.main([
    #     *test_files,
    #     # f"--apk={apk_path}",
    #     f"--alluredir={allure_dir}",
    #     "--clean-alluredir",
    #     "-v"
    # ])

    # if result == 0:
    #     print("✅ Tests Passed")
    # else:
    #     print("⚠️ Tests Failed or encountered errors")
        
    # To view the report, run: allure serve allure-results
    # print(f"\nTo view the detailed test report, run: allure serve {allure_dir}")

if __name__ == "__main__":
    # run_tests_and_get_suggestions()
    # Example usage for manual testing
    # import sys
    # if len(sys.argv) > 1:
    #     apk = sys.argv[1]
    # else:
    #     print("Usage: python tests/test_runner.py <apk_path>")
    #     sys.exit(1)
    # run_tests_and_get_suggestions(apk)
    import sys

    if len(sys.argv) <= 1:
        print("Usage: python tests/test_runner.py <apk_path>")
        raise SystemExit(1)

    run_tests_and_get_suggestions(sys.argv[1])