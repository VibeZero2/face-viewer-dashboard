// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('dashboard-theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-theme');
        updateThemeIcon(true);
    }
    
    // Theme toggle event listener
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const isDarkTheme = body.classList.toggle('dark-theme');
            localStorage.setItem('dashboard-theme', isDarkTheme ? 'dark' : 'light');
            updateThemeIcon(isDarkTheme);
            
            // Update Plotly charts if they exist
            updatePlotlyTheme(isDarkTheme);
        });
    }
    
    // Update theme icon based on current theme
    function updateThemeIcon(isDarkTheme) {
        if (themeToggle) {
            themeToggle.innerHTML = isDarkTheme ? 
                '<i class="fas fa-sun"></i>' : 
                '<i class="fas fa-moon"></i>';
        }
    }
    
    // Update Plotly charts theme
    function updatePlotlyTheme(isDarkTheme) {
        const plotlyDivs = document.querySelectorAll('[id^="plotly-"]');
        
        plotlyDivs.forEach(div => {
            if (div._fullData) {
                const newLayout = {
                    paper_bgcolor: isDarkTheme ? '#2c3034' : '#ffffff',
                    plot_bgcolor: isDarkTheme ? '#2c3034' : '#ffffff',
                    font: {
                        color: isDarkTheme ? '#f8f9fa' : '#212529'
                    },
                    xaxis: {
                        gridcolor: isDarkTheme ? '#495057' : '#e9ecef'
                    },
                    yaxis: {
                        gridcolor: isDarkTheme ? '#495057' : '#e9ecef'
                    }
                };
                
                Plotly.relayout(div.id, newLayout);
            }
        });
    }
    
    // Show loading overlay during AJAX requests
    const loadingOverlay = document.getElementById('loading-overlay');
    
    if (loadingOverlay) {
        // Show loading overlay before AJAX request
        document.addEventListener('ajax:before', function() {
            loadingOverlay.classList.add('show');
        });
        
        // Hide loading overlay after AJAX request
        document.addEventListener('ajax:complete', function() {
            loadingOverlay.classList.remove('show');
        });
    }
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Initialize popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => {
        new bootstrap.Popover(popover);
    });
    
    // Data table initialization
    const dataTables = document.querySelectorAll('.data-table');
    dataTables.forEach(table => {
        if (typeof $.fn.DataTable !== 'undefined') {
            $(table).DataTable({
                responsive: true,
                pageLength: 25
            });
        }
    });
    
    // Apply dark theme to Plotly charts if dark theme is active
    if (body.classList.contains('dark-theme')) {
        updatePlotlyTheme(true);
    }
});

// Function to download data as CSV
function downloadCSV(csvContent, fileName) {
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodedUri);
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Function to show confirmation dialog
function confirmAction(message, callback) {
    // If callback is provided, use it, otherwise just return the confirmation result
    if (callback) {
        if (confirm(message)) {
            callback();
        }
        return false;
    } else {
        return confirm(message);
    }
}

// Function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Function to show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const notificationContainer = document.getElementById('notification-container');
    if (notificationContainer) {
        notificationContainer.appendChild(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
}
