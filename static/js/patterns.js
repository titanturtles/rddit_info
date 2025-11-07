/**
 * Patterns page functionality
 */

console.log('[Patterns] Loading...');

// Get utilities from common.js
let fetchAPI, setElementText;

if (typeof window.dashboardUtils !== 'undefined') {
    fetchAPI = window.dashboardUtils.fetchAPI;
    setElementText = window.dashboardUtils.setElementText;
    console.log('[Patterns] Utilities loaded successfully');
} else {
    console.error('[Patterns] ERROR: window.dashboardUtils not available');
}

// ============================================================================
// INITIALIZE
// ============================================================================

async function initPatterns() {
    loadPatterns();

    // Refresh every 60 seconds
    setInterval(loadPatterns, 60000);

    // Refresh button
    document.getElementById('refresh-patterns-btn')?.addEventListener('click', loadPatterns);
}

// ============================================================================
// LOAD PATTERNS
// ============================================================================

async function loadPatterns() {
    const data = await fetchAPI('/patterns/latest?limit=20');
    if (data && data.patterns) {
        const container = document.getElementById('patterns-list');
        if (!container) return;

        container.innerHTML = '';

        if (data.patterns.length === 0) {
            container.innerHTML = '<div class="loading"><i class="fas fa-chart-area"></i> No patterns detected yet</div>';
            return;
        }

        // Calculate stats
        let totalPatterns = 0;
        let highConfidence = 0;
        let mediumConfidence = 0;

        // Get stats from API or calculate from data
        data.patterns.forEach(pattern => {
            totalPatterns++;
            const conf = pattern.confidence || 0;
            if (conf > 0.7) highConfidence++;
            else if (conf > 0.5) mediumConfidence++;
        });

        setElementText('patterns-total', totalPatterns);
        setElementText('patterns-high', highConfidence);
        setElementText('patterns-medium', mediumConfidence);

        // Display patterns
        data.patterns.forEach(pattern => {
            const confidence = pattern.confidence || 0;
            const confColor = confidence > 0.7 ? '#28a745' :
                            confidence > 0.5 ? '#ffc107' : '#6c757d';
            const confLabel = confidence > 0.7 ? 'High' :
                            confidence > 0.5 ? 'Medium' : 'Low';

            const card = document.createElement('div');
            card.className = 'pattern-card';
            card.style.borderLeftColor = confColor;

            card.innerHTML = `
                <div class="pattern-header">
                    <div>
                        <div class="pattern-symbol">${pattern.symbol}</div>
                        <div class="pattern-type">${pattern.pattern_type || 'Unknown'}</div>
                    </div>
                    <div class="confidence-badge" style="background: ${confColor};">
                        ${(confidence * 100).toFixed(0)}%
                    </div>
                </div>
                <div class="pattern-description">
                    ${pattern.description || 'Pattern detected in sentiment data and trading activity.'}
                </div>
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 0.8rem;
                    color: #999;
                ">
                    <span>Confidence: <strong style="color: ${confColor};">${confLabel}</strong></span>
                    <span>${new Date(pattern.timestamp).toLocaleDateString()}</span>
                </div>
            `;

            container.appendChild(card);
        });
    }
}

// ============================================================================
// DOCUMENT READY
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initPatterns();
});
