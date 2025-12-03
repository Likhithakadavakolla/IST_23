// Global variables
let currentLanguage = 'en';
let translations = {};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize navigation
    initializeNavigation();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize multilingual support
    initializeLanguageSupport();
    
    // Initialize smooth scrolling
    initializeSmoothScrolling();
}

// Navigation functionality
function initializeNavigation() {
    const hamburger = document.querySelector('.nav-hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
        
        // Close mobile menu when clicking on a link
        const navLinks = document.querySelectorAll('.nav-menu a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!hamburger.contains(event.target) && !navMenu.contains(event.target)) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    }
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });

    // Profile dropdown toggle
    const profileBtn = document.getElementById('profileBtn');
    const profileDropdown = document.getElementById('profileDropdown');
    if (profileBtn && profileDropdown) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            profileDropdown.classList.toggle('show');
        });
        document.addEventListener('click', (e) => {
            if (!profileDropdown.contains(e.target) && e.target !== profileBtn) {
                profileDropdown.classList.remove('show');
            }
        });
    }
}

// Animation functionality
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Observe all elements with fade-in class
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(el => observer.observe(el));
    
    // Add stagger delay for grids
    const gridContainers = document.querySelectorAll('.features-grid, .courses-grid, .progress-stats');
    gridContainers.forEach(container => {
        const items = container.querySelectorAll('.fade-in');
        items.forEach((item, index) => {
            item.style.transitionDelay = `${index * 0.1}s`;
        });
    });
}

// Smooth scrolling functionality
function initializeSmoothScrolling() {
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Multilingual support
function initializeLanguageSupport() {
    const languageSelect = document.getElementById('languageSelect');
    
    if (languageSelect) {
        // Load saved language preference
        const savedLanguage = localStorage.getItem('preferred-language');
        if (savedLanguage) {
            currentLanguage = savedLanguage;
            languageSelect.value = savedLanguage;
            loadTranslations(savedLanguage);
        } else {
            loadTranslations('en');
        }
        
        // Language change handler
        languageSelect.addEventListener('change', function(e) {
            const selectedLanguage = e.target.value;
            currentLanguage = selectedLanguage;
            localStorage.setItem('preferred-language', selectedLanguage);
            loadTranslations(selectedLanguage);
        });
    }
}

async function loadTranslations(language) {
    try {
        const response = await fetch(`/api/translations/${language}`);
        if (response.ok) {
            translations = await response.json();
            // expose for other scripts
            window.__translations = translations;
            if (!window.EduReachI18n) {
                window.EduReachI18n = { get: (key, fallback = '') => (window.__translations && window.__translations[key]) || fallback || key };
            }
            applyTranslations();
            // notify pages that dynamic content can be re-rendered
            document.dispatchEvent(new CustomEvent('languageChanged', { detail: { language, translations } }));
        }
    } catch (error) {
        console.error('Error loading translations:', error);
    }
}

function applyTranslations() {
    const elementsToTranslate = document.querySelectorAll('[data-translate]');
    
    elementsToTranslate.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[key]) {
            element.textContent = translations[key];
        }
    });
    
    // Update document title if translation exists
    if (translations.title) {
        const currentTitle = document.title;
        if (currentTitle.includes('EduReach')) {
            document.title = currentTitle.replace('EduReach', translations.title);
        }
    }
    
    // Update meta description if available
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription && translations.tagline) {
        metaDescription.setAttribute('content', translations.tagline);
    }
}

// Utility functions
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
    }
}

// Form validation utilities
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function showNotification(message, type = 'success', duration = 5000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(notification);
    
    // Slide in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Close functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        removeNotification(notification);
    });
    
    // Auto remove after duration
    setTimeout(() => {
        removeNotification(notification);
    }, duration);
}

function removeNotification(notification) {
    if (notification && notification.parentNode) {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }
}

// Loading spinner utility
function showLoadingSpinner(element, text = 'Loading...') {
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;
    element.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <span class="loading-text">${text}</span>
        </div>
    `;
    element.disabled = true;
}

function hideLoadingSpinner(element) {
    const originalContent = element.dataset.originalContent;
    if (originalContent) {
        element.innerHTML = originalContent;
        delete element.dataset.originalContent;
    }
    element.disabled = false;
}

// API utility functions
async function makeApiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Progress tracking utilities
function updateProgressBar(progressElement, percentage, animated = true) {
    const progressFill = progressElement.querySelector('.progress-fill');
    const progressText = progressElement.querySelector('.progress-text');
    
    if (progressFill) {
        if (animated) {
            progressFill.style.transition = 'width 1s ease-in-out';
        }
        progressFill.style.width = `${percentage}%`;
    }
    
    if (progressText) {
        progressText.textContent = `${Math.round(percentage)}% completed`;
    }
}

function calculateProgress(completed, total) {
    if (total === 0) return 0;
    return Math.round((completed / total) * 100);
}

// Chart utilities (for progress page)
function createProgressChart(ctx, data, type = 'bar') {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded');
        return null;
    }
    
    const config = {
        type: type,
        data: data,
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
    
    return new Chart(ctx, config);
}

// Video modal utilities
function openVideoModal(videoUrl, title, description) {
    const modal = document.getElementById('videoModal');
    const iframe = document.getElementById('videoFrame');
    const titleElement = document.getElementById('videoTitle');
    const descriptionElement = document.getElementById('videoDescription');
    
    if (modal && iframe) {
        iframe.src = videoUrl;
        if (titleElement) titleElement.textContent = title;
        if (descriptionElement) descriptionElement.textContent = description;
        
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
}

function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    const iframe = document.getElementById('videoFrame');
    
    if (modal && iframe) {
        modal.style.display = 'none';
        iframe.src = ''; // Stop video playback
        document.body.style.overflow = ''; // Restore scrolling
    }
}

// Local storage utilities
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        return defaultValue;
    }
}

// Performance monitoring
function measurePerformance(name, fn) {
    const startTime = performance.now();
    const result = fn();
    const endTime = performance.now();
    console.log(`${name} took ${endTime - startTime} milliseconds`);
    return result;
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showNotification('An unexpected error occurred. Please refresh the page.', 'error');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showNotification('A network error occurred. Please check your connection.', 'error');
});

// Accessibility improvements
function addAccessibilityFeatures() {
    // Add skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        left: -10000px;
        top: auto;
        width: 1px;
        height: 1px;
        overflow: hidden;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.cssText = `
            position: static;
            width: auto;
            height: auto;
            overflow: visible;
            background: #000;
            color: #fff;
            padding: 0.5rem;
            text-decoration: none;
            z-index: 10000;
        `;
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.cssText = `
            position: absolute;
            left: -10000px;
            top: auto;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content id if it doesn't exist
    const mainContent = document.querySelector('.main-content');
    if (mainContent && !mainContent.id) {
        mainContent.id = 'main-content';
    }
}

// Initialize accessibility features
document.addEventListener('DOMContentLoaded', addAccessibilityFeatures);

// Export utilities for use in other scripts
window.EduReachUtils = {
    showNotification,
    showLoadingSpinner,
    hideLoadingSpinner,
    makeApiRequest,
    updateProgressBar,
    calculateProgress,
    createProgressChart,
    openVideoModal,
    closeVideoModal,
    validateEmail,
    validatePassword,
    saveToLocalStorage,
    loadFromLocalStorage,
    debounce,
    throttle,
    measurePerformance
};