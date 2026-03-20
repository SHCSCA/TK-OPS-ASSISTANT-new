function makeConfigCenterRoute(config) {
    const navSections = config.navSections || [];
    const formGroups = config.formGroups || [];
    const notices = config.notices || [];
    const detailGroups = config.detailGroups || [];
    const detailCards = config.detailCards || [];
    const configType = config.configType || 'settings';

    const navHtml = navSections
        .map((section, i) => `<button class="config-nav-item ${i === 0 ? 'is-selected' : ''}" type="button" data-search="${section.search || section.label}">${section.icon ? `<span class="config-nav-icon">${section.icon}</span>` : ''}<span>${section.label}</span>${section.badge ? `<span class="pill ${section.badgeTone || 'info'}">${section.badge}</span>` : ''}</button>`)
        .join('');

    const noticeHtml = notices
        .map((n) => `<section class="notice-banner ${n.tone ? 'notice-banner--' + n.tone : ''}"><div><strong>${n.title}</strong><div>${n.desc}</div></div></section>`)
        .join('');

    let centerContentHtml = '';

    if (configType === 'settings') {
        centerContentHtml = formGroups
            .map((group) => `
                <section class="config-form-group">
                    <div class="config-form-group__header"><strong>${group.title}</strong><div class="subtle">${group.desc}</div></div>
                    <div class="config-form-fields">
                        ${group.fields
                            .map((f) => `
                                <div class="config-field" data-search="${f.search || f.label}">
                                    <label class="config-field__label">${f.label}${f.required ? ' <span class="config-field__req">*</span>' : ''}</label>
                                    <div class="config-field__control">
                                        ${f.type === 'select'
                                            ? `<div class="config-select"><span>${f.value}</span><span class="config-select__arrow">▾</span></div>`
                                            : f.type === 'toggle'
                                                ? `<div class="config-toggle ${f.value === true || f.value === '开' ? 'is-on' : ''}"><span class="config-toggle__track"></span><span class="config-toggle__label">${f.value === true || f.value === '开' ? '开' : '关'}</span></div>`
                                                : `<div class="config-input">${f.value || ''}</div>`
                                        }
                                    </div>
                                    ${f.hint ? `<div class="config-field__hint subtle">${f.hint}</div>` : ''}
                                </div>
                            `)
                            .join('')}
                    </div>
                </section>
            `)
            .join('');
    } else if (configType === 'permissions') {
        const matrix = config.permissionMatrix || {};
        const roles = matrix.roles || [];
        const modules = matrix.modules || [];
        centerContentHtml = `
            <section class="config-form-group">
                <div class="config-form-group__header"><strong>${matrix.title || '权限矩阵'}</strong><div class="subtle">${matrix.desc || '按角色和模块分配权限'}</div></div>
                <div class="table-wrapper">
                    <table>
                        <thead><tr><th>模块</th>${roles.map((r) => `<th>${r}</th>`).join('')}</tr></thead>
                        <tbody>
                            ${modules
                                .map((m) => `<tr data-search="${m.name} ${roles.join(' ')}"><td><strong>${m.name}</strong></td>${m.access.map((a) => `<td><span class="status-chip ${a === '完全' ? 'success' : a === '只读' ? 'info' : a === '禁止' ? 'error' : 'warning'}">${a}</span></td>`).join('')}</tr>`)
                                .join('')}
                        </tbody>
                    </table>
                </div>
            </section>
            ${config.memberList
                ? `<section class="config-form-group">
                    <div class="config-form-group__header"><strong>成员列表</strong><div class="subtle">已注册用户与权限分配</div></div>
                    <div class="table-wrapper">
                        <table>
                            <thead><tr><th>成员</th><th>角色</th><th>最后活跃</th><th>状态</th></tr></thead>
                            <tbody>
                                ${config.memberList.map((m) => `<tr data-search="${m.name} ${m.role}"><td><strong>${m.name}</strong></td><td>${m.role}</td><td class="subtle">${m.lastActive}</td><td><span class="status-chip ${m.statusTone}">${m.status}</span></td></tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </section>`
                : ''}
        `;
    } else if (configType === 'wizard') {
        const steps = config.wizardSteps || [];
        centerContentHtml = `
            <div class="wizard-progress">
                ${steps.map((s, i) => `<div class="wizard-step ${i === 0 ? 'is-active' : i < (config.currentStep || 0) ? 'is-done' : ''}" data-search="${s.search || s.title}"><span class="wizard-step__num">${i + 1}</span><div class="wizard-step__info"><strong>${s.title}</strong><div class="subtle">${s.desc}</div></div></div>`).join('<div class="wizard-step__connector"></div>')}
            </div>
            <section class="config-form-group wizard-active-step">
                <div class="config-form-group__header"><strong>${steps[0]?.title || '当前步骤'}</strong><div class="subtle">${steps[0]?.desc || ''}</div></div>
                <div class="config-form-fields">
                    ${(steps[0]?.fields || [])
                        .map((f) => `
                            <div class="config-field" data-search="${f.search || f.label}">
                                <label class="config-field__label">${f.label}</label>
                                <div class="config-field__control">
                                    ${f.type === 'select'
                                        ? `<div class="config-select"><span>${f.value}</span><span class="config-select__arrow">▾</span></div>`
                                        : `<div class="config-input">${f.value || ''}</div>`
                                    }
                                </div>
                                ${f.hint ? `<div class="config-field__hint subtle">${f.hint}</div>` : ''}
                            </div>
                        `)
                        .join('')}
                </div>
            </section>
        `;
    }

    const detailGroupsHtml = detailGroups
        .map((g) => `<div class="detail-item"><span class="subtle">${g.label}</span><strong>${g.value}</strong></div>`)
        .join('');

    const detailCardsHtml = detailCards
        .map((card) => `<article class="strip-card" data-search="${card.search || card.title}"><strong>${card.title}</strong><div class="subtle">${card.desc}</div><span class="pill ${card.tone}">${card.badge}</span></article>`)
        .join('');

    return {
        eyebrow: config.eyebrow,
        searchTerms: `${config.title} ${config.description} ${config.headerEyebrow} ${config.breadcrumb}`,
        sidebarSummary: config.sidebarSummary,
        statusLeft: config.statusLeft,
        statusRight: config.statusRight,
        mainHtml: `
            <div class="breadcrumbs"><span>${config.breadcrumb}</span><span>/</span><span>${config.title}</span></div>
            <div class="page-header">
                <div>
                    <div class="eyebrow">${config.headerEyebrow}</div>
                    <h1>${config.title}</h1>
                    <p>${config.description}</p>
                </div>
                <div class="header-actions">
                    <button class="secondary-button" type="button">${config.secondaryAction}</button>
                    <button class="primary-button" type="button">${config.primaryAction}</button>
                </div>
            </div>
            <section class="config-center-shell">
                <nav class="config-nav">${navHtml}</nav>
                <div class="config-center-body section-stack">
                    ${noticeHtml}
                    ${centerContentHtml}
                </div>
            </section>
            ${configType !== 'wizard' ? '' : `<div class="wizard-actions"><button class="secondary-button" type="button">上一步</button><button class="primary-button" type="button">下一步</button></div>`}
        `,
        detailHtml: `
            <div class="detail-root">
                <section class="panel">
                    <div class="panel__header"><div><strong>${config.detailTitle || config.title + '说明'}</strong><div class="subtle">${config.detailDesc || '当前配置项的状态与建议'}</div></div></div>
                    <div class="detail-list">${detailGroupsHtml}</div>
                </section>
                ${detailCardsHtml ? `<section class="panel"><div class="panel__header"><div><strong>配置建议</strong><div class="subtle">根据当前状态给出的优化提示</div></div></div><div class="workbench-side-list">${detailCardsHtml}</div></section>` : ''}
            </div>
        `,
    };
}

function makeLicenseIssuerRoute() {
    return {
        eyebrow: '许可证管理中心',
        searchTerms: '许可证 签发 管理员 machine id license issuer activation',
        sidebarSummary: {
            eyebrow: '授权提醒',
            title: '请使用完整 64 位机器码签发',
            copy: '短码仅用于人工识别，真正签发和校验必须使用完整机器指纹。',
        },
        statusLeft: ['管理员签发', '本地 HMAC 签名', '支持永久与期限许可证'],
        statusRight: [
            { text: '签发工具在线', tone: 'success' },
            { text: '仅限管理员', tone: 'warning' },
        ],
        mainHtml: `
            <div class="breadcrumbs"><span>system</span><span>/</span><span>许可证签发</span></div>
            <div class="page-header">
                <div>
                    <div class="eyebrow">管理员授权工作台</div>
                    <h1>许可证签发</h1>
                    <p>面向管理员生成单机许可证。上方展示当前设备机器码，签发远端设备时请粘贴对方提供的完整 64 位机器码。</p>
                </div>
                <div class="header-actions">
                    <button class="secondary-button" type="button" id="licenseIssuerUseLocal">使用本机机器码</button>
                    <button class="primary-button" type="button" id="licenseIssuerGenerate">生成许可证</button>
                </div>
            </div>
            <section class="section-stack">
                <div class="stat-grid">
                    <article class="stat-card"><div><div class="subtle">本机短码</div><div class="stat-card__value" id="licenseIssuerShort">加载中</div></div><div class="stat-card__delta"><span>显示识别</span><span class="subtle">仅供人工核对</span></div></article>
                    <article class="stat-card"><div><div class="subtle">许可证模式</div><div class="stat-card__value" id="licenseIssuerMode">永久 / 天数</div></div><div class="stat-card__delta"><span>可选</span><span class="subtle">支持试用与正式版</span></div></article>
                    <article class="stat-card"><div><div class="subtle">当前激活状态</div><div class="stat-card__value" id="licenseIssuerStatus">检测中</div></div><div class="stat-card__delta"><span>本机状态</span><span class="subtle">便于交叉验证</span></div></article>
                </div>
                <section class="config-center-shell">
                    <nav class="config-nav">
                        <button class="config-nav-item is-selected" type="button"><span class="config-nav-icon">签</span><span>许可证签发</span><span class="pill warning">管理员</span></button>
                        <button class="config-nav-item" type="button"><span class="config-nav-icon">验</span><span>结果校验</span></button>
                    </nav>
                    <div class="config-center-body section-stack">
                        <section class="notice-banner notice-banner--warning"><div><strong>短码不能用于真实签发</strong><div>短码只用于识别设备。远端设备必须提供完整 64 位机器码，否则签发出的许可证无法通过校验。</div></div></section>
                        <section class="config-form-group">
                            <div class="config-form-group__header"><strong>签发参数</strong><div class="subtle">先确认机器码、有效期和许可证等级，再点击生成。</div></div>
                            <div class="config-form-fields">
                                <div class="config-field">
                                    <label class="config-field__label">本机短码</label>
                                    <div class="config-field__control"><div class="config-input" id="licenseIssuerShortEcho">加载中</div></div>
                                    <div class="config-field__hint subtle">便于与用户口头确认是否为同一台设备</div>
                                </div>
                                <div class="config-field">
                                    <label class="config-field__label">完整机器码</label>
                                    <div class="config-field__control"><textarea id="licenseIssuerMachineId" class="license-input" rows="3" placeholder="粘贴 64 位十六进制完整机器码"></textarea></div>
                                    <div class="config-field__hint subtle">支持本机自动填充，也可粘贴远端设备机器码</div>
                                </div>
                                <div class="config-field">
                                    <label class="config-field__label">许可证等级</label>
                                    <div class="config-field__control"><select id="licenseIssuerTier" class="list-filter-select"><option value="free">free</option><option value="pro" selected>pro</option><option value="enterprise">enterprise</option></select></div>
                                    <div class="config-field__hint subtle">等级会直接写入许可证载荷</div>
                                </div>
                                <div class="config-field">
                                    <label class="config-field__label">有效天数</label>
                                    <div class="config-field__control"><input id="licenseIssuerDays" class="license-input" type="number" min="0" step="1" value="365"></div>
                                    <div class="config-field__hint subtle">填 0 表示永久许可证</div>
                                </div>
                            </div>
                        </section>
                        <section class="config-form-group">
                            <div class="config-form-group__header"><strong>签发结果</strong><div class="subtle">生成后可直接复制许可证，也可以立即用当前机器码做一次本地校验。</div></div>
                            <div class="config-form-fields">
                                <div class="config-field">
                                    <label class="config-field__label">许可证密钥</label>
                                    <div class="config-field__control"><textarea id="licenseIssuerOutput" class="license-input" rows="6" readonly placeholder="点击“生成许可证”后显示结果"></textarea></div>
                                    <div class="config-field__hint subtle" id="licenseIssuerMeta">尚未生成</div>
                                </div>
                                <div class="detail-actions">
                                    <button class="secondary-button" type="button" id="licenseIssuerCopyMachine">复制机器码</button>
                                    <button class="secondary-button" type="button" id="licenseIssuerCopyKey">复制许可证</button>
                                    <button class="secondary-button" type="button" id="licenseIssuerVerify">校验当前许可证</button>
                                </div>
                            </div>
                        </section>
                    </div>
                </section>
            </section>
        `,
        detailHtml: `
            <div class="detail-root">
                <section class="panel">
                    <div class="panel__header"><div><strong>签发说明</strong><div class="subtle">这页直接调用桌面端内置签名密钥，不是模拟页面。</div></div></div>
                    <div class="detail-list">
                        <div class="detail-item"><span class="subtle">签发要求</span><strong>必须使用完整机器码</strong></div>
                        <div class="detail-item"><span class="subtle">有效天数</span><strong>0 = 永久许可证</strong></div>
                        <div class="detail-item"><span class="subtle">风控提示</span><strong>支持复合机器码（漂移容忍）</strong></div>
                    </div>
                </section>
                <section class="panel">
                    <div class="panel__header"><div><strong>操作建议</strong><div class="subtle">避免再次出现短码签发导致的无效授权。</div></div></div>
                    <div class="workbench-side-list">
                        <article class="strip-card"><strong>先复制完整机器码</strong><div class="subtle">不要再把短码发给签发人。</div><span class="pill warning">关键</span></article>
                        <article class="strip-card"><strong>生成后立即校验</strong><div class="subtle">至少在签发端自检一次格式和有效期。</div><span class="pill success">建议</span></article>
                        <article class="strip-card"><strong>密钥已更新为生产版</strong><div class="subtle">HMAC-SHA256 256-bit 密钥已就绪。</div><span class="pill success">已完成</span></article>
                    </div>
                </section>
            </div>
        `,
    };
}

