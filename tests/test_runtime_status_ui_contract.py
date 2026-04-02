from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS_BAR_VUE = ROOT / "apps" / "desktop" / "src" / "layouts" / "StatusBar.vue"


def test_status_bar_consumes_runtime_socket_state() -> None:
    text = STATUS_BAR_VUE.read_text(encoding="utf-8")

    assert "createRuntimeSocket" in text
    assert "runtimeLabel" in text
    assert "runtimeVersion" in text
    assert "onMounted" in text
    assert "onBeforeUnmount" in text
