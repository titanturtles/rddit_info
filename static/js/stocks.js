/**
 * Stocks page functionality
 */

console.log('[Stocks] Loading...');

// Get utilities from common.js
let dFetchAPI, dCreateChart, dSetElementText;

if (typeof window.dashboardUtils !== 'undefined') {
    dFetchAPI = window.dashboardUtils.fetchAPI;
    dCreateChart = window.dashboardUtils.createChart;
    dSetElementText = window.dashboardUtils.setElementText;
    console.log('[Stocks] Utilities loaded successfully');
} else {
    console.error('[Stocks] ERROR: window.dashboardUtils not available');
}

// ============================================================================
// INITIALIZE
// ============================================================================

async function initStocks() {
    loadSentimentSummary();
    loadTopStocks(10);

    // Refresh every 30 seconds
    setInterval(loadSentimentSummary, 30000);
    setInterval(() => loadTopStocks(getCurrentLimit()), 30000);

    // Limit selector
    const limitSelect = document.getElementById('limit-select');
    if (limitSelect) {
        limitSelect.addEventListener('change', (e) => {
            loadTopStocks(parseInt(e.target.value));
        });
    }

    // Refresh button
    document.getElementById('refresh-stocks-btn')?.addEventListener('click', () => {
        loadTopStocks(getCurrentLimit());
    });
}

function getCurrentLimit() {
    const select = document.getElementById('limit-select');
    return select ? parseInt(select.value) : 10;
}

// ============================================================================
// LOAD SENTIMENT SUMMARY
// ============================================================================

async function loadSentimentSummary() {
    const data = await dFetchAPI('/sentiment/summary');
    if (data) {
        dSetElementText('bullish-count', data.bullish);
        dSetElementText('neutral-count', data.neutral);
        dSetElementText('bearish-count', data.bearish);

        // Create distribution chart
        const total = data.bullish + data.neutral + data.bearish;
        const chartConfig = {
            type: 'bar',
            data: {
                labels: ['Bullish', 'Neutral', 'Bearish'],
                datasets: [{
                    label: 'Count',
                    data: [data.bullish, data.neutral, data.bearish],
                    backgroundColor: [
                        '#28a745',  // Green (bullish)
                        '#6c757d',  // Gray (neutral)
                        '#dc3545'   // Red (bearish)
                    ],
                    borderRadius: 4,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        };

        window.dashboardUtils.dCreateChart('sentimentDistributionChart', chartConfig);
    }
}

// ============================================================================
// LOAD TOP STOCKS
// ============================================================================

async function loadTopStocks(limit = 10) {
    const data = await dFetchAPI(`/stocks/top?limit=${limit}`);
    if (data && data.stocks) {
        const tbody = document.getElementById('stocks-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (data.stocks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No data available</td></tr>';
            return;
        }

        data.stocks.forEach((stock, index) => {
            const bullishPercent = (stock.bullish_ratio * 100).toFixed(0);
            const sentimentColor = stock.bullish_ratio > 0.6 ? '#28a745' :
                                  stock.bullish_ratio < 0.4 ? '#dc3545' : '#666';

            // Trending indicator
            const trendingIcon = index < 3 ? '🔥' : '📊';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <strong style="font-size: 1.1rem;">${stock.symbol}</strong>
                    ${index < 3 ? `<span style="margin-left: 0.5rem;">${trendingIcon}</span>` : ''}
                </td>
                <td><strong>${stock.mentions}</strong></td>
                <td>
                    <div style="
                        background: linear-gradient(90deg, rgba(40, 167, 69, 0.2) 0%, rgba(40, 167, 69, 0.2) ${bullishPercent}%, transparent ${bullishPercent}%, transparent 100%);
                        padding: 0.5rem;
                        border-radius: 4px;
                        text-align: center;
                    ">
                        <span style="color: ${sentimentColor}; font-weight: 600;">
                            ${bullishPercent}%
                        </span>
                    </div>
                </td>
                <td>
                    <span style="
                        background: rgba(40, 167, 69, 0.1);
                        color: #28a745;
                        padding: 0.3rem 0.6rem;
                        border-radius: 4px;
                        font-weight: 500;
                    ">
                        ${stock.bullish}
                    </span>
                </td>
                <td>
                    <span style="
                        background: rgba(220, 53, 69, 0.1);
                        color: #dc3545;
                        padding: 0.3rem 0.6rem;
                        border-radius: 4px;
                        font-weight: 500;
                    ">
                        ${stock.bearish}
                    </span>
                </td>
                <td>
                    <span style="
                        background: rgba(108, 117, 125, 0.1);
                        color: #6c757d;
                        padding: 0.3rem 0.6rem;
                        border-radius: 4px;
                        font-weight: 500;
                    ">
                        ${stock.neutral}
                    </span>
                </td>
                <td>
                    <strong style="color: ${sentimentColor};">
                        ${stock.avg_sentiment_score > 0 ? '+' : ''}${stock.avg_sentiment_score}
                    </strong>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
}

// ============================================================================
// DOCUMENT READY
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initStocks();
});
