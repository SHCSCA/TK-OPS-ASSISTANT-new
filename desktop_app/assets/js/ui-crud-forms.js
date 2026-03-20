/* ── ui-crud-forms.js ─ CRUD 表单定义 ─────────────
   为 Account / Task / AIProvider / Group / Device
   提供 openXxxForm() 全局方法，内部使用 openModal()。
   ──────────────────────────────────────────────── */
(function () {
    'use strict';

    /* ══════════════════════════════════════════════
       Account 创建/编辑
       ══════════════════════════════════════════════ */
    function openAccountForm(existing) {
        var isEdit = !!(existing && existing.id);
        // 拉分组列表做下拉选项
        api.groups.list().then(function (groups) {
            groups = groups || [];
            var groupOpts = [{ value: '', label: '-- 不分组 --' }];
            groups.forEach(function (g) {
                groupOpts.push({ value: String(g.id), label: g.name });
            });

            openModal({
                title: isEdit ? '编辑账号' : '新建账号',
                width: 500,
                submitText: isEdit ? '保存修改' : '创建账号',
                fields: [
                    { key: 'username', label: '用户名', required: true, placeholder: '例如 TK_User_US_01',
                      value: existing ? existing.username : '', disabled: isEdit },
                    { key: 'platform', label: '平台', type: 'select', value: existing ? existing.platform : 'tiktok',
                      options: ['tiktok', 'tiktok_shop', 'instagram', 'youtube'] },
                    { key: 'region', label: '地区', type: 'select', value: existing ? existing.region : 'US',
                      options: ['US', 'UK', 'DE', 'JP', 'MY', 'ID', 'TH', 'VN', 'PH', 'BR', 'MX'] },
                    { key: 'status', label: '状态', type: 'select', value: existing ? existing.status : 'active',
                      options: [
                          { value: 'active', label: '活跃' },
                          { value: 'suspended', label: '封禁' },
                          { value: 'warming', label: '养号中' },
                          { value: 'idle', label: '闲置' },
                      ] },
                    { key: 'group_id', label: '所属分组', type: 'select', value: existing ? String(existing.group_id || '') : '',
                      options: groupOpts },
                    { key: 'followers', label: '粉丝数', type: 'number', value: existing ? existing.followers : 0, min: 0 },
                    { key: 'notes', label: '备注', type: 'textarea', placeholder: '可选描述',
                      value: existing ? existing.notes : '' },
                ],
                onSubmit: function (data) {
                    // 清理空字符串 group_id
                    if (data.group_id === '') { data.group_id = null; }
                    else { data.group_id = parseInt(data.group_id, 10); }
                    data.followers = parseInt(data.followers, 10) || 0;

                    if (isEdit) {
                        delete data.username; // username 不可改
                        return api.accounts.update(existing.id, data).then(function () {
                            showToast('账号已更新', 'success');
                        });
                    } else {
                        return api.accounts.create(data).then(function () {
                            showToast('账号已创建', 'success');
                        });
                    }
                },
            });
        });
    }

    /* ══════════════════════════════════════════════
       Task 创建/编辑
       ══════════════════════════════════════════════ */
    function openTaskForm(existing) {
        var isEdit = !!(existing && existing.id);
        // 拉账号列表做关联
        api.accounts.list().then(function (accounts) {
            accounts = accounts || [];
            var accountOpts = [{ value: '', label: '-- 不关联账号 --' }];
            accounts.forEach(function (a) {
                accountOpts.push({ value: String(a.id), label: a.username + ' (' + (a.platform || '') + ')' });
            });

            openModal({
                title: isEdit ? '编辑任务' : '新建任务',
                width: 500,
                submitText: isEdit ? '保存修改' : '创建任务',
                fields: [
                    { key: 'title', label: '任务标题', required: true, placeholder: '例如 自动回复批次 #13',
                      value: existing ? existing.title : '' },
                    { key: 'task_type', label: '任务类型', type: 'select',
                      value: existing ? existing.task_type : 'publish',
                      options: [
                          { value: 'publish', label: '发布' },
                          { value: 'interact', label: '互动' },
                          { value: 'scrape', label: '数据采集' },
                          { value: 'report', label: '报告生成' },
                          { value: 'maintenance', label: '系统维护' },
                      ] },
                    { key: 'priority', label: '优先级', type: 'select',
                      value: existing ? existing.priority : 'medium',
                      options: [
                          { value: 'urgent', label: '紧急' },
                          { value: 'high', label: '高' },
                          { value: 'medium', label: '中' },
                          { value: 'low', label: '低' },
                      ] },
                    { key: 'account_id', label: '关联账号', type: 'select',
                      value: existing ? String(existing.account_id || '') : '',
                      options: accountOpts },
                    { key: 'result_summary', label: '备注 / 结果摘要', type: 'textarea',
                      placeholder: '可选', value: existing ? existing.result_summary : '' },
                ],
                onSubmit: function (data) {
                    if (data.account_id === '') { data.account_id = null; }
                    else { data.account_id = parseInt(data.account_id, 10); }

                    if (isEdit) {
                        return api.tasks.update(existing.id, data).then(function () {
                            showToast('任务已更新', 'success');
                        });
                    } else {
                        return api.tasks.create(data).then(function () {
                            showToast('任务已创建', 'success');
                        });
                    }
                },
            });
        });
    }

    /* ══════════════════════════════════════════════
       AI Provider 创建/编辑
       ══════════════════════════════════════════════ */
    function openProviderForm(existing) {
        var isEdit = !!(existing && existing.id);
        openModal({
            title: isEdit ? '编辑 AI 供应商' : '新增 AI 供应商',
            width: 520,
            submitText: isEdit ? '保存修改' : '添加供应商',
            fields: [
                { key: 'name', label: '供应商名称', required: true, placeholder: '例如 OpenAI',
                  value: existing ? existing.name : '' },
                { key: 'provider_type', label: '类型', type: 'select',
                  value: existing ? existing.provider_type : 'openai',
                  options: [
                      { value: 'openai', label: 'OpenAI 兼容' },
                      { value: 'anthropic', label: 'Anthropic' },
                      { value: 'local', label: '本地模型' },
                      { value: 'custom', label: '自定义' },
                  ] },
                { key: 'api_base', label: 'API 地址', placeholder: 'https://api.openai.com/v1',
                  value: existing ? existing.api_base : 'https://api.openai.com/v1' },
                { key: 'api_key_encrypted', label: 'API Key', type: 'password',
                  placeholder: isEdit ? '留空则不修改' : 'sk-...',
                  value: '' , hint: isEdit ? 'API Key 已脱敏存储，留空则保持不变' : '' },
                { key: 'default_model', label: '默认模型', placeholder: 'gpt-4o-mini',
                  value: existing ? existing.default_model : 'gpt-4o-mini' },
                { key: 'temperature', label: '温度 (Temperature)', type: 'number',
                  value: existing ? existing.temperature : 0.7, min: 0, max: 2, step: 0.1 },
                { key: 'max_tokens', label: '最大 Token', type: 'number',
                  value: existing ? existing.max_tokens : 2048, min: 1, max: 128000 },
            ],
            onSubmit: function (data) {
                data.temperature = parseFloat(data.temperature) || 0.7;
                data.max_tokens = parseInt(data.max_tokens, 10) || 2048;
                // 编辑时如果 api_key 为空，不提交该字段
                if (isEdit && !data.api_key_encrypted) {
                    delete data.api_key_encrypted;
                }

                if (isEdit) {
                    return api.providers.update(existing.id, data).then(function () {
                        showToast('供应商已更新', 'success');
                    });
                } else {
                    return api.providers.create(data).then(function () {
                        showToast('供应商已添加', 'success');
                    });
                }
            },
        });
    }

    /* ══════════════════════════════════════════════
       Group 创建/编辑
       ══════════════════════════════════════════════ */
    function openGroupForm(existing) {
        var isEdit = !!(existing && existing.id);
        openModal({
            title: isEdit ? '编辑分组' : '新建分组',
            width: 400,
            submitText: isEdit ? '保存' : '创建分组',
            fields: [
                { key: 'name', label: '分组名称', required: true, placeholder: '例如 美国区直播号',
                  value: existing ? existing.name : '' },
                { key: 'description', label: '描述', type: 'textarea', placeholder: '可选',
                  value: existing ? existing.description : '' },
                { key: 'color', label: '标识色', placeholder: '#6366f1',
                  value: existing ? existing.color : '#6366f1', hint: '用于卡片左侧色条标识' },
            ],
            onSubmit: function (data) {
                if (isEdit) {
                    return api.groups.update(existing.id, data).then(function () {
                        showToast('分组已更新', 'success');
                    });
                } else {
                    return api.groups.create(data).then(function () {
                        showToast('分组已创建', 'success');
                    });
                }
            },
        });
    }

    /* ══════════════════════════════════════════════
       Device 创建/编辑
       ══════════════════════════════════════════════ */
    function openDeviceForm(existing) {
        var isEdit = !!(existing && existing.id);
        openModal({
            title: isEdit ? '编辑设备' : '新增设备',
            width: 480,
            submitText: isEdit ? '保存' : '添加设备',
            fields: [
                { key: 'device_code', label: '设备编码', required: true, placeholder: 'DEV-001',
                  value: existing ? existing.device_code : '', disabled: isEdit },
                { key: 'name', label: '设备名称', required: true, placeholder: '美国节点 #1',
                  value: existing ? existing.name : '' },
                { key: 'proxy_ip', label: '代理 IP', placeholder: '192.168.1.100:8080',
                  value: existing ? existing.proxy_ip : '' },
                { key: 'region', label: '地区', type: 'select',
                  value: existing ? existing.region : 'US',
                  options: ['US', 'UK', 'DE', 'JP', 'MY', 'ID', 'TH', 'VN', 'PH', 'BR', 'MX'] },
                { key: 'status', label: '设备状态', type: 'select',
                  value: existing ? existing.status : 'healthy',
                  options: [
                      { value: 'healthy', label: '健康' },
                      { value: 'warning', label: '警告' },
                      { value: 'error', label: '异常' },
                      { value: 'idle', label: '闲置' },
                  ] },
            ],
            onSubmit: function (data) {
                if (isEdit) {
                    delete data.device_code;
                    return api.devices.update(existing.id, data).then(function () {
                        showToast('设备已更新', 'success');
                    });
                } else {
                    return api.devices.create(data).then(function () {
                        showToast('设备已添加', 'success');
                    });
                }
            },
        });
    }

    /* ══════════════════════════════════════════════
       Asset 创建/编辑
       ══════════════════════════════════════════════ */
    function openAssetForm(existing) {
        var isEdit = !!(existing && existing.id);
        api.accounts.list().then(function (accounts) {
            accounts = accounts || [];
            var accountOpts = [{ value: '', label: '-- 不关联账号 --' }];
            accounts.forEach(function (a) {
                accountOpts.push({ value: String(a.id), label: a.username + ' (' + (a.platform || '') + ')' });
            });

            openModal({
                title: isEdit ? '编辑素材' : '新增素材',
                width: 520,
                submitText: isEdit ? '保存素材' : '创建素材',
                fields: [
                    { key: 'filename', label: '文件名', required: true, placeholder: '例如 campaign-cover-01.png', value: existing ? existing.filename : '' },
                    { key: 'asset_type', label: '素材类型', type: 'select', value: existing ? existing.asset_type : 'image',
                      options: [
                          { value: 'image', label: '图片' },
                          { value: 'video', label: '视频' },
                          { value: 'audio', label: '音频' },
                          { value: 'text', label: '文本' },
                          { value: 'template', label: '模板' },
                      ] },
                    { key: 'file_path', label: '本地路径', required: true, placeholder: 'C:/assets/campaign-cover-01.png', value: existing ? existing.file_path : '' },
                    { key: 'file_size', label: '文件大小(Byte)', type: 'number', min: 0, value: existing ? existing.file_size : 0 },
                    { key: 'account_id', label: '关联账号', type: 'select', value: existing ? String(existing.account_id || '') : '', options: accountOpts },
                    { key: 'tags', label: '标签', placeholder: '封面, 春促, US', value: existing ? existing.tags : '' },
                ],
                onSubmit: function (data) {
                    data.file_size = parseInt(data.file_size, 10) || 0;
                    if (data.account_id === '') data.account_id = null;
                    else data.account_id = parseInt(data.account_id, 10);

                    if (isEdit) {
                        return api.assets.update(existing.id, data).then(function () {
                            showToast('素材已更新', 'success');
                        });
                    }
                    return api.assets.create(data).then(function () {
                        showToast('素材已创建', 'success');
                    });
                },
            });
        });
    }

    // ── 暴露全局 ──
    window.openAccountForm = openAccountForm;
    window.openTaskForm = openTaskForm;
    window.openProviderForm = openProviderForm;
    window.openGroupForm = openGroupForm;
    window.openDeviceForm = openDeviceForm;
    window.openAssetForm = openAssetForm;
})();
