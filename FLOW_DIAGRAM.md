# Test Automation Platform - Flow Diagram

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Test Automation Platform                      │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    ┌─────────┴─────────┐
                    │                   │
              ┌─────▼─────┐       ┌─────▼──────┐
              │ FRONTEND  │       │  BACKEND   │
              │(React+    │       │(FastAPI+   │
              │ Vite)     │       │ WebSocket) │
              └─────┬─────┘       └─────┬──────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Test Execution   │
                    │  (Pytest+Appium)  │
                    │  (APK Testing)    │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Test Reporting   │
                    │  (Allure Reports) │
                    └───────────────────┘
```

## 2. Frontend to Backend Communication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                       FRONTEND (React)                        │
│                     test-platform/src/                        │
│                                                               │
│  • App.jsx (Main Component)                                  │
│  • WebSocket Connection to ws://localhost:8000/ws/test-status│
│  • REST API calls to http://localhost:8000                   │
│                                                               │
│  APP VARIANTS SUPPORTED:                                     │
│  ├─ Krishivaas Farmer (Regular)                             │
│  ├─ Krishivaas Client (Regular)                             │
│  ├─ State Farmer App                                        │
│  └─ State Client App                                        │
└──────────────────┬───────────────────────────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
   [Play]   [Select App]  [Select Module]
   Button   Dropdown      List
       │           │           │
       └───────────┼───────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  USER INITIATES     │
         │  TEST RUN REQUEST   │
         └────────────┬────────┘
                      │
                      ▼
    ┌─────────────────────────────────────┐
    │         BACKEND (FastAPI)           │
    │       backend/server.py             │
    │                                     │
    │  ✓ Receive test run request         │
    │  ✓ Download APK from Google Drive   │
    │  ✓ Extract app icon                 │
    │  ✓ Get APK info                     │
    └─────────────────┬───────────────────┘
                      │
                      ▼
```

## 3. Backend Test Execution Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                BACKEND PROCESSING FLOW                        │
└──────────────────────┬───────────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  server.py Receives Request │
        │  • Parse test parameters    │
        │  • Load APK from drive      │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  gdrive_loader.py           │
        │  • download_apk()           │
        │  • extract_app_icon()       │
        │  • get_apk_info()           │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  temp_apks/ Directory       │
        │  (Store downloaded APKs)    │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  test_runner.py             │
        │                             │
        │  run_tests_and_get_         │
        │  suggestions()              │
        └──────────────┬──────────────┘
                       │
```

## 4. Test Runner Execution Pipeline

```
┌────────────────────────────────────────────────────────────────┐
│                    TEST RUNNER (Pytest)                        │
│                  tests/test_runner.py                          │
└────────────────────┬─────────────────────────────────────────┘
                     │
      ┌──────────────▼──────────────┐
      │ TEST REGISTRY:              │
      │ • regular_farmer            │
      │   └─ test_login_pytest.py   │
      │   └─ test_onboarding_pytest │
      │ • regular_client            │
      │   └─ test_login_pytest.py   │
      └──────────────┬──────────────┘
                     │
      ┌──────────────▼──────────────────────┐
      │ Load Locators from JSON            │
      │ tests/locators/                    │
      │ • regular_client.json              │
      │ • regular_farmer.json              │
      └──────────────┬───────────────────────┘
                     │
      ┌──────────────▼──────────────┐
      │ Initialize Appium Driver   │
      │ conftest.py                │
      │ • UiAutomator2Options      │
      │ • Connect to AndroidDevice │
      │ • Load APK app             │
      └──────────────┬──────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
test_login      test_onboarding  test_dashboard
    │                │                │
    │   Execute Test Steps    │
    │                │                │
    └────────────────┼────────────────┘
                     │
      ┌──────────────▼──────────────┐
      │ Test Utilities Execution   │
      │ tests/utils/               │
      │ • ai_agent.py              │
      │ • ocr_utils.py             │
      │ • touch_utils.py           │
      │ • wait_utils.py            │
      │ • test_logger.py           │
      └──────────────┬──────────────┘
                     │
      ┌──────────────▼──────────────┐
      │ Collect Screenshots/Logs   │
      │ on Test Failure            │
      └──────────────┬──────────────┘
                     │
      ┌──────────────▼──────────────┐
      │ Generate Allure Results    │
      │ allure-results/            │
      │ (JSON format)              │
      └──────────────┬──────────────┘
                     │
