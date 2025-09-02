/**
 * Political Discourse Analyzer - Main JavaScript
 * Provides interactive functionality and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    setupFormValidation();
    setupInteractiveElements();
    setupTooltips();
    setupAnimations();
    setupAccessibility();
}

/**
 * Setup form validation and enhancements
 */
function setupFormValidation() {
    // Enhanced form validation for politician name input
    const politicianNameInput = document.getElementById('politician_name');
    if (politicianNameInput) {
        politicianNameInput.addEventListener('input', function() {
            validatePoliticianName(this);
        });
        
        politicianNameInput.addEventListener('blur', function() {
            validatePoliticianName(this, true);
        });
    }
    
    // Analysis form validation
    const analysisForm = document.getElementById('analysisForm');
    if (analysisForm) {
        analysisForm.addEventListener('submit', function(e) {
            if (!validateAnalysisForm(this)) {
                e.preventDefault();
                return false;
            }
        });
    }
    
}

/**
 * Validate politician name input
 */
function validatePoliticianName(input, showFeedback = false) {
    const value = input.value.trim();
    const isValid = /^[A-Za-z\s\-\.']+$/.test(value) && value.length >= 2;
    
    // Remove existing validation classes
    input.classList.remove('is-valid', 'is-invalid');
    
    // Remove existing feedback
    const existingFeedback = input.parentNode.querySelector('.invalid-feedback, .valid-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    if (value.length > 0) {
        if (isValid) {
            input.classList.add('is-valid');
            if (showFeedback) {
                showInputFeedback(input, 'Valid politician name', 'valid');
            }
        } else {
            input.classList.add('is-invalid');
            if (showFeedback) {
                showInputFeedback(input, 'Please enter a valid name (letters, spaces, hyphens, periods, and apostrophes only)', 'invalid');
            }
        }
    }
    
    return isValid;
}


/**
 * Validate entire analysis form
 */
function validateAnalysisForm(form) {
    const politicianName = form.querySelector('#politician_name');
    
    let isValid = true;
    
    // Validate politician name
    if (!validatePoliticianName(politicianName, true)) {
        isValid = false;
    }
    
    return isValid;
}

/**
 * Show input validation feedback
 */
function showInputFeedback(input, message, type) {
    const feedback = document.createElement('div');
    feedback.className = `${type}-feedback`;
    feedback.textContent = message;
    input.parentNode.appendChild(feedback);
}

/**
 * Setup interactive elements
 */
function setupInteractiveElements() {
    // Sample politician selection
    setupSamplePoliticianSelection();
    
    // Copy to clipboard functionality
    setupCopyToClipboard();
    
    // Progress animation helpers
    setupProgressAnimations();
    
    // Card hover effects
    setupCardHoverEffects();
    
    // Smooth scrolling
    setupSmoothScrolling();
}

/**
 * Setup sample politician quick-select functionality
 */
function setupSamplePoliticianSelection() {
    const samplePoliticians = document.querySelectorAll('.list-unstyled li');
    
    samplePoliticians.forEach(item => {
        if (item.textContent.trim()) {
            item.style.cursor = 'pointer';
            item.classList.add('clickable');
            
            // Add hover effect
            item.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(0, 86, 179, 0.1)';
                this.style.borderRadius = '6px';
                this.style.padding = '0.25rem 0.5rem';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
                this.style.padding = '';
            });
            
            // Add click functionality
            item.addEventListener('click', function() {
                const name = this.textContent.trim();
                const nameInput = document.getElementById('politician_name');
                const countrySelect = document.getElementById('country');
                
                if (nameInput) {
                    nameInput.value = name;
                    validatePoliticianName(nameInput);
                    
                    // Add visual feedback
                    nameInput.style.backgroundColor = '#d4edda';
                    setTimeout(() => {
                        nameInput.style.backgroundColor = '';
                    }, 1000);
                }
                
                // Set appropriate country
                if (countrySelect) {
                    const countryMappings = {
                        'Barack Obama': 'USA',
                        'Joe Biden': 'USA',
                        'Donald Trump': 'USA',
                        'Hillary Clinton': 'USA',
                        'Winston Churchill': 'UK',
                        'Angela Merkel': 'Germany',
                        'Justin Trudeau': 'Canada',
                        'Emmanuel Macron': 'France'
                    };
                    
                    const country = countryMappings[name];
                    if (country) {
                        countrySelect.value = country;
                    }
                }
                
                // Show success message
                showTemporaryMessage('Politician selected: ' + name, 'success');
            });
        }
    });
}

