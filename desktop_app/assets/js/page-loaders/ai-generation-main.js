(function () {
    'use strict';

    var shared = window.__pageLoaderShared;
    if (!shared) {
        throw new Error('page loader shared helpers not loaded');
    }

    var loaders = window._pageLoaders;
    var runtimeSummaryHandlers = window.__runtimeSummaryHandlers;
    if (!loaders || !runtimeSummaryHandlers) {
        throw new Error('page loader registries not loaded');
    }

    var _esc = shared.esc;

/* ══════════════════════════════════════════════
       AI Generation 页面
       ══════════════════════════════════════════════ */
    loaders['viral-title'] = function () {
        Promise.all([
            api.providers.list().catch(function () { return []; }),
        ]).then(function (results) {
            runtimeSummaryHandlers['viral-title']({ providers: results[0] || [] });
        });
        _loadAiGenerationPage({
            routeKey: 'viral-title',
            preset: 'title-generator',
            actionText: '生成标题方案',
            inputSelector: '#mainHost .title-editor-textarea',
            triggerSelectors: ['#mainHost .page-header .primary-button', '#mainHost .title-editor-actions .primary-button'],
            beforeCall: function (input) {
                return '请基于以下主题生成 3 个适合 TikTok Shop 的爆款标题方案，并简要说明适用场景：\n' + input;
            },
            renderResult: function (result, input) {
                var variants = _extractAiItems(result.content, 3);
                _renderVariantList('#mainHost .variant-list', variants, '方案');
                var metricCards = document.querySelectorAll('#mainHost .title-metric-grid .mini-metric-card');
                if (metricCards.length >= 3) {
                    metricCards[0].querySelector('strong').textContent = _calcTitleScore(variants[0] || input) + ' / 10';
                    metricCards[0].querySelector('small').textContent = '基于当前输出长度与钩子密度估算';
                    metricCards[1].querySelector('strong').textContent = String(Math.min(98, 72 + Math.max(0, result.total_tokens || 0) / 8)).slice(0, 2) + '%';
                    metricCards[1].querySelector('small').textContent = '供应商：' + (result.provider || '-');
                    metricCards[2].querySelector('strong').textContent = Math.min(99, 78 + variants.length * 5) + '%';
                    metricCards[2].querySelector('small').textContent = '耗时 ' + _formatElapsed(result.elapsed_ms) + ' / ' + (result.model || '-');
                }
                var textarea = document.querySelector('#mainHost .title-editor-textarea');
                if (textarea && variants[0]) textarea.value = variants[0];
            },
            bindExtra: function () {
                document.querySelectorAll('#mainHost .template-showcase-card').forEach(function (card) {
                    card.addEventListener('click', function () {
                        var templateName = extractTextFromEl(card, 'strong');
                        var textarea = document.querySelector('#mainHost .title-editor-textarea');
                        if (!textarea || !templateName) return;
                        textarea.value = templateName + '｜' + textarea.value;
                    });
                });
            },
        });
    };

    loaders['product-title'] = function () {
        Promise.all([
            api.providers.list().catch(function () { return []; }),
        ]).then(function (results) {
            runtimeSummaryHandlers['product-title']({ providers: results[0] || [] });
        });
        _loadAiGenerationPage({
            routeKey: 'product-title',
            preset: 'seo-optimizer',
            actionText: '优化商品标题',
            inputSelector: '#mainHost .product-input-row input',
            triggerSelectors: ['#mainHost .page-header .primary-button', '#mainHost .product-input-row .primary-button'],
            beforeCall: function (input) {
                return '请把以下商品标题优化为 2 个版本：高转化版和 SEO 版。要求保留核心品类词，并说明推荐场景。\n商品标题：' + input;
            },
            renderResult: function (result, input) {
                var variants = _extractAiItems(result.content, 2);
                _renderVariantList('#mainHost .product-result-board .variant-list', variants, ['高转化型', 'SEO 加强型']);
                var detailItems = document.querySelectorAll('#mainHost .product-insight-grid .detail-item strong');
                if (detailItems.length >= 3) {
                    var tokens = _keywordChunks(input);
                    detailItems[0].textContent = (tokens[0] || '核心词') + ' ' + _keywordDensity(input, tokens[0]) + '%';
                    detailItems[1].textContent = (tokens[1] || '属性词') + ' ' + _keywordDensity(input, tokens[1]) + '%';
                    detailItems[2].textContent = (tokens[2] || '修饰词') + ' ' + _keywordDensity(input, tokens[2]) + '%';
                }
            },
        });
    };

    loaders['ai-copywriter'] = function () {
        Promise.all([
            api.providers.list().catch(function () { return []; }),
        ]).then(function (results) {
            runtimeSummaryHandlers['ai-copywriter']({ providers: results[0] || [] });
        });
        _loadAiGenerationPage({
            routeKey: 'ai-copywriter',
            preset: 'copywriter',
            actionText: '生成营销文案',
            inputSelector: '#mainHost .copy-settings-column textarea',
            triggerSelectors: ['#mainHost .page-header .primary-button'],
            beforeCall: function (input) {
                var toneBtn = document.querySelector('#mainHost .copy-tone-list .is-active');
                var tone = toneBtn ? toneBtn.textContent.trim() : '专业严谨';
                return '请用“' + tone + '”语气，基于以下产品信息生成 3 个文案版本，并单独给出一条风险规避建议。\n' + input;
            },
            renderResult: function (result) {
                var variants = _extractAiItems(result.content, 3);
                _renderVariantList('#mainHost .copy-results-column .variant-list', variants, ['Variant 01', 'Variant 02', 'Variant 03']);
                _renderCompliance('#mainHost .copy-compliance-column', result.content);
            },
            bindExtra: function () {
                var buttons = document.querySelectorAll('#mainHost .copy-tone-list button');
                buttons.forEach(function (btn) {
                    btn.addEventListener('click', function () {
                        buttons.forEach(function (b) { b.classList.remove('is-active'); });
                        btn.classList.add('is-active');
                    });
                });
            },
        });
    };

    loaders['script-extractor'] = function () {
        Promise.all([
            api.providers.list().catch(function () { return []; }),
        ]).then(function (results) {
            runtimeSummaryHandlers['script-extractor']({ providers: results[0] || [] });
        });
        _loadAiGenerationPage({
            routeKey: 'script-extractor',
            preset: 'script-extractor',
            actionText: '提取脚本结构',
            inputSelector: '#mainHost .extractor-url-field input',
            triggerSelectors: ['#mainHost .page-header .primary-button'],
            beforeCall: function (input) {
                return '请基于以下视频链接或描述，输出脚本时间轴、结构标签和可复用结论。\n输入：' + input;
            },
            renderResult: function (result, input) {
                _renderExtractorResult(result.content);
                var progressText = document.querySelector('#mainHost .extractor-progress-row strong');
                if (progressText) progressText.textContent = '100%';
                var progressBar = document.querySelector('#mainHost .progress-bar span');
                if (progressBar) progressBar.style.width = '100%';
                var summary = document.querySelector('#mainHost .extractor-preview-column .panel p.subtle');
                if (summary) summary.textContent = '已完成结构提取：来源 ' + input + '，模型 ' + (result.model || '-') + '，总 tokens ' + (result.total_tokens || 0) + '。';
            },
        });
    };

    function _loadAiGenerationPage(config) {
        Promise.all([
            api.providers.list().catch(function () { return []; }),
            api.ai.usageToday().catch(function () { return []; }),
        ]).then(function (results) {
            _hydrateAiSelects(results[0] || []);
            _updateAiUsageHint(results[1] || []);
        });

        (config.triggerSelectors || []).forEach(function (selector) {
            _rewireElements(selector, function (btn) {
                btn.addEventListener('click', function () {
                    var inputEl = document.querySelector(config.inputSelector);
                    var input = inputEl ? String(inputEl.value || '').trim() : '';
                    _runAiGeneration(config, input, btn, null);
                });
            });
        });

        _rewireElements('#mainHost .page-header .secondary-button', function (btn) {
            btn.addEventListener('click', function () {
                var text = _collectAiResultText(config);
                if (!text) {
                    showToast('当前没有可复制内容', 'warning');
                    return;
                }
                if (api.utils && typeof api.utils.copyToClipboard === 'function') {
                    api.utils.copyToClipboard(text).then(function () {
                        showToast('结果已复制', 'success');
                    }).catch(function () {
                        showToast('复制失败，请重试', 'error');
                    });
                    return;
                }
                showToast('复制能力不可用', 'warning');
            });
        });

        _rewireElements('#mainHost .variant-card', function (card) {
            card.addEventListener('click', function () {
                document.querySelectorAll('#mainHost .variant-card').forEach(function (item) {
                    item.classList.remove('is-best');
                });
                card.classList.add('is-best');
                var text = extractTextFromEl(card, 'p');
                var target = document.querySelector(config.inputSelector);
                if (target && text) target.value = text;
                showToast('已应用该版本到编辑区', 'success');
            });
        });

        _rewireElements('#mainHost .js-ai-regen', function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var card = btn.closest('.variant-card');
                var seed = card ? extractTextFromEl(card, 'p') : '';
                _runAiGeneration(config, seed, btn, { diversify: true });
            });
        });

        _rewireElements('#mainHost .js-ai-apply-next', function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var card = btn.closest('.variant-card');
                var text = card ? extractTextFromEl(card, 'p') : '';
                if (!text) {
                    showToast('当前版本内容为空', 'warning');
                    return;
                }
                _applyAiResultToDownstream(config, text);
            });
        });

        if (typeof config.bindExtra === 'function') config.bindExtra();
    }

    function _runAiGeneration(config, input, btn, options) {
        var source = String(input || '').trim();
        if (!source) {
            showToast('请先填写生成内容', 'warning');
            return;
        }
        var originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = (options && options.diversify) ? '重算中…' : (config.actionText || '处理中…');
        var prompt = config.beforeCall ? config.beforeCall(source) : source;
        if (options && options.diversify) {
            prompt += '\n请基于同一主题输出全新角度，避免复用已有句式。';
        }
        api.ai.chat({
            preset: config.preset,
            model: _selectedModel(),
            messages: [{ role: 'user', content: prompt }],
            temperature: 0.7,
            max_tokens: 1200,
        }).then(function (result) {
            if (config.renderResult) config.renderResult(result || {}, source);
            showToast((options && options.diversify) ? '已生成同主题新版本' : '已生成最新结果', 'success');
            if (typeof bindRouteInteractions === 'function') bindRouteInteractions();
        }).catch(function (err) {
            showToast('生成失败: ' + err.message, 'error');
        }).finally(function () {
            btn.disabled = false;
            btn.textContent = originalText;
        });
    }

    function _applyAiResultToDownstream(config, text) {
        var map = {
            'viral-title': { route: 'creative-workshop', title: '标题方案下发', task_type: 'report' },
            'product-title': { route: 'creative-workshop', title: '商品标题下发', task_type: 'report' },
            'ai-copywriter': { route: 'ai-content-factory', title: '营销文案下发', task_type: 'publish' },
            'script-extractor': { route: 'video-editor', title: '脚本结构下发', task_type: 'publish' },
        };
        var target = map[config.routeKey] || { route: 'creative-workshop', title: 'AI 结果下发', task_type: 'report' };
        var payload = {
            sourceRoute: config.routeKey,
            targetRoute: target.route,
            text: text,
            createdAt: new Date().toISOString(),
        };
        window.localStorage.setItem('tkops.ai.handoff', JSON.stringify(payload));
        api.tasks.create({
            title: target.title,
            task_type: target.task_type,
            priority: 'high',
            status: 'pending',
            result_summary: text.slice(0, 160),
        }).catch(function () { return null; }).finally(function () {
            if (typeof renderRoute === 'function') renderRoute(target.route);
            showToast('已下发到 ' + target.route + '，可继续处理', 'success');
        });
    }

    function _collectAiResultText(config) {
        var selected = document.querySelector('#mainHost .variant-card.is-best p');
        if (selected && selected.textContent.trim()) return selected.textContent.trim();
        var first = document.querySelector('#mainHost .variant-card p');
        if (first && first.textContent.trim()) return first.textContent.trim();
        var inputEl = document.querySelector(config.inputSelector);
        if (inputEl && String(inputEl.value || '').trim()) return String(inputEl.value || '').trim();
        return '';
    }

    function _rewireElements(selector, binder) {
        document.querySelectorAll(selector).forEach(function (node) {
            var clone = node.cloneNode(true);
            node.parentNode.replaceChild(clone, node);
            binder(clone);
        });
    }

    function _hydrateAiSelects(providers) {
        var list = providers || [];
        var active = list.find(function (provider) {
            return provider.is_active === true || provider.is_active === 'True';
        }) || list[0] || null;
        var providerNames = list.map(function (provider) { return provider.name || '未命名供应商'; });
        var models = [];
        list.forEach(function (provider) {
            if (provider.default_model && models.indexOf(provider.default_model) === -1) {
                models.push(provider.default_model);
            }
        });
        if (!models.length && active && active.default_model) models.push(active.default_model);
        if (!models.length) models = ['GPT-4o'];

        document.querySelectorAll('#mainHost select, #detailHost select').forEach(function (select) {
            var label = _fieldLabel(select);
            if (label.indexOf('供应商') !== -1) {
                select.innerHTML = providerNames.length
                    ? providerNames.map(function (name) {
                        return '<option' + (active && active.name === name ? ' selected' : '') + '>' + _esc(name) + '</option>';
                    }).join('')
                    : '<option selected>未配置供应商</option>';
            }
            if (label.indexOf('模型') !== -1) {
                select.innerHTML = models.map(function (name, index) {
                    return '<option' + (index === 0 ? ' selected' : '') + '>' + _esc(name) + '</option>';
                }).join('');
            }
        });
    }

    function _updateAiUsageHint(rows) {
        var totalTokens = 0;
        (rows || []).forEach(function (row) {
            totalTokens += parseInt(row.total_tokens || row.total || 0, 10) || 0;
        });
        var detailItems = document.querySelectorAll('#detailHost .detail-item strong');
        if (detailItems.length >= 1 && totalTokens > 0) {
            detailItems[0].textContent = detailItems[0].textContent + ' / 今日 tokens ' + totalTokens;
        }
    }

    function _renderVariantList(selector, items, labels) {
        var host = document.querySelector(selector);
        if (!host) return;
        var toneList = ['success', 'info', 'warning'];
        var list = (items || []).filter(Boolean);
        if (!list.length) list = ['暂无可展示结果'];
        host.innerHTML = list.map(function (item, index) {
            var tag = Array.isArray(labels)
                ? (labels[index] || ('Variant ' + (index + 1)))
                : ((labels || 'Variant') + ' ' + String.fromCharCode(65 + index));
            return '<article class="variant-card' + (index === 0 ? ' is-best' : '') + '">' 
                + '<div class="variant-card__head"><span class="pill ' + toneList[index % toneList.length] + '">' + _esc(tag) + '</span><strong>' + (index === 0 ? '推荐采用' : '候选版本') + '</strong></div>'
                + '<p>' + _esc(item) + '</p>'
                + '<div class="detail-actions"><button class="ghost-button js-ai-regen" type="button">同主题重算</button><button class="secondary-button js-ai-apply-next" type="button">下发到下游</button></div>'
                + '<small>' + (index === 0 ? '当前结果已按最新输入刷新。' : '可用于补充测试与渠道分发。') + '</small></article>';
        }).join('');
    }

    function _renderCompliance(selector, text) {
        var root = document.querySelector(selector);
        if (!root) return;
        var scoreCard = root.querySelector('.copy-score-card strong');
        var scoreNote = root.querySelector('.copy-score-card small');
        var riskStrong = root.querySelectorAll('.metric-kv .detail-item strong');
        var flagged = _detectRiskWords(text);
        var score = Math.max(48, 94 - flagged.length * 14);
        if (scoreCard) scoreCard.textContent = score;
        if (scoreNote) scoreNote.textContent = score >= 85 ? '低风险' : score >= 70 ? '中等风险' : '高风险';
        if (riskStrong.length >= 2) {
            riskStrong[0].textContent = flagged.length;
            riskStrong[1].textContent = Math.max(0, Math.min(3, flagged.length + 1));
        }
        var list = root.querySelector('.workbench-side-list');
        if (list) {
            list.innerHTML = (flagged.length ? flagged : ['当前输出未发现明显高风险词']).map(function (word) {
                return '<article class="workbench-sidecard"><strong>' + _esc(word === '当前输出未发现明显高风险词' ? word : ('风险词：' + word)) + '</strong><div class="subtle">'
                    + (word === '当前输出未发现明显高风险词' ? '建议继续人工复核利益承诺和绝对化表达。' : '建议替换为更稳妥的中性表达，再进入投放。')
                    + '</div></article>';
            }).join('');
        }
    }

    function _renderExtractorResult(text) {
        var host = document.querySelector('#mainHost .extractor-result-table');
        if (!host) return;
        var rows = _extractAiItems(text, 6);
        host.innerHTML = rows.map(function (row, index) {
            var match = row.match(new RegExp('(\\d{2}:\\d{2}:\\d{2})'));
            var ts = match ? match[1] : ('00:00:' + String(12 + index * 8).padStart(2, '0'));
            var cleaned = row
                .replace(new RegExp('(\\d{2}:\\d{2}:\\d{2})'), '')
                .replace(new RegExp('^[-*•\\d\\.\\)\\s]+'), '')
                .trim();
            return '<div class="extractor-result-row"><span>' + _esc(ts) + '</span><div><strong>' + (cleaned.indexOf('CTA') !== -1 ? '[CTA]' : cleaned.indexOf('镜头') !== -1 ? '[视觉描述]' : '[脚本结构]') + '</strong><p>' + _esc(cleaned) + '</p></div><em>' + (96 - index * 2) + '%</em></div>';
        }).join('');
    }

    function _extractAiItems(text, limit) {
        var cleaned = String(text || '')
            .split(new RegExp('\\n+'))
            .map(function (line) { return line.replace(new RegExp('^[-*•\\d\\.\\)\\s]+'), '').trim(); })
            .filter(function (line) { return line && line.length >= 6; });
        if (!cleaned.length) return [String(text || '').trim()];
        return cleaned.slice(0, limit || 3);
    }

    function _selectedModel() {
        var modelSelect = null;
        document.querySelectorAll('#mainHost select, #detailHost select').forEach(function (select) {
            if (!modelSelect && _fieldLabel(select).indexOf('模型') !== -1) modelSelect = select;
        });
        return modelSelect ? modelSelect.value : null;
    }

    function _fieldLabel(node) {
        var field = node.closest('.form-field, .config-field');
        var label = field ? field.querySelector('label, .config-field__label') : null;
        return label ? label.textContent.trim() : '';
    }

    function _calcTitleScore(text) {
        var value = String(text || '');
        var score = 6.8;
        if (value.indexOf('!') !== -1 || value.indexOf('！') !== -1) score += 0.6;
        if (new RegExp('\\d').test(value)) score += 0.8;
        if (value.length >= 16 && value.length <= 28) score += 1.1;
        if (new RegExp('为什么|只有|别再|立即|揭秘|必看').test(value)) score += 0.5;
        return Math.min(9.8, Math.round(score * 10) / 10);
    }

    function _keywordChunks(text) {
        var parts = String(text || '').split(new RegExp('[\\s\\-_/【】\\[\\]，,。]+')).filter(Boolean);
        if (parts.length >= 3) return parts.slice(0, 3);
        return [String(text || '').slice(0, 4), String(text || '').slice(4, 8), String(text || '').slice(8, 12)].filter(Boolean);
    }

    function _keywordDensity(text, token) {
        if (!text || !token) return '0.0';
        var total = String(text).length || 1;
        var count = String(text).split(token).length - 1;
        return ((count * token.length / total) * 100).toFixed(1);
    }

    function _detectRiskWords(text) {
        var source = String(text || '');
        var patterns = ['最强', '第一', '稳赚', '赚钱', '100%', '绝对', '永久', '包过'];
        return patterns.filter(function (word) { return source.indexOf(word) !== -1; });
    }

    function _formatElapsed(ms) {
        var n = parseInt(ms || 0, 10) || 0;
        if (n < 1000) return n + 'ms';
        return (n / 1000).toFixed(1) + 's';
    }
})();
