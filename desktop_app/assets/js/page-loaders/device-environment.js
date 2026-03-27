(function () {
    'use strict';

    var shared = window.__pageLoaderShared;
    if (!shared) {
        throw new Error('page loader shared helpers not loaded');
    }

    var loaders = window._pageLoaders;
    if (!loaders) {
        throw new Error('page loader registry not loaded');
    }

    var _deviceBool = shared.deviceBool;

    function _renderDeviceDetail(deviceModel, logs) {
        var page = window.__deviceManagementPageMain;
        if (page && typeof page.renderDeviceDetail === 'function') {
            return page.renderDeviceDetail(deviceModel, logs);
        }
    }

    function _runDeviceInspection(deviceIds) {
        var models = window.__devicePageData || [];
        var targets = Array.isArray(deviceIds) && deviceIds.length ? models.filter(function (item) { return deviceIds.indexOf(item.id) >= 0; }) : models;
        return Promise.all((targets || []).map(function (item) {
            return api.devices.inspect(item.id);
        })).then(function (results) {
            var abnormal = (results || []).filter(function (item) { return item && item.status === 'error'; }).length;
            var warnings = (results || []).filter(function (item) { return item && item.status === 'warning'; }).length;
            var idle = (results || []).filter(function (item) { return item && item.status === 'idle'; }).length;
            showToast('已完成 ' + results.length + ' 台设备巡检，异常 ' + abnormal + ' 台，告警 ' + warnings + ' 台，空闲 ' + idle + ' 台', abnormal || warnings ? 'warning' : 'success');
            if (uiState['device-management']) {
                var firstProblem = (results || []).find(function (item) { return item && (item.status === 'error' || item.status === 'warning'); });
                if (firstProblem) uiState['device-management'].selectedId = firstProblem.device_id;
            }
            loaders['device-management']();
            return results;
        }).catch(function (err) {
            showToast('设备巡检失败: ' + ((err && err.message) || '未知错误'), 'error');
            throw err;
        });
    }

    function _runDeviceRepair(deviceIds) {
        var models = window.__devicePageData || [];
        var targets = Array.isArray(deviceIds) && deviceIds.length ? models.filter(function (item) { return deviceIds.indexOf(item.id) >= 0; }) : models;
        return Promise.all((targets || []).map(function (item) {
            return api.devices.repair(item.id);
        })).then(function (results) {
            var manual = (results || []).filter(function (item) {
                var actions = (item && item.actions) || [];
                return actions.some(function (action) { return String(action).indexOf('人工') >= 0; });
            }).length;
            showToast('已执行 ' + results.length + ' 台设备修复：完成状态归一、隔离 profile 准备，并记录修复日志。仍有 ' + manual + ' 台需要人工处理。', manual ? 'warning' : 'success');
            loaders['device-management']();
            return results;
        });
    }

    function _openDeviceEnvironment(deviceId) {
        if (!deviceId) {
            showToast('请先选择设备', 'warning');
            return Promise.resolve(null);
        }
        return api.devices.openEnvironment(deviceId).then(function (result) {
            showToast('已启动外部浏览器隔离实例', 'success');
            return result;
        }).catch(function (err) {
            showToast('打开环境失败: ' + ((err && err.message) || '未知错误'), 'error');
            throw err;
        });
    }

    function _exportDeviceReport() {
        var models = window.__devicePageData || [];
        var lines = [];
        models.forEach(function (item) {
            lines.push('设备：' + item.name + ' / ' + item.deviceCode);
            lines.push('状态：' + item.statusMeta.label + ' / 代理 ' + item.proxyStatusLabel + ' / 指纹 ' + item.fingerprintLabel);
            lines.push('地区：' + item.regionLabel + ' / 代理地址：' + item.proxyLabel);
            lines.push('绑定账号：' + (item.boundAccounts.length ? item.boundAccounts.map(function (account) {
                var login = account.last_login_check_status || 'unknown';
                var isolation = _deviceBool(account.isolation_enabled) ? '已隔离' : '未隔离';
                return (account.username || ('账号#' + account.id)) + ' [' + isolation + ' / 登录态 ' + login + ']';
            }).join('；') : '无'));
            lines.push('隔离覆盖：' + item.coveragePercent + '% / 最近巡检：' + item.lastInspectionLabel);
            lines.push('巡检问题：' + (item.issues.length ? item.issues.map(function (issue) { return issue.title + ' - ' + issue.copy; }).join('；') : '无'));
            lines.push('');
        });
        return _exportThroughBackend('设备环境报告', lines, '设备报告已导出');
    }

    function _exportDeviceLog(deviceId, options) {
        var config = options || {};
        var models = window.__devicePageData || [];
        var target = models.find(function (item) { return String(item.id || '') === String(deviceId || ''); }) || null;
        if (!target) {
            showToast('未找到设备日志数据', 'warning');
            return Promise.resolve(null);
        }
        return api.devices.logs(target.id).then(function (logs) {
            target.logs = logs || [];
            _renderDeviceDetail(target, target.logs);
            if (!config.silent) showToast('已切换到当前设备的日志详情', 'info');
            return logs || [];
        }).catch(function (err) {
            showToast('加载设备日志失败: ' + ((err && err.message) || '未知错误'), 'error');
            throw err;
        });
    }

    window.__deviceEnvironmentHelpers = {
        runDeviceInspection: _runDeviceInspection,
        runDeviceRepair: _runDeviceRepair,
        openDeviceEnvironment: _openDeviceEnvironment,
        exportDeviceReport: _exportDeviceReport,
        exportDeviceLog: _exportDeviceLog,
    };
})();