/**
 * Setup copy to clipboard functionality
 */
function setupCopyToClipboard() {
    // Add copy buttons to code blocks or data sections
    const copyableElements = document.querySelectorAll('[data-copyable]');
    
    copyableElements.forEach(element => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-2';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.style.zIndex = '10';
        
        element.style.position = 'relative';
        element.appendChild(copyBtn);
        
        copyBtn.addEventListener('click', function() {
            const text = element.textContent || element.innerText;
            navigator.clipboard.writeText(text).then(() => {
                this.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-copy"></i>';
                }, 2000);
            });
        });
    });
}

/**
 * Setup progress animations
 */
function setupProgressAnimations() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const originalWidth = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = originalWidth;
        }, 100);
    });
}

/**
 * Setup card hover effects
 */
function setupCardHoverEffects() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 25px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}

/**
 * Setup smooth scrolling
 */
function setupSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Setup tooltips
 */
function setupTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Custom tooltips for form elements
    const formInputs = document.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        if (input.title) {
            input.addEventListener('focus', function() {
                showTooltip(this, this.title);
            });
            
            input.addEventListener('blur', function() {
                hideTooltip(this);
            });
        }
    });
}

/**
 * Show custom tooltip
 */
function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #333;
        color: white;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.bottom + 5) + 'px';
    
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 100);
    
    element._tooltip = tooltip;
}

/**
 * Hide custom tooltip
 */
function hideTooltip(element) {
    if (element._tooltip) {
        element._tooltip.style.opacity = '0';
        setTimeout(() => {
            if (element._tooltip && element._tooltip.parentNode) {
                element._tooltip.parentNode.removeChild(element._tooltip);
            }
            element._tooltip = null;
        }, 300);
    }
}

/**
 * Setup animations
 */
function setupAnimations() {
    // Fade in animations for cards
    const animatedElements = document.querySelectorAll('.card, .alert');
    
    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Loading spinner animations
    setupLoadingSpinners();
}

/**
 * Setup loading spinners
 */
function setupLoadingSpinners() {
    const spinners = document.querySelectorAll('.fa-spinner');
    
    spinners.forEach(spinner => {
        spinner.style.animation = 'spin 1s linear infinite';
    });
    
    // Add CSS for spin animation if not exists
    if (!document.querySelector('#spin-animation-style')) {
        const style = document.createElement('style');
        style.id = 'spin-animation-style';
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Setup accessibility enhancements
 */
function setupAccessibility() {
    // Add ARIA labels to interactive elements
    const interactiveElements = document.querySelectorAll('.clickable, button, [role="button"]');
    
    interactiveElements.forEach(element => {
        if (!element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby')) {
            const text = element.textContent || element.title || 'Interactive element';
            element.setAttribute('aria-label', text.trim());
        }
    });
    
    // Keyboard navigation for custom interactive elements
    const customInteractives = document.querySelectorAll('.clickable');
    customInteractives.forEach(element => {
        if (!element.hasAttribute('tabindex')) {
            element.setAttribute('tabindex', '0');
        }
        
        element.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Focus management
    setupFocusManagement();
}

/**
 * Setup focus management
 */
function setupFocusManagement() {
    // Focus trap for modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const focusableElements = this.querySelectorAll('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (focusableElements.length > 0) {
                focusableElements[0].focus();
            }
        });
    });
    
    // Skip link functionality
    const skipLink = document.querySelector('.skip-link');
    if (skipLink) {
        skipLink.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.focus();
                target.scrollIntoView();
            }
        });
    }
}

/**
 * Utility Functions
 */

/**
 * Show temporary message
 */
function showTemporaryMessage(message, type = 'info', duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1050;
        min-width: 300px;
    `;
    
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : type === 'warning' ? 'exclamation-triangle' : 'info'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 300);
        }
    }, duration);
}

/**
 * Format numbers with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Debounce function
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
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Check if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Animate elements when they come into view
 */
function setupScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// Initialize scroll animations
document.addEventListener('DOMContentLoaded', function() {
    setupScrollAnimations();
});

// Export functions for use in other scripts
window.PoliticalAnalyzer = {
    showTemporaryMessage,
    formatNumber,
    debounce,
    throttle,
    isInViewport
};