```

## 5. Appium Test Execution Flow

```
┌─────────────────────────────────────────┐
│      APPIUM DRIVER (conftest.py)        │
└──────────────────┬──────────────────────┘
                   │
     ┌─────────────▼──────────┐
     │ UiAutomator2Options   │
     │ • Platform: Android   │
     │ • Device: AndroidDevice
     │ • App: /path/to/app  │
     └─────────────┬──────────┘
                   │
     ┌─────────────▼──────────────────┐
     │ Connect to Appium Server       │
     │ (localhost:4723)               │
     └─────────────┬──────────────────┘
                   │
     ┌─────────────▼──────────────────┐
     │ Load APK on Android Emulator   │
     └─────────────┬──────────────────┘
                   │
     ┌─────────────▼──────────────────┐
     │ Run Test Steps:                │
     │ • Find Elements (by locators)  │
     │ • Tap/Click                    │
     │ • Type Text                    │
     │ • Take Screenshots             │
     │ • Verify UI State              │
     └─────────────┬──────────────────┘
                   │
     ┌─────────────▼──────────────────┐
     │ Capture Test Data:             │
     │ • Pass/Fail Status             │
     │ • Screenshots                  │
     │ • Logs/Errors                  │
     └─────────────┬──────────────────┘
                   │
     ┌─────────────▼──────────────────┐
     │ Stop Driver & Cleanup          │
     └────────────────────────────────┘
```

## 6. Test Flow Steps (Example: Login Flow)

```
test-flows/login_flow_success.json
                    │
         ┌──────────▼──────────┐
         │ Step 1: Open App   │
         │ Status: Success    │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │ Step 2: Fill Email  │
         │ Status: Success    │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────────┐
         │ Step 3: Fill Password  │
         │ Status: Success        │
         └──────────┬──────────────┘
                    │
         ┌──────────▼──────────────┐
         │ Step 4: Click Login    │
         │ Status: Success        │
         └──────────┬──────────────┘
                    │
         ┌──────────▼──────────────┐
         │ Step 5: Dashboard      │
         │ Verified              │
         │ Status: Success        │
         └────────────────────────┘
```

## 7. Test Reporting & Result Generation

```
┌──────────────────────────────────────────┐
│       ALLURE REPORTING FRAMEWORK         │
└───────────────────┬──────────────────────┘
                    │
    ┌───────────────▼───────────────┐
    │ Test Results Collection       │
    │ allure-results/ directory     │
    │                              │
    │ Files:                        │
    │ • *.json (test results)       │
    │ • *-result.json               │
    │ • *-container.json            │
    │ • *-attachment.txt            │
    │   (screenshots & logs)        │
    └───────────────┬───────────────┘
                    │
    ┌───────────────▼───────────────┐
    │ Generate HTML Report         │
    │ allure-report/               │
    │ • app.js                      │
    │ • index.html                  │
    │ • favicon.ico                 │
    └───────────────┬───────────────┘
                    │
    ┌───────────────▼───────────────┐
    │ Display Report in Browser    │
    │ with Metrics:                 │
    │ • Pass/Fail Counts            │
    │ • Duration                    │
    │ • Screenshots                 │
    │ • Step Details                │
    └──────────────────────────────┘
```

## 8. WebSocket Real-time Status Updates

```
┌─────────────────────────────────────────┐
│       WEBSOCKET CONNECTION              │
│  ws://localhost:8000/ws/test-status    │
└──────────────┬──────────────────────────┘
               │
    ┌──────────▼──────────────────┐
    │ Frontend Connects           │
    │ (React useWebSocket hook)   │
    └──────────┬──────────────────┘
               │
    ┌──────────▼──────────────────┐
    │ Backend Maintains Broadcast│
    │ • Test started             │
    │ • Test step completed      │
    │ • Test passed/failed       │
    │ • Progress metrics         │
    │ • Resource usage           │
    └──────────┬──────────────────┘
               │
    ┌──────────▼──────────────────┐
    │ Frontend Updates UI Display │
    │ • Progress bars            │
    │ • Status indicators        │
    │ • Performance metrics      │
    │ • Line charts              │
    └────────────────────────────┘
```

## 9. Complete End-to-End Flow

```
USER INTERACTION
       │
       ▼
