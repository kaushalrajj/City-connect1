// Main JavaScript for Team01 Project

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle with animation
    const mobileNavToggle = document.getElementById('mobile-nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileNavToggle) {
        mobileNavToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            navLinks.classList.toggle('show');
            this.classList.toggle('active');

            // Add slide-in animation to nav links
            const links = navLinks.querySelectorAll('a');
            if (navLinks.classList.contains('show')) {
                links.forEach((link, index) => {
                    link.style.animation = `slideIn 0.3s ease forwards ${index * 0.1}s`;
                    link.style.opacity = '0';
                    setTimeout(() => {
                        link.style.opacity = '1';
                    }, index * 100 + 50);
                });
            } else {
                links.forEach(link => {
                    link.style.animation = 'none';
                });
            }
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('nav') && navLinks.classList.contains('show')) {
                navLinks.classList.remove('show');
                mobileNavToggle.classList.remove('active');

                // Reset animations
                const links = navLinks.querySelectorAll('a');
                links.forEach(link => {
                    link.style.animation = 'none';
                });
            }
        });

        // Close mobile menu when window is resized to desktop
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768 && navLinks.classList.contains('show')) {
                navLinks.classList.remove('show');
                mobileNavToggle.classList.remove('active');

                // Reset animations
                const links = navLinks.querySelectorAll('a');
                links.forEach(link => {
                    link.style.animation = 'none';
                });
            }
        });
    }

    // Flash messages handling
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        // Auto-dismiss after 5 seconds
        flashMessages.forEach(message => {
            setTimeout(() => {
                dismissAlert(message);
            }, 5000);
        });

        // Handle manual dismissal
        const closeButtons = document.querySelectorAll('.alert .close');
        closeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const alert = this.closest('.alert');
                dismissAlert(alert);
            });
        });
    }

    // Function to dismiss alerts with animation
    function dismissAlert(alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            alert.style.height = '0';
            alert.style.margin = '0';
            alert.style.padding = '0';
            alert.style.border = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 300);
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');

                    // Create error message if it doesn't exist
                    let errorMessage = field.nextElementSibling;
                    if (!errorMessage || !errorMessage.classList.contains('error-message')) {
                        errorMessage = document.createElement('div');
                        errorMessage.classList.add('error-message');
                        errorMessage.textContent = 'This field is required';
                        field.parentNode.insertBefore(errorMessage, field.nextSibling);
                    }
                } else {
                    field.classList.remove('is-invalid');

                    // Remove error message if it exists
                    const errorMessage = field.nextElementSibling;
                    if (errorMessage && errorMessage.classList.contains('error-message')) {
                        errorMessage.remove();
                    }
                }
            });

            if (!isValid) {
                event.preventDefault();
            }
        });
    });

    // Password confirmation validation
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');

    if (passwordField && confirmPasswordField) {
        confirmPasswordField.addEventListener('input', function() {
            if (passwordField.value !== confirmPasswordField.value) {
                confirmPasswordField.setCustomValidity("Passwords don't match");
            } else {
                confirmPasswordField.setCustomValidity('');
            }
        });
    }

    // Image preview for file uploads
    const imageInput = document.querySelector('input[type="file"]');
    if (imageInput) {
        const previewContainer = document.createElement('div');
        previewContainer.classList.add('image-preview');
        previewContainer.innerHTML = '<p>Image Preview</p><div class="preview"></div>';
        imageInput.parentNode.insertBefore(previewContainer, imageInput.nextSibling);

        const preview = previewContainer.querySelector('.preview');

        imageInput.addEventListener('change', function() {
            while (preview.firstChild) {
                preview.removeChild(preview.firstChild);
            }

            const file = this.files[0];
            if (file) {
                const reader = new FileReader();

                reader.addEventListener('load', function() {
                    const image = new Image();
                    image.src = this.result;
                    image.classList.add('preview-image');
                    preview.appendChild(image);
                });

                reader.readAsDataURL(file);
            }
        });
    }
});
