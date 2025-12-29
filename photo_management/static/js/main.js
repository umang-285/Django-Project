/* ===============================================
   Photo Gallery - JavaScript
   =============================================== */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {

    // Initialize all components
    initLightbox();
    initFormValidation();
    initAnimations();
    initPasswordToggle();

});

/* ===============================================
   Lightbox Gallery
   =============================================== */

function initLightbox() {
    // Create lightbox element if it doesn't exist
    if (!document.querySelector('.lightbox')) {
        const lightbox = document.createElement('div');
        lightbox.className = 'lightbox';
        lightbox.id = 'lightbox';
        lightbox.innerHTML = `
            <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
            <img class="lightbox-img" id="lightbox-img" src="" alt="Full size image">
        `;
        document.body.appendChild(lightbox);
    }

    // Add click handlers to gallery items
    const galleryItems = document.querySelectorAll('.gallery-item');
    galleryItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const img = this.querySelector('.gallery-img');
            if (img) {
                openLightbox(img.src, img.alt);
            }
        });
    });

    // Close lightbox on background click
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        lightbox.addEventListener('click', function(e) {
            if (e.target === this) {
                closeLightbox();
            }
        });
    }

    // Close lightbox on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeLightbox();
        }
    });
}

function openLightbox(src, alt) {
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');

    if (lightbox && lightboxImg) {
        lightboxImg.src = src;
        lightboxImg.alt = alt || 'Full size image';
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeLightbox() {
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }
}

/* ===============================================
   Form Validation
   =============================================== */

function initFormValidation() {
    // Password strength indicator
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            validatePasswordStrength(this.value);
        });
    }

    // Real-time validation for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

function validatePasswordStrength(password) {
    const strengthIndicator = document.getElementById('password-strength');
    if (!strengthIndicator) return;

    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
    if (password.match(/\d/)) strength++;
    if (password.match(/[^a-zA-Z\d]/)) strength++;

    const strengthTexts = ['Weak', 'Fair', 'Good', 'Strong'];
    const strengthColors = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'];

    if (password.length > 0) {
        strengthIndicator.textContent = 'Strength: ' + strengthTexts[strength - 1];
        strengthIndicator.style.color = strengthColors[strength - 1];
        strengthIndicator.style.display = 'block';
    } else {
        strengthIndicator.style.display = 'none';
    }
}

function validateField(field) {
    const value = field.value.trim();
    const parent = field.closest('.form-group-custom');

    if (!parent) return;

    // Remove existing error message
    const existingError = parent.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }

    // Check if field is empty
    if (field.hasAttribute('required') && value === '') {
        showFieldError(field, 'This field is required');
        return false;
    }

    // Email validation
    if (field.type === 'email' && value !== '') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }

    // Remove error styling if validation passes
    field.style.borderColor = '#10b981';
    setTimeout(() => {
        field.style.borderColor = '';
    }, 2000);

    return true;
}

function showFieldError(field, message) {
    field.style.borderColor = '#ef4444';

    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#ef4444';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.5rem';
    errorDiv.textContent = message;

    const parent = field.closest('.form-group-custom');
    if (parent) {
        parent.appendChild(errorDiv);
    }
}

/* ===============================================
   Password Toggle
   =============================================== */

function initPasswordToggle() {
    // Add toggle buttons to password fields
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';

        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);

        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.innerHTML = '👁️';
        toggleBtn.style.cssText = `
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.25rem;
            opacity: 0.6;
            transition: opacity 0.3s ease;
        `;

        toggleBtn.addEventListener('click', function() {
            if (field.type === 'password') {
                field.type = 'text';
                this.innerHTML = '🙈';
            } else {
                field.type = 'password';
                this.innerHTML = '👁️';
            }
        });

        toggleBtn.addEventListener('mouseenter', function() {
            this.style.opacity = '1';
        });

        toggleBtn.addEventListener('mouseleave', function() {
            this.style.opacity = '0.6';
        });

        wrapper.appendChild(toggleBtn);
    });
}

/* ===============================================
   Scroll Animations
   =============================================== */

function initAnimations() {
    // Add intersection observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe cards
    const cards = document.querySelectorAll('.card-custom, .gallery-item');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `all 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });
}

/* ===============================================
   Smooth Scroll
   =============================================== */

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

/* ===============================================
   Alert Auto-dismiss
   =============================================== */

setTimeout(function() {
    const alerts = document.querySelectorAll('.alert-custom');
    alerts.forEach(alert => {
        alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            alert.remove();
        }, 500);
    });
}, 5000);

/* ===============================================
   Loading Indicator
   =============================================== */

// Show loading indicator on form submission
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.innerHTML = '<span class="loading-spinner" style="width: 20px; height: 20px; margin: 0 auto;"></span>';
            submitBtn.disabled = true;
        }
    });
});
