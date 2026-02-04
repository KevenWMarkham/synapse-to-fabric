/**
 * DMTSP Fabric Migration Accelerators - ROI Calculator
 * Calculates projected savings based on engagement parameters
 */

// Estimation constants based on the accelerator document
const ESTIMATES = {
    // Per-object base hours
    tables: {
        baseHoursPerUnit: 4,
        reduction: 0.475  // Average of 40-55%
    },
    views: {
        baseHoursPerUnit: 1.5,
        reduction: 0.475
    },
    storedProcs: {
        baseHoursPerUnit: 2,
        reduction: 0.30  // Average of 25-35%
    },
    sparkProcs: {
        baseHoursPerUnit: 16,  // Weighted average of 8/16/24
        reduction: 0.175  // Average of 15-20%
    },
    pipelines: {
        baseHoursPerUnit: 2,
        reduction: 0.40  // Average of 30-50%
    },
    datasets: {
        baseHoursPerUnit: 2,
        reduction: 0.50  // Average of 40-60%
    },
    logicApps: {
        baseHoursPerUnit: 2,
        reduction: 0.20  // Average of 15-25%
    },
    adlsAccounts: {
        baseHoursPerUnit: 4,
        reduction: 0.30  // Average of 20-40%
    }
};

// Environment deployment overhead (applied to Dev total)
const ENVIRONMENT_OVERHEAD = {
    sit: {
        percentage: 0.20,
        reduction: 0.25  // Average of 20-30%
    },
    uat: {
        percentage: 0.10,
        reduction: 0.20  // Average of 15-25%
    },
    prod: {
        percentage: 0.03,
        reduction: 0.15  // Average of 10-20%
    }
};

// Copilot compound effect
const COPILOT_COMPOUND = 0.075;  // 5-10% additional

/**
 * Calculate ROI based on user inputs
 */
