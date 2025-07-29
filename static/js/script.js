// File Server JavaScript Functions

// Copy to clipboard functionality
async function copyToClipboard(elementId) {
    try {
        const element = document.getElementById(elementId);
        const text = element.value || element.textContent;
        
        let success = false;
        
        // Method 1: Modern clipboard API (works on HTTPS and localhost)
        if (navigator.clipboard && (window.isSecureContext || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
            try {
                await navigator.clipboard.writeText(text);
                success = true;
            } catch (clipboardErr) {
                console.log('Clipboard API failed, trying fallback:', clipboardErr);
            }
        }
        
        // Method 2: Legacy execCommand fallback
        if (!success) {
            try {
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                textArea.style.opacity = '0';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                textArea.setSelectionRange(0, 99999); // For mobile devices
                
                const result = document.execCommand('copy');
                textArea.remove();
                
                if (result) {
                    success = true;
                } else {
                    throw new Error('execCommand failed');
                }
            } catch (execErr) {
                console.log('execCommand failed:', execErr);
            }
        }
        
        // Method 3: Manual selection for user to copy
        if (!success) {
            // Select the text in the input field
            element.focus();
            element.select();
            element.setSelectionRange(0, 99999); // For mobile devices
            
            showToast('Text selected! Press Ctrl+C (or Cmd+C on Mac) to copy', 'info');
            return;
        }
        
        // Show success feedback
        showToast('Copied to clipboard!', 'success');
        
        // Visual feedback on button
        const button = event.target.closest('button');
        if (button) {
            const originalIcon = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.classList.add('btn-success');
            button.classList.remove('btn-outline-secondary');
            
            setTimeout(() => {
                button.innerHTML = originalIcon;
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-secondary');
            }, 1500);
        }
        
    } catch (err) {
        console.error('Failed to copy text: ', err);
        
        // Final fallback - show the text in an alert
        const element = document.getElementById(elementId);
        const text = element.value || element.textContent;
        
        // Try to select the text for manual copying
        try {
            element.focus();
            element.select();
            showToast('Please manually copy the selected text (Ctrl+C)', 'warning');
        } catch (selectErr) {
            // Last resort - show in alert
            alert(`Copy this text manually:\n\n${text}`);
        }
    }
}

// Show toast notifications
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Map types to Bootstrap colors
    const typeColorMap = {
        'error': 'danger',
        'success': 'success',
        'warning': 'warning',
        'info': 'info'
    };
    
    const iconMap = {
        'error': 'exclamation-triangle',
        'success': 'check-circle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    
    const bgColor = typeColorMap[type] || 'info';
    const icon = iconMap[type] || 'info-circle';
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${bgColor} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    
    // Fallback if Bootstrap toast is not available
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: type === 'warning' || type === 'error' ? 5000 : 3000
        });
        
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    } else {
        // Manual fallback
        toastElement.style.display = 'block';
        setTimeout(() => {
            toastElement.style.opacity = '0';
            setTimeout(() => toastElement.remove(), 300);
        }, type === 'warning' || type === 'error' ? 5000 : 3000);
    }
}

// Refresh server information
async function refreshInfo() {
    try {
        const button = event.target;
        const originalContent = button.innerHTML;
        
        // Show loading state
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Refreshing...';
        button.disabled = true;
        
        // Fetch server info
        const response = await fetch('/api/server-info');
        const data = await response.json();
        
        // Update UI elements
        const serverUrl = document.getElementById('serverUrl');
        const serverPassword = document.getElementById('serverPassword');
        
        if (serverUrl) {
            serverUrl.value = data.url;
        }
        
        if (serverPassword) {
            serverPassword.value = data.password;
        }
        
        // Update QR code
        const qrImage = document.querySelector('.qr-code');
        if (qrImage) {
            qrImage.src = '/qr?' + new Date().getTime(); // Add timestamp to force refresh
        }
        
        showToast('Server information refreshed!', 'success');
        
    } catch (error) {
        console.error('Error refreshing server info:', error);
        showToast('Failed to refresh server information', 'error');
    } finally {
        // Restore button state
        const button = event.target;
        button.innerHTML = originalContent;
        button.disabled = false;
    }
}

// File drag and drop functionality
function initializeDragAndDrop() {
    const uploadModal = document.getElementById('uploadModal');
    const fileInput = document.getElementById('file');
    
    if (!uploadModal || !fileInput) return;
    
    // Add drag and drop styles
    const dropZoneHTML = `
        <div id="dropZone" class="drop-zone d-none">
            <div class="drop-zone-content">
                <i class="fas fa-cloud-upload-alt fa-3x mb-3"></i>
                <h5>Drop files here to upload</h5>
                <p class="text-muted">Or click to browse</p>
            </div>
        </div>
    `;
    
    const modalBody = uploadModal.querySelector('.modal-body');
    modalBody.insertAdjacentHTML('beforeend', dropZoneHTML);
    
    const dropZone = document.getElementById('dropZone');
    
    // Show drop zone when modal opens
    uploadModal.addEventListener('shown.bs.modal', () => {
        dropZone.classList.remove('d-none');
    });
    
    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        dropZone.classList.add('drag-over');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }
    
    dropZone.addEventListener('drop', handleDrop, false);
    dropZone.addEventListener('click', () => fileInput.click());
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            updateFileInfo(fileInput);
        }
    }
}

