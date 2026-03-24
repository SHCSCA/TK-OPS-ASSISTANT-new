"""Phase 8 AI Integration — E2E Tests.

Validates:
  1. Import chain integrity
  2. Presets system
  3. ChatService structure (no live API)
  4. UsageTracker persistence
  5. Bridge slot existence
  6. JS file syntax balance (braces, parens, brackets)
"""
import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Force temp DB for tests
os.environ.setdefault("TK_OPS_DATA_DIR", tempfile.mkdtemp())


class Test01_Imports(unittest.TestCase):
    def test_chat_service(self):
        from desktop_app.services.chat_service import (
            ChatService, ChatMessage, ChatResult, StreamChunk,
            list_presets, get_preset, PRESETS, _build_client,
        )
        self.assertTrue(callable(ChatService))
        self.assertTrue(callable(_build_client))

    def test_usage_tracker(self):
        from desktop_app.services.usage_tracker import UsageTracker
        self.assertTrue(callable(UsageTracker))

    def test_bridge(self):
        from desktop_app.ui.bridge import Bridge
        self.assertTrue(callable(Bridge))

    def test_database_honors_tk_ops_data_dir_override(self):
        temp_dir = tempfile.mkdtemp()
        env = os.environ.copy()
        env["TK_OPS_DATA_DIR"] = temp_dir
        output = subprocess.check_output(
            [
                sys.executable,
                "-c",
                "import desktop_app.database as db; print(db.DB_PATH)",
            ],
            cwd=str(ROOT),
            env=env,
            text=True,
            stderr=subprocess.STDOUT,
        )
        db_path = Path(output.strip().splitlines()[-1])
        self.assertEqual(db_path, Path(temp_dir) / "tk_ops.db")


class Test02_Presets(unittest.TestCase):
    def test_list_presets_count(self):
        from desktop_app.services.chat_service import list_presets
        presets = list_presets()
        self.assertEqual(len(presets), 9)

    def test_list_presets_keys(self):
        from desktop_app.services.chat_service import list_presets
        keys = {p["key"] for p in list_presets()}
        expected = {"default", "title-generator", "copywriter", "script-extractor",
                    "reply-bot", "data-analyst", "content-planner", "seo-optimizer",
                    "competitor-analyst"}
        self.assertEqual(keys, expected)

    def test_each_preset_has_fields(self):
        from desktop_app.services.chat_service import list_presets
        for p in list_presets():
            self.assertIn("key", p)
            self.assertIn("name", p)
            self.assertIn("icon", p)
            self.assertIn("system", p)
            self.assertIsInstance(p["system"], str)
            self.assertGreater(len(p["system"]), 10)

    def test_get_preset_found(self):
        from desktop_app.services.chat_service import get_preset
        p = get_preset("title-generator")
        self.assertIsNotNone(p)
        self.assertEqual(p["name"], "爆款标题大师")

    def test_get_preset_missing(self):
        from desktop_app.services.chat_service import get_preset
        self.assertIsNone(get_preset("nonexistent"))


class Test03_ChatService(unittest.TestCase):
    def test_no_providers_returns_fallback(self):
        from desktop_app.services.chat_service import ChatService
        svc = ChatService()
        result = svc.chat([{"role": "user", "content": "hello"}])
        self.assertIn("未配置", result.content)
        self.assertTrue(result.finished)

    def test_inject_preset(self):
        from desktop_app.services.chat_service import ChatService
        msgs = [{"role": "user", "content": "hi"}]
        out = ChatService._inject_preset(msgs, "default")
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["role"], "system")

    def test_inject_preset_no_duplicate(self):
        from desktop_app.services.chat_service import ChatService
        msgs = [{"role": "system", "content": "custom"}, {"role": "user", "content": "hi"}]
        out = ChatService._inject_preset(msgs, "default")
        self.assertEqual(len(out), 2)  # should NOT prepend

    def test_inject_preset_none(self):
        from desktop_app.services.chat_service import ChatService
        msgs = [{"role": "user", "content": "hi"}]
        out = ChatService._inject_preset(msgs, None)
        self.assertEqual(len(out), 1)

    def test_stream_no_providers(self):
        from desktop_app.services.chat_service import ChatService
        svc = ChatService()
        chunks = list(svc.chat_stream([{"role": "user", "content": "hello"}]))
        self.assertEqual(len(chunks), 1)
        self.assertTrue(chunks[0].done)
        self.assertIn("未配置", chunks[0].delta)


