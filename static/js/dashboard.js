/**
 * Dashboard page functionality
 */

console.log('[Dashboard] Script starting...');
console.log('[Dashboard] window.dashboardUtils exists?', typeof window.dashboardUtils !== 'undefined');

// Get utilities from common.js
let dFetchAPI, dFormatNumber, dCreateChart, dUpdateChart, dSetElementText;

if (typeof window.dashboardUtils === 'undefined') {
    console.error('[Dashboard] ERROR: window.dashboardUtils is not defined!');
    console.error('[Dashboard] This means common.js did not load properly');
} else {
    console.log('[Dashboard] Successfully loading from window.dashboardUtils');
    dFetchAPI = window.dashboardUtils.fetchAPI;
    dFormatNumber = window.dashboardUtils.formatNumber;
    dCreateChart = window.dashboardUtils.createChart;
    dUpdateChart = window.dashboardUtils.updateChart;
    dSetElementText = window.dashboardUtils.setElementText;
}

// ============================================================================
// INITIALIZE
// ============================================================================

async function initDashboard() {
    console.log('[Dashboard] Initializing...');

    // Safety check: verify functions are available
    if (typeof dFetchAPI === 'undefined') {
        console.error('[Dashboard] CRITICAL: dFetchAPI is not defined!');
        console.error('[Dashboard] Cannot proceed with initialization');
        return;
    }

    if (typeof dSetElementText === 'undefined') {
        console.error('[Dashboard] CRITICAL: dSetElementText is not defined!');
        console.error('[Dashboard] Cannot proceed with initialization');
        return;
    }

    try {
        console.log('[Dashboard] Functions verified, starting data loads...');
        await loadDashboardStats();
        await loadSentimentSummary();
        await loadTopStocks();
        await loadRecentLLMCalls();
        console.log('[Dashboard] Initialization complete');

        // Refresh every 30 seconds
        setInterval(loadDashboardStats, 30000);
        setInterval(loadSentimentSummary, 30000);
        setInterval(loadTopStocks, 60000);
        setInterval(loadRecentLLMCalls, 20000);
    } catch (error) {
        console.error('[Dashboard] Error during initialization:', error);
        console.error('[Dashboard] Stack trace:', error.stack);
    }
}

// ============================================================================
// LOAD DASHBOARD STATS
// ============================================================================

async function loadDashboardStats() {
    console.log('[Dashboard] Loading dashboard stats...');
    const data = await dFetchAPI('/dashboard/stats');
    console.log('[Dashboard] Dashboard stats data:', data);
    if (data) {
        console.log('[Dashboard] Updating UI with stats');
        dSetElementText('posts-count', data.posts);
        dSetElementText('comments-count', data.comments);
        dSetElementText('sentiments-count', data.sentiments_analyzed);
        dSetElementText('stocks-count', data.unique_stocks);
        dSetElementText('llm-calls', data.llm_calls);
        dSetElementText('patterns-count', data.patterns_detected);
    } else {
        console.error('[Dashboard] Failed to load dashboard stats');
    }
}

// ============================================================================
// LOAD SENTIMENT SUMMARY
// ============================================================================

async function loadSentimentSummary() {
    const data = await dFetchAPI('/sentiment/summary');
    console.log('Sentiment summary:', data);
    if (data) {
        const chartConfig = {
            type: 'doughnut',
            data: {
                labels: ['Bullish', 'Neutral', 'Bearish'],
                datasets: [{
                    data: [data.bullish, data.neutral, data.bearish],
                    backgroundColor: [
                        '#28a745',  // Green (bullish)
                        '#6c757d',  // Gray (neutral)
                        '#dc3545'   // Red (bearish)
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        };

        dCreateChart('sentimentChart', chartConfig);
    }
}

// ============================================================================
// LOAD TOP STOCKS
// ============================================================================

async function loadTopStocks() {
    const data = await dFetchAPI('/stocks/top?limit=10');
    if (data && data.stocks) {
        const tbody = document.getElementById('top-stocks-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (data.stocks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No data available</td></tr>';
            return;
        }

        data.stocks.forEach(stock => {
            const row = document.createElement('tr');
            const bullishPercent = (stock.bullish_ratio * 100).toFixed(0);
            const sentimentColor = stock.bullish_ratio > 0.6 ? '#28a745' :
                                  stock.bullish_ratio < 0.4 ? '#dc3545' : '#666';

            row.innerHTML = `
                <td><strong>${stock.symbol}</strong></td>
                <td>${stock.mentions}</td>
                <td>
                    <span style="color: ${sentimentColor}; font-weight: 600;">
                        ${bullishPercent}%
                    </span>
                </td>
                <td><span style="color: #28a745;">${stock.bullish}</span></td>
                <td><span style="color: #dc3545;">${stock.bearish}</span></td>
                <td>${stock.neutral}</td>
                <td>
                    <span style="color: ${sentimentColor}; font-weight: 500;">
                        ${stock.avg_sentiment_score}
                    </span>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
}

// ============================================================================
// LOAD RECENT LLM CALLS
// ============================================================================

async function loadRecentLLMCalls() {
    const data = await dFetchAPI('/llm/recent?limit=5');
    if (data && data.calls) {
        const container = document.getElementById('activity-list');
        if (!container) return;

        container.innerHTML = '';

        if (data.calls.length === 0) {
            container.innerHTML = '<div class="loading">No LLM calls yet</div>';
            return;
        }

        data.calls.forEach(call => {
            const statusColor = call.status === 'success' ? '#28a745' :
                              call.status === 'error' ? '#dc3545' : '#ffc107';
            const statusIcon = call.status === 'success' ? '✓' :
                             call.status === 'error' ? '✗' : '⚠';

            const item = document.createElement('div');
            item.className = 'activity-item';
            item.innerHTML = `
                <div class="activity-item-header">
                    <div>
                        <span style="color: ${statusColor}; font-weight: 600;">
                            ${statusIcon} ${call.status.toUpperCase()}
                        </span>
                    </div>
                    <div class="activity-item-time">
                        ${new Date(call.timestamp).toLocaleTimeString()}
                    </div>
                </div>
                <div class="activity-item-text">
                    <strong>${call.model}</strong> -
                    Prompt: ${call.prompt_length} chars,
                    Response: ${call.response_length} chars
                    ${call.error ? `<br><span style="color: #dc3545;">Error: ${call.error}</span>` : ''}
                </div>
            `;
            container.appendChild(item);
        });
    }
}

// ============================================================================
// LOAD TIMELINE DATA
// ============================================================================

async function loadTimelineData() {
    const data = await dFetchAPI('/data/timeline?days=7');
    if (data && data.timeline) {
        const labels = data.timeline.map(item => item.date);
        const counts = data.timeline.map(item => item.posts);

        const chartConfig = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Posts',
                    data: counts,
                    borderColor: '#0066cc',
                    backgroundColor: 'rgba(0, 102, 204, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#0066cc',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        };

        dCreateChart('timelineChart', chartConfig);
    }
}

// ============================================================================
// DOCUMENT READY
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Dashboard] DOMContentLoaded event fired');
    initDashboard();
    loadTimelineData();
});

console.log('[Dashboard] Script loaded, waiting for DOMContentLoaded event');
