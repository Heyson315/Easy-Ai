/**
 * M365 Security Toolkit - Main JavaScript
 * Interactive functionality for GitHub Pages
 * Version: 1.0.0
 */

(function() {
    'use strict';

    // ========================================
    // Mobile Navigation
    // ========================================
    function initMobileMenu() {
        const toggle = document.querySelector('.mobile-menu-toggle');
        const nav = document.querySelector('.navbar-nav');
        
        if (toggle && nav) {
            toggle.addEventListener('click', function() {
                nav.classList.toggle('mobile-active');
                
                // Update ARIA attributes
                const isExpanded = nav.classList.contains('mobile-active');
                toggle.setAttribute('aria-expanded', isExpanded);
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!toggle.contains(e.target) && !nav.contains(e.target)) {
                    nav.classList.remove('mobile-active');
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });
            
            // Close menu when link is clicked
            const navLinks = nav.querySelectorAll('a');
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    nav.classList.remove('mobile-active');
                    toggle.setAttribute('aria-expanded', 'false');
                });
            });
        }
    }

    // ========================================
    // Smooth Scrolling
    // ========================================
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                
                // Skip empty anchors
                if (href === '#' || href === '#!') {
                    e.preventDefault();
                    return;
                }
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    
                    // Get navbar height for offset
                    const navbar = document.querySelector('.navbar');
                    const offset = navbar ? navbar.offsetHeight : 0;
                    
                    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                    
                    // Update URL without jumping
                    if (history.pushState) {
                        history.pushState(null, null, href);
                    }
                }
            });
        });
    }

    // ========================================
    // Sticky Navigation
    // ========================================
    function initStickyNav() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        let lastScroll = 0;
        
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;
            
            // Add shadow when scrolled
            if (currentScroll > 10) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            
            lastScroll = currentScroll;
        });
    }

    // ========================================
    // Form Validation
    // ========================================
    function initFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                let isValid = true;
                const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
                
                inputs.forEach(input => {
                    if (!validateInput(input)) {
                        isValid = false;
                    }
                });
                
                if (isValid) {
                    // Form is valid, submit it
                    if (form.dataset.formspree) {
                        // Handle Formspree submission
                        submitFormspree(form);
                    } else {
                        form.submit();
                    }
                }
            });
            
            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    if (this.hasAttribute('required')) {
                        validateInput(this);
                    }
                });
            });
        });
    }

    function validateInput(input) {
        const value = input.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        // Required validation
        if (input.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Email validation
        if (isValid && input.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }
        
        // Phone validation
        if (isValid && input.type === 'tel' && value) {
            const phoneRegex = /^[\d\s\-\+\(\)]+$/;
            if (!phoneRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number';
            }
        }
        
        // Display error
        displayError(input, isValid, errorMessage);
        
        return isValid;
    }

    function displayError(input, isValid, message) {
        const formGroup = input.closest('.form-group') || input.parentElement;
        let errorElement = formGroup.querySelector('.error-message');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            formGroup.appendChild(errorElement);
        }
        
        if (isValid) {
            input.classList.remove('error');
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        } else {
            input.classList.add('error');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    function submitFormspree(form) {
        const formData = new FormData(form);
        const action = form.action;
        
        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Sending...';
        submitButton.disabled = true;
        
        fetch(action, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.ok) {
                // Success
                showNotification('Thank you! Your message has been sent.', 'success');
                form.reset();
            } else {
                // Error
                showNotification('Oops! There was a problem submitting your form.', 'error');
            }
        })
        .catch(error => {
            showNotification('Oops! There was a problem submitting your form.', 'error');
        })
        .finally(() => {
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        });
    }

    // ========================================
    // Notifications
    // ========================================
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.setAttribute('role', 'alert');
        
        document.body.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }

    // ========================================
    // Analytics (Optional)
    // ========================================
    function initAnalytics() {
        // Track button clicks
        document.querySelectorAll('a.btn, button').forEach(element => {
            element.addEventListener('click', function() {
                const action = this.textContent.trim();
                const category = this.classList.contains('btn-primary') ? 'Primary CTA' : 'Secondary Action';
                
                // If Google Analytics is loaded
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'click', {
                        'event_category': category,
                        'event_label': action
                    });
                }
            });
        });
    }

    // ========================================
    // Copy to Clipboard
    // ========================================
    function initCopyButtons() {
        const copyButtons = document.querySelectorAll('[data-copy]');
        
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.dataset.copy;
                const target = document.querySelector(targetId);
                
                if (target) {
                    const text = target.textContent || target.value;
                    
                    navigator.clipboard.writeText(text).then(() => {
                        const originalText = button.textContent;
                        button.textContent = 'Copied!';
                        button.classList.add('copied');
                        
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.classList.remove('copied');
                        }, 2000);
                    }).catch(err => {
                        console.error('Failed to copy text: ', err);
                    });
                }
            });
        });
    }

    // ========================================
    // Lazy Loading Images
    // ========================================
    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for browsers without IntersectionObserver
            images.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
    }

    // ========================================
    // Date/Time Utilities
    // ========================================
    function updateDynamicDates() {
        const dateElements = document.querySelectorAll('[data-date="today"]');
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        
        dateElements.forEach(element => {
            element.textContent = formattedDate;
        });
        
        // Next month dates
        const nextMonthElements = document.querySelectorAll('[data-date="next-month"]');
        const nextMonth = new Date(today);
        nextMonth.setMonth(nextMonth.getMonth() + 1);
        const formattedNextMonth = nextMonth.toISOString().split('T')[0];
        
        nextMonthElements.forEach(element => {
            element.textContent = formattedNextMonth;
        });
    }

    // ========================================
    // Tooltip/Popover
    // ========================================
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            const tooltipText = element.dataset.tooltip;
            
            element.addEventListener('mouseenter', function(e) {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = tooltipText;
                tooltip.setAttribute('role', 'tooltip');
                
                document.body.appendChild(tooltip);
                
                const rect = element.getBoundingClientRect();
                tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                
                element.tooltipElement = tooltip;
            });
            
            element.addEventListener('mouseleave', function() {
                if (this.tooltipElement) {
                    this.tooltipElement.remove();
                    this.tooltipElement = null;
                }
            });
        });
    }

    // ========================================
    // Initialize on DOM Ready
    // ========================================
    function init() {
        initMobileMenu();
        initSmoothScroll();
        initStickyNav();
        initFormValidation();
        initCopyButtons();
        initLazyLoading();
        updateDynamicDates();
        initTooltips();
        
        // Optional analytics
        // initAnalytics();
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose some utilities globally
    window.M365Toolkit = {
        showNotification: showNotification,
        updateDynamicDates: updateDynamicDates
    };

})();
