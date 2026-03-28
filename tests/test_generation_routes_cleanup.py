from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATION_JS = ROOT / "desktop_app" / "assets" / "js" / "factories" / "generation.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
AI_GENERATION_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "ai-generation-main.js"
APP_SHELL_HTML = ROOT / "desktop_app" / "assets" / "app_shell.html"


def _load_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


class TestViralTitleCleanup:
    def test_no_hardcoded_viral_title_examples(self) -> None:
        text = _load_text(GENERATION_JS)
        idx = text.find("function makeViralTitleRoute()")
        end = text.find("function makeScriptExtractorRoute()", idx)
        section = text[idx:end]
        forbidden = [
            "只有 1% 的人知道的理财秘籍",
            "别再盲目理财了",
            "看完这套方法，你会重新理解",
            "预期 CTR 4.8%",
            "预期 CTR 3.2%",
            "预期 CTR 3.9%",
            "92% 成功率",
            "88% 成功率",
            "85% 成功率",
            "8.4 / 10",
            "击败 94% 同类标题",
        ]
        for marker in forbidden:
            assert marker not in section, f"found hardcoded prototype content: {marker}"

    def test_viral_title_uses_placeholder_metrics(self) -> None:
        text = _load_text(GENERATION_JS)
        idx = text.find("function makeViralTitleRoute()")
        end = text.find("function makeScriptExtractorRoute()", idx)
        section = text[idx:end]
        assert "--" in section, "placeholder metrics should be present"

    def test_viral_title_loader_moved_to_split_module(self) -> None:
        root_text = _load_text(PAGE_LOADERS_JS)
        split_text = _load_text(AI_GENERATION_MAIN_JS)
        assert "loaders['viral-title']" not in root_text, \
            "viral-title loader should move out of root page-loaders.js"
        assert "loaders['viral-title']" in split_text, \
            "viral-title loader should live in ai-generation-main.js"
        assert "runtimeSummaryHandlers['viral-title']" in split_text, \
            "viral-title loader should still call runtimeSummaryHandlers"

    def test_viral_title_page_audit_registered(self) -> None:
        text = _load_text(PAGE_LOADERS_JS)
        idx = text.find("pageAudits = ")
        assert "'viral-title'" in text[idx:idx + 5000], \
            "viral-title should have a pageAudit entry"


class TestScriptExtractorCleanup:
    def test_no_hardcoded_script_extractor_examples(self) -> None:
        text = _load_text(GENERATION_JS)
        idx = text.find("function makeScriptExtractorRoute()")
        end = text.find("function makeProductTitleRoute()", idx)
        section = text[idx:end]
        forbidden = [
            "https://example.com/video/viral-case",
            "第 124 / 300 帧",
            "02:45",
            "01:12",
            "高效生产力指南",
            "番茄钟示例",
            "主讲人出现在镜头中央",
        ]
        for marker in forbidden:
            assert marker not in section, f"found hardcoded prototype content: {marker}"

    def test_script_extractor_loader_moved_to_split_module(self) -> None:
        root_text = _load_text(PAGE_LOADERS_JS)
        split_text = _load_text(AI_GENERATION_MAIN_JS)
        assert "loaders['script-extractor']" not in root_text, \
            "script-extractor loader should move out of root page-loaders.js"
        assert "loaders['script-extractor']" in split_text, \
            "script-extractor loader should live in ai-generation-main.js"
        assert "runtimeSummaryHandlers['script-extractor']" in split_text, \
            "script-extractor loader should still call runtimeSummaryHandlers"

    def test_script_extractor_page_audit_registered(self) -> None:
        text = _load_text(PAGE_LOADERS_JS)
        idx = text.find("pageAudits = ")
        assert "'script-extractor'" in text[idx:idx + 5000], \
            "script-extractor should have a pageAudit entry"


class TestProductTitleCleanup:
    def test_no_hardcoded_product_title_examples(self) -> None:
        text = _load_text(GENERATION_JS)
        idx = text.find("function makeProductTitleRoute()")
        end = text.find("function makeAICopywriterRoute()", idx)
        section = text[idx:end]
        forbidden = [
            "夏季新款纯棉短袖T恤男装韩版潮牌",
            "国潮重磅纯棉短袖T恤男宽松百搭体恤",
            "简约基础款圆领纯棉短袖T恤",
            "纯棉T恤 2.4%",
            "夏季新款 1.8%",
            "韩版潮流 0.5%",
            "100%纯棉",
            "124 小时",
        ]
        for marker in forbidden:
            assert marker not in section, f"found hardcoded prototype content: {marker}"

    def test_product_title_loader_moved_to_split_module(self) -> None:
        root_text = _load_text(PAGE_LOADERS_JS)
        split_text = _load_text(AI_GENERATION_MAIN_JS)
        assert "loaders['product-title']" not in root_text, \
            "product-title loader should move out of root page-loaders.js"
        assert "loaders['product-title']" in split_text, \
            "product-title loader should live in ai-generation-main.js"
        assert "runtimeSummaryHandlers['product-title']" in split_text, \
            "product-title loader should still call runtimeSummaryHandlers"

    def test_product_title_page_audit_registered(self) -> None:
        text = _load_text(PAGE_LOADERS_JS)
        idx = text.find("pageAudits = ")
        assert "'product-title'" in text[idx:idx + 5000], \
            "product-title should have a pageAudit entry"


