/**
 * Common utility functions for the trading bot dashboard
 */

console.log('[Common] Loading common.js utilities...');

// ============================================================================
// API FUNCTIONS
// ============================================================================

const API_BASE_URL = '/api';
console.log('[Common] API_BASE_URL:', API_BASE_URL);

async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

// ============================================================================
// FORMATTING FUNCTIONS
// ============================================================================

function formatNumber(num) {
    if (num === null || num === undefined) return '--';
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatDate(dateString) {
    if (!dateString) return '--';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function formatTime(dateString) {
    if (!dateString) return '--';
    const date = new Date(dateString);
    return date.toLocaleTimeString();
}

function formatPercent(value, decimals = 2) {
    if (value === null || value === undefined) return '--%';
    return (value * 100).toFixed(decimals) + '%';
}

function getSentimentColor(sentiment) {
    if (!sentiment) return '#999';
    const sentimentLower = sentiment.toLowerCase();
    if (sentimentLower.includes('bullish') || sentimentLower.includes('positive')) {
        return '#28a745'; // Green
    }
    if (sentimentLower.includes('bearish') || sentimentLower.includes('negative')) {
        return '#dc3545'; // Red
    }
    return '#666'; // Gray (neutral)
}

function getSentimentIcon(sentiment) {
    if (!sentiment) return '➜';
    const sentimentLower = sentiment.toLowerCase();
    if (sentimentLower.includes('bullish') || sentimentLower.includes('positive')) {
        return '↑';
    }
    if (sentimentLower.includes('bearish') || sentimentLower.includes('negative')) {
        return '↓';
    }
    return '➜';
}

// ============================================================================
// DOM HELPER FUNCTIONS
// ============================================================================

function getElementById(id) {
    return document.getElementById(id);
}

function setElementText(id, text) {
    const element = getElementById(id);
    if (element) {
        element.textContent = formatNumber(text);
    }
}

function setElementHTML(id, html) {
    const element = getElementById(id);
    if (element) {
        element.innerHTML = html;
    }
}

function addEventListener(id, event, callback) {
    const element = getElementById(id);
    if (element) {
        element.addEventListener(event, callback);
    }
}

function hideElement(id) {
    const element = getElementById(id);
    if (element) {
        element.style.display = 'none';
    }
}

function showElement(id, display = 'block') {
    const element = getElementById(id);
    if (element) {
        element.style.display = display;
    }
}

// ============================================================================
// TIME FUNCTIONS
// ============================================================================

function updateLastUpdated() {
    const timestamp = new Date().toLocaleTimeString();
    const element = getElementById('last-updated');
    if (element) {
        element.textContent = timestamp;
    }
}

setInterval(updateLastUpdated, 1000);

// ============================================================================
// CHART HELPER FUNCTIONS
// ============================================================================

let chartInstances = {};

function createChart(canvasId, config) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    // Destroy existing chart if any
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }

    const chart = new Chart(ctx, config);
    chartInstances[canvasId] = chart;
    return chart;
}

function updateChart(canvasId, labels, datasets) {
    const chart = chartInstances[canvasId];
    if (chart) {
        chart.data.labels = labels;
        chart.data.datasets = datasets;
        chart.update();
    }
}

function destroyChart(canvasId) {
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
        delete chartInstances[canvasId];
    }
}

// ============================================================================
// STATUS FUNCTIONS
// ============================================================================

async function checkHealth() {
    const data = await fetchAPI('/health');
    if (data) {
        const statusElement = getElementById('health-status');
        if (statusElement) {
            const status = data.status === 'healthy' ? 'Healthy' : 'Unhealthy';
            const icon = data.status === 'healthy'
                ? '<i class="fas fa-check-circle" style="color: #28a745;"></i>'
                : '<i class="fas fa-exclamation-circle" style="color: #dc3545;"></i>';
            statusElement.innerHTML = `${icon} ${status}`;
        }
    }
}

// Check health every 30 seconds - but wait for DOM to be ready first
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkHealth);
} else {
    checkHealth();
}
setInterval(checkHealth, 30000);

// ============================================================================
// EXPORT FUNCTIONS
// ============================================================================

window.dashboardUtils = {
    fetchAPI,
    formatNumber,
    formatDate,
    formatTime,
    formatPercent,
    getSentimentColor,
    getSentimentIcon,
    getElementById,
    setElementText,
    setElementHTML,
    addEventListener,
    hideElement,
    showElement,
    createChart,
    updateChart,
    destroyChart,
    checkHealth
};

console.log('[Common] window.dashboardUtils exported successfully');
console.log('[Common] Available utilities:', Object.keys(window.dashboardUtils));