class Test04_UsageTracker(unittest.TestCase):
    def test_record_and_retrieve(self):
        from desktop_app.services.usage_tracker import UsageTracker
        tracker = UsageTracker()
        before = tracker.get_stats()["total"].get("prompt", 0)
        tracker.record("TestProvider", "gpt-4o-mini", 100, 50)
        stats = tracker.get_stats()
        self.assertEqual(stats["total"]["prompt"], before + 100)
        self.assertGreater(stats["total"]["requests"], 0)

    def test_get_today(self):
        from desktop_app.services.usage_tracker import UsageTracker
        tracker = UsageTracker()
        tracker.record("TestP", "model", 10, 5)
        today = tracker.get_today()
        self.assertGreaterEqual(today["prompt"], 10)

    def test_accumulate(self):
        from desktop_app.services.usage_tracker import UsageTracker
        tracker = UsageTracker()
        tracker.record("P1", "m1", 100, 50)
        tracker.record("P1", "m1", 200, 100)
        stats = tracker.get_stats()
        self.assertGreaterEqual(stats["total"]["prompt"], 300)
        self.assertGreaterEqual(stats["total"]["requests"], 2)


class Test05_BridgeSlots(unittest.TestCase):
    def test_bridge_has_ai_slots(self):
        from desktop_app.ui.bridge import Bridge
        expected_methods = [
            "chatSync", "startChatStream", "pollChatStream",
            "listAiPresets", "getAiPreset", "testAiProvider",
            "getAiUsageStats", "getAiUsageToday",
        ]
        for name in expected_methods:
            self.assertTrue(hasattr(Bridge, name), f"Bridge missing slot: {name}")

    def test_list_presets_slot(self):
        from desktop_app.ui.bridge import Bridge
        b = Bridge()
        raw = b.listAiPresets()
        data = json.loads(raw)
        self.assertTrue(data["ok"])
        self.assertEqual(len(data["data"]), 9)

    def test_get_preset_slot(self):
        from desktop_app.ui.bridge import Bridge
        b = Bridge()
        raw = b.getAiPreset("copywriter")
        data = json.loads(raw)
        self.assertTrue(data["ok"])
        self.assertEqual(data["data"]["name"], "AI 文案师")

    def test_get_preset_slot_missing(self):
        from desktop_app.ui.bridge import Bridge
        b = Bridge()
        raw = b.getAiPreset("nope")
        data = json.loads(raw)
        self.assertFalse(data["ok"])

    def test_usage_stats_slot(self):
        from desktop_app.ui.bridge import Bridge
        b = Bridge()
        raw = b.getAiUsageStats()
        data = json.loads(raw)
        self.assertTrue(data["ok"])
        self.assertIn("total", data["data"])

    def test_poll_empty(self):
        from desktop_app.ui.bridge import Bridge
        b = Bridge()
        raw = b.pollChatStream()
        data = json.loads(raw)
        self.assertTrue(data["ok"])
        self.assertTrue(data["data"]["finished"])

    def test_bridge_stub_has_runtime_methods(self):
        bridge_js = (ROOT / "desktop_app" / "assets" / "js" / "bridge.js").read_text(encoding="utf-8")
        expected_stub_methods = [
            "listAssetsByType:",
            "getAssetStats:",
            "chatSync:",
            "startChatStream:",
            "pollChatStream:",
            "listAiPresets:",
            "getAiPreset:",
            "testAiProvider:",
            "getAiUsageStats:",
            "getAiUsageToday:",
        ]
        for method in expected_stub_methods:
            self.assertIn(method, bridge_js)


class Test06_JsSyntax(unittest.TestCase):
    """Check brace/paren/bracket balance in modified JS files."""

    JS_FILES = [
        "desktop_app/assets/js/data.js",
        "desktop_app/assets/js/ui-aichat.js",
        "desktop_app/assets/js/main.js",
    ]

    def _check_balance(self, filepath):
        full = ROOT / filepath
        content = full.read_text(encoding="utf-8")
        content = content.replace("&quot;", '"').replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        pairs = {"{": "}", "(": ")", "[": "]"}
        stack = []
        i = 0
        length = len(content)
        while i < length:
            ch = content[i]
            # Skip block comments /* ... */
            if ch == '/' and i + 1 < length and content[i + 1] == '*':
                i = content.find('*/', i + 2)
                i = i + 2 if i >= 0 else length
                continue
            # Skip line comments // ...
            if ch == '/' and i + 1 < length and content[i + 1] == '/':
                i = content.find('\n', i + 2)
                i = i + 1 if i >= 0 else length
                continue
            # Skip strings
            if ch in ('"', "'", '`'):
                quote = ch
                i += 1
                while i < length:
                    if content[i] == '\\':
                        i += 2
                        continue
                    if content[i] == quote:
                        break
                    i += 1
                i += 1
                continue
            if ch in pairs:
                stack.append(pairs[ch])
            elif ch in pairs.values():
                if not stack or stack[-1] != ch:
                    return False, f"Unmatched '{ch}'"
                stack.pop()
            i += 1
        if stack:
            return False, f"Unclosed: {stack}"
        return True, "OK"

    def test_js_files_balanced(self):
        for f in self.JS_FILES:
            ok, msg = self._check_balance(f)
            self.assertTrue(ok, f"{f}: {msg}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