class TestAICopywriterCleanup:
    def test_no_hardcoded_ai_copywriter_examples(self) -> None:
        text = _load_text(GENERATION_JS)
        idx = text.find("function makeAICopywriterRoute()")
        end = text.find("function makeAIContentFactoryRoute()", idx)
        section = text[idx:end]
        forbidden = [
            "这款划时代的智能助手",
            "让你的工作效率瞬间翻倍",
            "告别繁琐，极简主义者",
            "全网最强性能",
            "首批用户体验报告",
            "72",
            "中等风险",
            "Anthropic / Claude 3.7 Sonnet",
        ]
        for marker in forbidden:
            assert marker not in section, f"found hardcoded prototype content: {marker}"

    def test_ai_copywriter_loader_moved_to_split_module(self) -> None:
        root_text = _load_text(PAGE_LOADERS_JS)
        split_text = _load_text(AI_GENERATION_MAIN_JS)
        assert "loaders['ai-copywriter']" not in root_text, \
            "ai-copywriter loader should move out of root page-loaders.js"
        assert "loaders['ai-copywriter']" in split_text, \
            "ai-copywriter loader should live in ai-generation-main.js"
        assert "runtimeSummaryHandlers['ai-copywriter']" in split_text, \
            "ai-copywriter loader should still call runtimeSummaryHandlers"

    def test_ai_copywriter_page_audit_registered(self) -> None:
        text = _load_text(PAGE_LOADERS_JS)
        idx = text.find("pageAudits = ")
        assert "'ai-copywriter'" in text[idx:idx + 5000], \
            "ai-copywriter should have a pageAudit entry"


class TestGenerationPageAudits:
    def test_all_four_generation_routes_have_runtime_handlers(self) -> None:
        text = _load_text(PAGE_LOADERS_JS)
        for route in ['viral-title', 'script-extractor', 'product-title', 'ai-copywriter']:
            assert f"'{route}': function (payload)" in text, \
                f"{route} should have a runtimeSummaryHandler"

    def test_all_four_generation_routes_have_page_audit_entries(self) -> None:
        text = _load_text(PAGE_LOADERS_JS)
        audits_start = text.find("pageAudits = ")
        audits_section = text[audits_start:audits_start + 5000]
        for route in ['viral-title', 'script-extractor', 'product-title', 'ai-copywriter']:
            assert f"'{route}':" in audits_section, \
                f"{route} should have a pageAudit entry"

    def test_generation_helpers_move_out_of_root_page_loader(self) -> None:
        root_text = _load_text(PAGE_LOADERS_JS)
        split_text = _load_text(AI_GENERATION_MAIN_JS)
        helper_defs = [
            'function _loadAiGenerationPage(config)',
            'function _runAiGeneration(config, input, btn, options)',
            'function _applyAiResultToDownstream(config, text)',
            'function _collectAiResultText(config)',
            'function _hydrateAiSelects(providers)',
            'function _updateAiUsageHint(rows)',
            'function _renderVariantList(selector, items, labels)',
            'function _renderCompliance(selector, text)',
            'function _renderExtractorResult(text)',
            'function _extractAiItems(text, limit)',
            'function _calcTitleScore(text)',
            'function _keywordChunks(text)',
            'function _keywordDensity(text, token)',
            'function _detectRiskWords(text)',
            'function _formatElapsed(ms)',
        ]
        for marker in helper_defs:
            assert marker not in root_text, f"generation helper should leave root file: {marker}"
            assert marker in split_text, f"generation helper should exist in split module: {marker}"

    def test_app_shell_loads_split_generation_module_after_root_loader(self) -> None:
        text = _load_text(APP_SHELL_HTML)
        root_idx = text.find('./js/page-loaders.js')
        split_idx = text.find('./js/page-loaders/ai-generation-main.js')
        main_idx = text.find('./js/main.js')
        assert root_idx != -1, "app_shell should load root page-loaders.js"
        assert split_idx != -1, "app_shell should load ai-generation-main.js"
        assert main_idx != -1, "app_shell should load main.js"
        assert root_idx < split_idx < main_idx, \
            "ai-generation-main.js should load after page-loaders.js and before main.js"