┌─────────────────────────────┐
│ 1. Frontend Selection       │
│    • Choose App Variant    │
│    • Select Module/Test    │
│    • Click Run Tests       │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 2. Send Request to Backend  │
│    POST /api/run-tests     │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 3. Backend Processing       │
│    • Download APK          │
│    • Setup Environment     │
│    • Connect Appium        │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 4. Execute Tests            │
│    • Run pytest             │
│    • Appium Commands        │
│    • Collect Results        │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 5. Stream Results           │
│    • WebSocket Updates      │
│    • Frontend Receives Data │
│    • Display Progress       │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 6. Generate Reports         │
│    • Allure Report Gen      │
│    • Result Analysis        │
│    • Suggestions/Failures   │
└─────────┬───────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ 7. Display Final Results    │
│    • Test Summary           │
│    • Pass/Fail Status       │
│    • Performance Metrics    │
│    • View Detailed Report   │
└─────────────────────────────┘
```

## 10. Project Structure Summary

```
test-automation-platform/
│
├── FRONTEND (React/Vite)
│   └── frontend/test-platform/
│       ├── src/
│       │   ├── App.jsx          (Main UI Component)
│       │   ├── App.css          (Styling)
│       │   ├── main.jsx         (Entry Point)
│       │   └── assets/          (Static Files)
│       ├── index.html           (HTML Template)
│       ├── package.json         (Dependencies)
│       └── vite.config.js       (Build Config)
│
├── BACKEND (FastAPI)
│   └── backend/
│       ├── server.py           (Main FastAPI App)
│       ├── gdrive_loader.py    (APK Download/Info)
│       └── static/             (Served Static Files)
│
├── TEST FRAMEWORK (Pytest + Appium)
│   └── tests/
│       ├── test_runner.py      (Test Orchestration)
│       ├── conftest.py         (Fixtures & Appium Setup)
│       ├── profiler.py         (Performance Profiling)
│       ├── locators/           (UI Element Locators)
│       │   ├── regular_client.json
│       │   └── regular_farmer.json
│       ├── test_cases/
│       │   ├── regular_farmer_test_cases/
│       │   │   ├── test_login_pytest.py
│       │   │   └── test_onboarding_pytest.py
│       │   └── regular_client_test_cases/
│       │       └── test_login_pytest.py
│       └── utils/
│           ├── ai_agent.py     (AI-powered Testing)
│           ├── ocr_utils.py    (Text Recognition)
│           ├── touch_utils.py  (Touch Interactions)
│           ├── wait_utils.py   (Waits & Delays)
│           ├── test_logger.py  (Logging)
│           └── test_flow_logger.py
│
├── TEST FLOWS
│   └── test-flows/
│       ├── login_flow_success.json
│       ├── onboarding_flow_success.json
│       └── farmer_flow_success.json
│
├── REPORTING
│   ├── allure-results/         (Test Result Data)
│   └── allure-report/          (HTML Reports)
│
└── CONFIGURATION
    ├── README.md
    ├── run_platform.sh         (Startup Script)
    └── .gitignore
```

## 11. Key Technologies & Stack

```
┌─────────────────────────────────────────────────────────┐
│                  TECHNOLOGY STACK                       │
├──────────────────┬──────────────────┬──────────────────┐
│    FRONTEND      │    BACKEND       │    TESTING       │
├──────────────────┼──────────────────┼──────────────────┤
│ • React          │ • FastAPI        │ • Pytest         │
│ • Vite           │ • WebSocket      │ • Appium         │
│ • Recharts       │ • Uvicorn        │ • UiAutomator2   │
│ • Lucide Icons   │ • CORS           │ • Allure         │
│ • React Hooks    │ • Pydantic       │ • Selenium       │
│                  │ • Google Drive   │                  │
│                  │   API            │                  │
└──────────────────┴──────────────────┴──────────────────┘
```

## 12. Data Flow Between Components

```
┌──────────────┐
│   FRONTEND   │
│   (React)    │
└──────┬───────┘
       │
       │ REST API + WebSocket
       │
┌──────▼───────────────┐
│   BACKEND            │
│   (FastAPI Server)   │
└──────┬───────────────┘
       │
       │ Subprocess calls
       │
┌──────▼───────────────────────┐
│   TEST RUNNER                │
│   (Pytest Process)           │
└──────┬───────────────────────┘
       │
       │ JDWP/Commands
       │
┌──────▼───────────────────────┐
│   APPIUM SERVER              │
│   + Android Emulator         │
└──────┬───────────────────────┘
       │
       │ UI Interactions
       │
┌──────▼───────────────────────┐
│   KRISHIVAAS APP (APK)       │
│   (Under Test)               │
└──────────────────────────────┘
```

---

**Summary**: This is a comprehensive mobile app test automation platform that allows testing multiple variants of the Krishivaas app (Farmer & Client apps in both regular and state versions). Tests are triggered from a React frontend, orchestrated by a FastAPI backend, executed via Pytest + Appium against the Android app, and results are reported through Allure with real-time WebSocket updates.
