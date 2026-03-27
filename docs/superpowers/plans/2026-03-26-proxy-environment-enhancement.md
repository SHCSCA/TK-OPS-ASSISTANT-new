# Proxy Environment Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade device environment launch to use a proxy self-check page, support authenticated proxy formats, and keep the browser profile isolated and verifiable.

**Architecture:** The backend service will resolve and validate proxy configuration, build a local self-check launcher page inside the device profile directory, and launch the browser against that launcher instead of opening TikTok directly. The self-check page will show the configured proxy, the actual startup proxy, the current egress IP, and clear failure reasons, then gate the TikTok tab behind a verified proxy state. Authenticated proxies will be handled by a local loopback helper proxy so credentials never need to be passed on the browser command line.

**Tech Stack:** Python 3.11, stdlib networking, SQLAlchemy models/services, PySide6 bridge slots, vanilla HTML/CSS/JS, pytest.

---

### Task 1: Proxy Parsing and Local Launcher

**Files:**
- Modify: `desktop_app/services/account_service.py`
- Test: `tests/test_backend_entities.py`

- [ ] **Step 1: Write the failing test**

```python
def test_open_device_environment_supports_authenticated_proxy_and_launcher_page():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `venv\Scripts\python.exe -m pytest tests/test_backend_entities.py::test_open_device_environment_supports_authenticated_proxy_and_launcher_page -v`
Expected: FAIL because authenticated proxy handling and launcher validation are not complete.

- [ ] **Step 3: Write minimal implementation**

```python
def _parse_proxy_url(raw: str) -> dict[str, str]:
    ...

def open_device_environment(...):
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `venv\Scripts\python.exe -m pytest tests/test_backend_entities.py::test_open_device_environment_supports_authenticated_proxy_and_launcher_page -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add desktop_app/services/account_service.py tests/test_backend_entities.py
git commit -m "feat: add proxy launcher and auth proxy parsing"
```

### Task 2: Self-Check Page and Bridge Exposure

**Files:**
- Modify: `desktop_app/ui/bridge.py`
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/js/data.js`
- Modify: `desktop_app/assets/js/bridge.js`
- Test: `tests/test_task_backed_actions.py`
- Test: `tests/test_bridge_runtime_contract.py`

- [ ] **Step 1: Write the failing test**

```python
def test_device_page_routes_environment_actions_to_runtime_hooks():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `venv\Scripts\python.exe -m pytest tests/test_task_backed_actions.py::test_device_page_routes_environment_actions_to_runtime_hooks -v`
Expected: FAIL until launcher hooks and runtime payload fields are updated.

- [ ] **Step 3: Write minimal implementation**

```python
@Slot(int, result=str)
def openDeviceEnvironment(self, pk: int) -> str:
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `venv\Scripts\python.exe -m pytest tests/test_task_backed_actions.py::test_device_page_routes_environment_actions_to_runtime_hooks -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add desktop_app/ui/bridge.py desktop_app/assets/js/page-loaders.js desktop_app/assets/js/data.js desktop_app/assets/js/bridge.js tests/test_task_backed_actions.py tests/test_bridge_runtime_contract.py
git commit -m "feat: enhance device proxy self-check launcher"
```

### Task 3: Verification Sweep

**Files:**
- Test: `tests/test_backend_entities.py`
- Test: `tests/test_task_backed_actions.py`
- Test: `tests/test_bridge_runtime_contract.py`

- [ ] **Step 1: Run targeted tests**

Run: `venv\Scripts\python.exe -m pytest tests/test_backend_entities.py tests/test_task_backed_actions.py tests/test_bridge_runtime_contract.py -v`
Expected: PASS

- [ ] **Step 2: Run launch check**

Run: `venv\Scripts\python.exe desktop_app\main.py`
Expected: App starts and the launcher path resolves without runtime errors.

- [ ] **Step 3: Commit**

```bash
git add tests/test_backend_entities.py tests/test_task_backed_actions.py tests/test_bridge_runtime_contract.py
git commit -m "test: cover device proxy launcher flow"
```