// Format file size helper
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Initialize file search functionality
function initializeSearch() {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Search files...';
    searchInput.id = 'fileSearch';
    
    const fileGrid = document.getElementById('fileGrid');
    if (fileGrid) {
        fileGrid.parentNode.insertBefore(searchInput, fileGrid);
        
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const fileItems = document.querySelectorAll('.file-item');
            
            fileItems.forEach(item => {
                const fileName = item.dataset.name;
                if (fileName.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
}

// Handle media player controls
function setupMediaPlayer() {
    // Add custom controls to video/audio elements
    document.addEventListener('DOMContentLoaded', () => {
        const mediaElements = document.querySelectorAll('video, audio');
        
        mediaElements.forEach(media => {
            media.addEventListener('loadstart', () => {
                console.log('Media loading started');
            });
            
            media.addEventListener('canplay', () => {
                console.log('Media can start playing');
            });
            
            media.addEventListener('error', (e) => {
                console.error('Media error:', e);
                showToast('Error loading media file', 'error');
            });
        });
    });
}

// Network status monitoring
function initializeNetworkMonitoring() {
    function updateNetworkStatus() {
        const isOnline = navigator.onLine;
        const statusBadge = document.querySelector('.badge.bg-success');
        
        if (statusBadge) {
            if (isOnline) {
                statusBadge.innerHTML = '<i class="fas fa-wifi me-1"></i>Online';
                statusBadge.className = 'badge bg-success me-2';
            } else {
                statusBadge.innerHTML = '<i class="fas fa-wifi-slash me-1"></i>Offline';
                statusBadge.className = 'badge bg-warning me-2';
            }
        }
    }
    
    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);
    
    // Initial check
    updateNetworkStatus();
}

// Add CSS for drag and drop
function addDragDropStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .drop-zone {
            border: 2px dashed #6c757d;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background-color: rgba(255, 255, 255, 0.05);
        }
        
        .drop-zone:hover,
        .drop-zone.drag-over {
            border-color: #0d6efd;
            background-color: rgba(13, 110, 253, 0.1);
        }
        
        .drop-zone-content {
            pointer-events: none;
        }
        
        .drop-zone i {
            color: #6c757d;
        }
        
        .drop-zone:hover i,
        .drop-zone.drag-over i {
            color: #0d6efd;
        }
    `;
    document.head.appendChild(style);
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add drag and drop styles
    addDragDropStyles();
    
    // Initialize features
    initializeDragAndDrop();
    initializeSearch();
    setupMediaPlayer();
    initializeNetworkMonitoring();
    
    // Register service worker for PWA functionality
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('Service Worker registered successfully:', registration.scope);
            })
            .catch(function(error) {
                console.log('Service Worker registration failed:', error);
            });
    }

    // PWA Install functionality
    let deferredPrompt;
    const installBtn = document.getElementById('installBtn');
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Show install button
        if (installBtn) {
            installBtn.style.display = 'block';
            installBtn.addEventListener('click', () => {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        showToast('App installed successfully!', 'success');
                        installBtn.style.display = 'none';
                    }
                    deferredPrompt = null;
                });
            });
        }
    });
    
    // Hide install button if already installed
    window.addEventListener('appinstalled', () => {
        if (installBtn) {
            installBtn.style.display = 'none';
        }
        showToast('App installed successfully!', 'success');
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible:not(.permanent)');
        alerts.forEach(alert => {
            if (bootstrap.Alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }
        });
    }, 5000);
    
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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
});

// Service worker removed to fix clipboard issues in non-HTTPS contexts

// Handle beforeunload for unsaved changes
window.addEventListener('beforeunload', function(e) {
    const forms = document.querySelectorAll('form');
    let hasUnsavedChanges = false;
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[type="file"]');
        inputs.forEach(input => {
            if (input.files && input.files.length > 0) {
                hasUnsavedChanges = true;
            }
        });
    });
    
    if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        return e.returnValue;
    }
});

// Utility functions
const Utils = {
    // Debounce function for search
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function for scroll events
    throttle: function(func, limit) {
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
    },
    
    // Get file extension
    getFileExtension: function(filename) {
        return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2);
    },
    
    // Generate random ID
    generateId: function() {
        return Math.random().toString(36).substr(2, 9);
    }
};

// Export for use in other scripts
window.FileServer = {
    copyToClipboard,
    showToast,
    refreshInfo,
    formatFileSize,
    Utils
};
