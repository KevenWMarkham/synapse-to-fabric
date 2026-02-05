/**
 * DMTSP Fabric Migration Accelerators - Main JavaScript
 * Handles UI interactions, accordion functionality, and navigation
 */

/**
 * Toggle accelerator accordion panels
 */
function toggleAccelerator(num) {
    const card = document.getElementById('acc-' + num);
    const isOpen = card.classList.contains('open');

    // Close all other cards
    document.querySelectorAll('.accelerator-card').forEach(c => {
        c.classList.remove('open');
    });

    // Toggle current card
    if (!isOpen) {
        card.classList.add('open');

        // Smooth scroll to card
        setTimeout(() => {
            card.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

/**
 * Smooth scroll navigation
 */
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.overview-card, .accelerator-card, .summary-card, .result-card').forEach(el => {
        observer.observe(el);
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });

    // Active nav link highlighting
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links a');

    window.addEventListener('scroll', () => {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;

            if (window.pageYOffset >= sectionTop && window.pageYOffset < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });

    // Input field formatting
    document.querySelectorAll('.calc-inputs input[type="number"]').forEach(input => {
        input.addEventListener('focus', function() {
            this.select();
        });

        input.addEventListener('change', function() {
            calculateROI();
        });

        input.addEventListener('keyup', debounce(function() {
            calculateROI();
        }, 300));
    });

    // Initialize first accelerator as open
    toggleAccelerator(1);

    // Render sprint plan cards
    renderSprints();

    // Observe sprint cards for animation
    document.querySelectorAll('.sprint-card, .comparison-card').forEach(el => {
        observer.observe(el);
    });
});

/**
 * Debounce function for input handling
 */
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

/**
 * Print-friendly export
 */
function exportToPDF() {
    window.print();
}

/**
 * Copy results to clipboard
 */
function copyResults() {
    const base = document.getElementById('baseHours').textContent;
    const accelerated = document.getElementById('acceleratedHours').textContent;
    const saved = document.getElementById('savedHours').textContent;
    const cost = document.getElementById('costSavings').textContent;
    const efficiency = document.getElementById('efficiencyValue').textContent;

    const text = `DMTSP Fabric Migration Accelerator Analysis
---------------------------------------
Base Estimate: ${base} hours
With Accelerators: ${accelerated} hours
Hours Saved: ${saved} hours
Cost Savings: ${cost}
Overall Efficiency Gain: ${efficiency}

Generated by DMTSP Accelerator Calculator`;

    navigator.clipboard.writeText(text).then(() => {
        alert('Results copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

/**
 * Add keyboard accessibility
 */
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        // Close all accordions on Escape
        document.querySelectorAll('.accelerator-card').forEach(c => {
            c.classList.remove('open');
        });
    }
});

/**
 * Sprint Plan — Phase Toggle
 */
function togglePhase(phase) {
    const phase1Container = document.getElementById('phase1-sprints');
    const phase2Container = document.getElementById('phase2-sprints');
    const buttons = document.querySelectorAll('.phase-btn');

    if (phase === 'phase1') {
        phase1Container.style.display = '';
        phase2Container.style.display = 'none';
        buttons[0].classList.add('active');
        buttons[1].classList.remove('active');
    } else {
        phase1Container.style.display = 'none';
        phase2Container.style.display = '';
        buttons[0].classList.remove('active');
        buttons[1].classList.add('active');
    }
}

/**
 * Sprint Plan — Toggle individual sprint card
 */
function toggleSprint(phase, sprintId) {
    const container = document.getElementById(phase + '-sprints');
    const card = container.querySelector('[data-sprint="' + sprintId + '"]');
    const isOpen = card.classList.contains('open');

    // Close all other sprint cards in this phase
    container.querySelectorAll('.sprint-card').forEach(c => {
        c.classList.remove('open');
    });

    // Toggle current card
    if (!isOpen) {
        card.classList.add('open');
        setTimeout(() => {
            card.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

/**
 * Sprint Plan — Render sprint cards from data
 */
function renderSprints() {
    renderPhase('phase1', PHASE1_SPRINTS, false);
    renderPhase('phase2', PHASE2_SPRINTS, true);
    renderCalloutBreakdown();
}

function renderPhase(phaseId, sprints, showAccelerator) {
    const container = document.getElementById(phaseId + '-sprints');
    if (!container) return;

    container.innerHTML = sprints.map(sprint => {
        const taskRows = sprint.tasks.map(t => {
            let cols = `
                <td><span class="task-name">${escapeHtml(t.task)}</span><br><span class="task-subtasks">${escapeHtml(t.subtasks)}</span></td>
                <td>${t.hours}</td>
                <td>${escapeHtml(t.owners)}</td>`;
            if (showAccelerator) {
                cols += `<td class="task-accelerator">${escapeHtml(t.accelerator || '\u2014')}</td>`;
            }
            return '<tr>' + cols + '</tr>';
        }).join('');

        const accHeader = showAccelerator ? '<th>Accelerator</th>' : '';

        const milestonesHtml = sprint.milestones.length > 0
            ? `<div class="sprint-milestones">${sprint.milestones.map(m =>
                `<span class="milestone-badge">${escapeHtml(m)}</span>`
              ).join('')}</div>`
            : '';

        return `
        <div class="sprint-card" data-sprint="${sprint.id}">
            <div class="sprint-header" onclick="toggleSprint('${phaseId}', ${sprint.id})">
                <div class="sprint-number">${sprint.id}</div>
                <div class="sprint-info">
                    <h4>${escapeHtml(sprint.name)}</h4>
                </div>
                <div class="sprint-hours">
                    ${formatNumber(sprint.hours)}
                    <span>hours</span>
                </div>
                <svg class="sprint-toggle" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"/>
                </svg>
            </div>
            <div class="sprint-content">
                <table class="sprint-task-table">
                    <thead>
                        <tr>
                            <th>Task</th>
                            <th>Hours</th>
                            <th>Owner(s)</th>
                            ${accHeader}
                        </tr>
                    </thead>
                    <tbody>${taskRows}</tbody>
                </table>
                ${milestonesHtml}
            </div>
        </div>`;
    }).join('');
}

function renderCalloutBreakdown() {
    const container = document.getElementById('calloutBreakdown');
    if (!container) return;

    container.innerHTML = ADDITIONAL_WORK.breakdown.map(item =>
        `<div class="callout-item">
            <span class="callout-item-label">${escapeHtml(item.workstream)}</span>
            <span class="callout-item-value">+${formatNumber(item.hoursSaved)} hrs</span>
        </div>`
    ).join('');
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Make functions available globally
window.toggleAccelerator = toggleAccelerator;
window.exportToPDF = exportToPDF;
window.copyResults = copyResults;
window.togglePhase = togglePhase;
window.toggleSprint = toggleSprint;
