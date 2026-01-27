/**
 * VIMaster Web UI JavaScript
 */

// API 基础 URL
const API_BASE = '';

// 通用 API 请求函数
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(API_BASE + url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        return await response.json();
    } catch (error) {
        console.error('API 请求失败:', error);
        throw error;
    }
}

// 分析单只股票
async function analyzeStock(stockCode) {
    return apiRequest('/api/analyze', {
        method: 'POST',
        body: JSON.stringify({ stock_code: stockCode })
    });
}

// 批量分析
async function analyzePortfolio(stockCodes) {
    return apiRequest('/api/analyze/batch', {
        method: 'POST',
        body: JSON.stringify({ stock_codes: stockCodes })
    });
}

// 获取历史记录
async function getHistory(stockCode = '', limit = 20) {
    let url = `/api/history?limit=${limit}`;
    if (stockCode) {
        url += `&stock_code=${stockCode}`;
    }
    return apiRequest(url);
}

// 获取统计信息
async function getStats() {
    return apiRequest('/api/stats');
}

// 格式化数字
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return 'N/A';
    return Number(num).toFixed(decimals);
}

// 格式化百分比
function formatPercent(num, decimals = 2) {
    if (num === null || num === undefined) return 'N/A';
    return Number(num).toFixed(decimals) + '%';
}

// 格式化货币
function formatCurrency(num, decimals = 2) {
    if (num === null || num === undefined) return 'N/A';
    return '¥' + Number(num).toFixed(decimals);
}

// 获取信号颜色类
function getSignalColorClass(signal) {
    const colors = {
        '强烈买入': 'success',
        '买入': 'success',
        '持有': 'warning',
        '卖出': 'danger',
        '强烈卖出': 'danger'
    };
    return colors[signal] || 'secondary';
}

// 获取风险颜色类
function getRiskColorClass(level) {
    const colors = {
        '低': 'success',
        '中': 'warning',
        '高': 'danger'
    };
    return colors[level] || 'secondary';
}

// 显示加载中
function showLoading(element, message = '加载中...') {
    element.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
            <p class="lead mt-3">${message}</p>
        </div>
    `;
}

// 显示错误
function showError(element, error) {
    element.innerHTML = `
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle"></i> ${error}
        </div>
    `;
}

// 显示成功提示
function showToast(message, type = 'success') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }

    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = container.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// 日期格式化
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    console.log('VIMaster Web UI 已加载');
});
