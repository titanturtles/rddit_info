/**
 * LLM Monitor page functionality
 */

console.log('[LLM Monitor] Loading...');

// Get utilities from common.js
let fetchAPI, createChart, setElementText;

if (typeof window.dashboardUtils !== 'undefined') {
    fetchAPI = window.dashboardUtils.fetchAPI;
    createChart = window.dashboardUtils.createChart;
    setElementText = window.dashboardUtils.setElementText;
    console.log('[LLM Monitor] Utilities loaded successfully');
} else {
    console.error('[LLM Monitor] ERROR: window.dashboardUtils not available');
}

let autoRefreshEnabled = true;

// ============================================================================
// INITIALIZE
// ============================================================================

async function initLLMMonitor() {
    loadLLMStats();
    loadRecentLLMCalls();
    loadLLMErrors();

    // Auto-refresh
    setInterval(() => {
        if (autoRefreshEnabled) {
            loadLLMStats();
            loadRecentLLMCalls();
            loadLLMErrors();
        }
    }, 15000);

    // Refresh button
    document.getElementById('refresh-btn')?.addEventListener('click', () => {
        loadLLMStats();
        loadRecentLLMCalls();
        loadLLMErrors();
    });
}

// ============================================================================
// LOAD LLM STATS
// ============================================================================

async function loadLLMStats() {
    const data = await fetchAPI('/llm/stats');
    if (data) {
        setElementText('llm-total-calls', data.total_calls);
        setElementText('llm-success', data.success);
        setElementText('llm-errors', data.errors);
        setElementText('llm-exceptions', data.exceptions);

        const successRateElement = document.getElementById('llm-success-rate');
        if (successRateElement) {
            successRateElement.textContent = data.success_rate.toFixed(1) + '%';
        }

        // Update status chart
        const chartConfig = {
            type: 'pie',
            data: {
                labels: ['Success', 'Errors', 'Exceptions'],
                datasets: [{
                    data: [data.success, data.errors, data.exceptions],
                    backgroundColor: [
                        '#28a745',  // Green (success)
                        '#ffc107',  // Yellow (error)
                        '#dc3545'   // Red (exception)
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

        window.dashboardUtils.createChart('llmStatusChart', chartConfig);
    }
}

// ============================================================================
// LOAD RECENT LLM CALLS
// ============================================================================

async function loadRecentLLMCalls() {
    const data = await fetchAPI('/llm/recent?limit=20');
    if (data && data.calls) {
        const tbody = document.getElementById('llm-calls-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (data.calls.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No LLM calls yet</td></tr>';
            return;
        }

        data.calls.forEach(call => {
            const statusColor = call.status === 'success' ? '#28a745' :
                              call.status === 'error' ? '#dc3545' : '#ffc107';
            const statusBg = call.status === 'success' ? 'rgba(40, 167, 69, 0.1)' :
                           call.status === 'error' ? 'rgba(220, 53, 69, 0.1)' : 'rgba(255, 193, 7, 0.1)';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(call.timestamp).toLocaleString()}</td>
                <td>${call.model}</td>
                <td>
                    <span style="
                        color: ${statusColor};
                        background: ${statusBg};
                        padding: 0.3rem 0.6rem;
                        border-radius: 4px;
                        font-weight: 600;
                        font-size: 0.85rem;
                    ">
                        ${call.status.toUpperCase()}
                    </span>
                </td>
                <td>${call.prompt_length}</td>
                <td>${call.response_length}</td>
                <td>${call.error ? `<span style="color: #dc3545;">${call.error}</span>` : '--'}</td>
            `;
            tbody.appendChild(row);
        });
    }
}

// ============================================================================
// LOAD LLM ERRORS
// ============================================================================

async function loadLLMErrors() {
    const data = await fetchAPI('/llm/errors');
    if (data && data.errors) {
        const tbody = document.getElementById('errors-tbody');
        const section = document.getElementById('errors-section');

        if (!tbody || !section) return;

        if (data.errors.length === 0) {
            section.style.display = 'none';
            return;
        }

        section.style.display = 'block';
        tbody.innerHTML = '';

        data.errors.forEach(error => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(error.timestamp).toLocaleString()}</td>
                <td>
                    <span style="
                        color: ${error.status === 'error' ? '#dc3545' : '#ffc107'};
                        font-weight: 600;
                        font-size: 0.85rem;
                    ">
                        ${error.status.toUpperCase()}
                    </span>
                </td>
                <td><span style="color: #dc3545;">${error.error}</span></td>
                <td><code style="background: #f5f5f5; padding: 0.2rem 0.4rem; border-radius: 3px; font-size: 0.8rem;">
                    ${error.prompt}
                </code></td>
            `;
            tbody.appendChild(row);
        });
    }
}

// ============================================================================
// DOCUMENT READY
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initLLMMonitor();
});