function calculateROI() {
    // Get input values
    const inputs = {
        tables: parseInt(document.getElementById('tables').value) || 0,
        views: parseInt(document.getElementById('views').value) || 0,
        storedProcs: parseInt(document.getElementById('storedProcs').value) || 0,
        sparkProcs: parseInt(document.getElementById('sparkProcs').value) || 0,
        pipelines: parseInt(document.getElementById('pipelines').value) || 0,
        datasets: parseInt(document.getElementById('datasets').value) || 0,
        logicApps: parseInt(document.getElementById('logicApps').value) || 0,
        adlsAccounts: parseInt(document.getElementById('adlsAccounts').value) || 0,
        hourlyRate: parseInt(document.getElementById('hourlyRate').value) || 175
    };

    // Calculate base hours by workstream
    const workstreams = {
        'Synapse DW': {
            base: (inputs.tables * ESTIMATES.tables.baseHoursPerUnit) +
                  (inputs.views * ESTIMATES.views.baseHoursPerUnit),
            reduction: ESTIMATES.tables.reduction
        },
        'Stored Procs': {
            base: (inputs.storedProcs * ESTIMATES.storedProcs.baseHoursPerUnit) +
                  (inputs.sparkProcs * ESTIMATES.sparkProcs.baseHoursPerUnit),
            reduction: (inputs.storedProcs * ESTIMATES.storedProcs.reduction * ESTIMATES.storedProcs.baseHoursPerUnit +
                       inputs.sparkProcs * ESTIMATES.sparkProcs.reduction * ESTIMATES.sparkProcs.baseHoursPerUnit) /
                       ((inputs.storedProcs * ESTIMATES.storedProcs.baseHoursPerUnit) +
                        (inputs.sparkProcs * ESTIMATES.sparkProcs.baseHoursPerUnit) || 1)
        },
        'ADF Migration': {
            base: (inputs.pipelines * ESTIMATES.pipelines.baseHoursPerUnit) +
                  (inputs.datasets * ESTIMATES.datasets.baseHoursPerUnit),
            reduction: ((inputs.pipelines * ESTIMATES.pipelines.reduction * ESTIMATES.pipelines.baseHoursPerUnit) +
                       (inputs.datasets * ESTIMATES.datasets.reduction * ESTIMATES.datasets.baseHoursPerUnit)) /
                       ((inputs.pipelines * ESTIMATES.pipelines.baseHoursPerUnit) +
                        (inputs.datasets * ESTIMATES.datasets.baseHoursPerUnit) || 1)
        },
        'Logic/ADLS': {
            base: (inputs.logicApps * ESTIMATES.logicApps.baseHoursPerUnit) +
                  (inputs.adlsAccounts * ESTIMATES.adlsAccounts.baseHoursPerUnit),
            reduction: ((inputs.logicApps * ESTIMATES.logicApps.reduction * ESTIMATES.logicApps.baseHoursPerUnit) +
                       (inputs.adlsAccounts * ESTIMATES.adlsAccounts.reduction * ESTIMATES.adlsAccounts.baseHoursPerUnit)) /
                       ((inputs.logicApps * ESTIMATES.logicApps.baseHoursPerUnit) +
                        (inputs.adlsAccounts * ESTIMATES.adlsAccounts.baseHoursPerUnit) || 1)
        }
    };

    // Calculate development total
    let devBase = 0;
    let devAccelerated = 0;

    Object.keys(workstreams).forEach(key => {
        const ws = workstreams[key];
        devBase += ws.base;
        devAccelerated += ws.base * (1 - ws.reduction);
    });

    // Apply Copilot compound effect
    devAccelerated = devAccelerated * (1 - COPILOT_COMPOUND);

    // Calculate environment hours
    const envBase = devBase * (ENVIRONMENT_OVERHEAD.sit.percentage +
                               ENVIRONMENT_OVERHEAD.uat.percentage +
                               ENVIRONMENT_OVERHEAD.prod.percentage);

    const envAccelerated = (devBase * ENVIRONMENT_OVERHEAD.sit.percentage * (1 - ENVIRONMENT_OVERHEAD.sit.reduction)) +
                          (devBase * ENVIRONMENT_OVERHEAD.uat.percentage * (1 - ENVIRONMENT_OVERHEAD.uat.reduction)) +
                          (devBase * ENVIRONMENT_OVERHEAD.prod.percentage * (1 - ENVIRONMENT_OVERHEAD.prod.reduction));

    // Add environment workstream
    workstreams['Environments'] = {
        base: envBase,
        reduction: 1 - (envAccelerated / envBase)
    };

    // Total calculations
    const totalBase = devBase + envBase;
    const totalAccelerated = devAccelerated + envAccelerated;
    const totalSaved = totalBase - totalAccelerated;
    const efficiencyGain = (totalSaved / totalBase) * 100;

    // Update display
    document.getElementById('baseHours').textContent = formatNumber(Math.round(totalBase));
    document.getElementById('acceleratedHours').textContent = formatNumber(Math.round(totalAccelerated));
    document.getElementById('savedHours').textContent = formatNumber(Math.round(totalSaved));
    document.getElementById('costSavings').textContent = '$' + formatNumber(Math.round(totalSaved * inputs.hourlyRate));

    // Update efficiency meter
    const efficiencyBar = document.getElementById('efficiencyBar');
    const efficiencyValue = document.getElementById('efficiencyValue');
    efficiencyBar.style.width = efficiencyGain + '%';
    efficiencyValue.textContent = efficiencyGain.toFixed(1) + '%';

    // Update breakdown bars
    updateBreakdownBars(workstreams);
}

/**
 * Update the savings breakdown visualization
 */
function updateBreakdownBars(workstreams) {
    const container = document.getElementById('breakdownBars');
    container.innerHTML = '';

    // Find max for scaling
    const maxSaved = Math.max(...Object.values(workstreams).map(ws => ws.base * ws.reduction));

    Object.keys(workstreams).forEach(key => {
        const ws = workstreams[key];
        const saved = Math.round(ws.base * ws.reduction);
        const percentage = (saved / maxSaved) * 100;

        const item = document.createElement('div');
        item.className = 'breakdown-item';
        item.innerHTML = `
            <span class="breakdown-label">${key}</span>
            <div class="breakdown-bar-container">
                <div class="breakdown-bar" style="width: ${percentage}%"></div>
            </div>
            <span class="breakdown-value">${formatNumber(saved)} hrs</span>
        `;
        container.appendChild(item);
    });
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Initialize calculator on page load
document.addEventListener('DOMContentLoaded', function() {
    calculateROI();
});
