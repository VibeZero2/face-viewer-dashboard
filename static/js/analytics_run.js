/**
 * Analytics Run JavaScript
 * Handles analytics form submission, results display, and export functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const form = document.getElementById('analytics-form');
    const runButton = document.getElementById('run-analysis-btn');
    const resultsBox = document.getElementById('analysis-results');
    const errorBox = document.getElementById('analysis-error');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const exportHtmlBtn = document.getElementById('export-html-btn');
    const exportPdfBtn = document.getElementById('export-pdf-btn');
    const testSelect = document.getElementById('test-select');
    const dvSelect = document.getElementById('dv-select');
    const secondaryVarSelect = document.getElementById('secondary-variable-select');
    const genderFilter = document.getElementById('gender-filter');
    const ageMinInput = document.getElementById('age-min');
    const ageMaxInput = document.getElementById('age-max');
    const dateFromInput = document.getElementById('date-from');
    const dateToInput = document.getElementById('date-to');
    
    // Fetch available variables from backend
    fetch('/api/analytics/variables')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch variables');
            }
            return response.json();
        })
        .then(variables => {
            // Populate variable dropdowns
            populateDropdown(dvSelect, variables);
            populateDropdown(secondaryVarSelect, variables, true); // Add empty option
            
            // Restore saved selections
            restoreFromLocalStorage();
        })
        .catch(error => {
            console.error('Error fetching variables:', error);
            errorBox.textContent = 'Failed to load variable options. Please refresh the page.';
            errorBox.classList.remove('d-none');
        });
    
    // Form submission handler
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Save current selections to localStorage
        saveToLocalStorage();
        
        // Disable button and show loading state
        runButton.disabled = true;
        runButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running...';
        errorBox.classList.add('d-none');
        resultsBox.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Running analysis...</p></div>';
        
        // Build request payload
        const payload = {
            test: testSelect.value,
            dv: dvSelect.value,
            filters: {}
        };
        
        // Add secondary variable if selected
        if (secondaryVarSelect.value) {
            payload.secondary_variable = secondaryVarSelect.value;
        }
        
        // Add filters
        if (genderFilter.value && genderFilter.value !== 'all') {
            payload.filters.gender = genderFilter.value;
        }
        
        if (ageMinInput.value) {
            payload.filters.age_min = parseInt(ageMinInput.value);
        }
        
        if (ageMaxInput.value) {
            payload.filters.age_max = parseInt(ageMaxInput.value);
        }
        
        if (dateFromInput.value) {
            payload.filters.date_from = dateFromInput.value;
        }
        
        if (dateToInput.value) {
            payload.filters.date_to = dateToInput.value;
        }
        
        // Send request to backend
        fetch('/api/run_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            // Reset button state
            runButton.disabled = false;
            runButton.innerHTML = 'Run Statistical Analysis';
            
            // Handle error
            if (!data.ok) {
                errorBox.textContent = data.message || 'Analysis failed with an unknown error.';
                errorBox.classList.remove('d-none');
                resultsBox.innerHTML = '';
                disableExportButtons();
                return;
            }
            
            // Display results
            displayResults(data);
            
            // Enable export buttons
            enableExportButtons();
        })
        .catch(error => {
            // Reset button state
            runButton.disabled = false;
            runButton.innerHTML = 'Run Statistical Analysis';
            
            // Show error
            console.error('Error running analysis:', error);
            errorBox.textContent = 'Failed to run analysis. Please try again.';
            errorBox.classList.remove('d-none');
            resultsBox.innerHTML = '';
            disableExportButtons();
        });
    });
    
    // Export button handlers
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function() {
            const params = buildExportParams();
            window.location.href = `/analytics/data.csv?${params}`;
        });
    }
    
    if (exportHtmlBtn) {
        exportHtmlBtn.addEventListener('click', function() {
            const params = buildExportParams();
            window.open(`/analytics/report.html?${params}`, '_blank');
        });
    }
    
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', function() {
            const params = buildExportParams();
            window.location.href = `/analytics/report.pdf?${params}`;
        });
    }
    
    // Helper functions
    function populateDropdown(select, variables, addEmptyOption = false) {
        // Clear existing options
        select.innerHTML = '';
        
        // Add empty option if requested
        if (addEmptyOption) {
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = '-- None --';
            select.appendChild(emptyOption);
        }
        
        // Add variable options
        variables.forEach(variable => {
            const option = document.createElement('option');
            option.value = variable.key;
            option.textContent = variable.label;
            select.appendChild(option);
        });
    }
    
    function saveToLocalStorage() {
        // Save form values to localStorage
        localStorage.setItem('analytics_test', testSelect.value);
        localStorage.setItem('analytics_dv', dvSelect.value);
        localStorage.setItem('analytics_secondary_var', secondaryVarSelect.value);
        localStorage.setItem('analytics_gender', genderFilter.value);
        localStorage.setItem('analytics_age_min', ageMinInput.value);
        localStorage.setItem('analytics_age_max', ageMaxInput.value);
        localStorage.setItem('analytics_date_from', dateFromInput.value);
        localStorage.setItem('analytics_date_to', dateToInput.value);
    }
    
    function restoreFromLocalStorage() {
        // Restore form values from localStorage
        if (localStorage.getItem('analytics_test')) {
            testSelect.value = localStorage.getItem('analytics_test');
        }
        
        if (localStorage.getItem('analytics_dv')) {
            dvSelect.value = localStorage.getItem('analytics_dv');
        }
        
        if (localStorage.getItem('analytics_secondary_var')) {
            secondaryVarSelect.value = localStorage.getItem('analytics_secondary_var');
        }
        
        if (localStorage.getItem('analytics_gender')) {
            genderFilter.value = localStorage.getItem('analytics_gender');
        }
        
        if (localStorage.getItem('analytics_age_min')) {
            ageMinInput.value = localStorage.getItem('analytics_age_min');
        }
        
        if (localStorage.getItem('analytics_age_max')) {
            ageMaxInput.value = localStorage.getItem('analytics_age_max');
        }
        
        if (localStorage.getItem('analytics_date_from')) {
            dateFromInput.value = localStorage.getItem('analytics_date_from');
        }
        
        if (localStorage.getItem('analytics_date_to')) {
            dateToInput.value = localStorage.getItem('analytics_date_to');
        }
    }
    
    function displayResults(data) {
        // Clear previous results
        resultsBox.innerHTML = '';
        
        // Create results container
        const resultsContainer = document.createElement('div');
        resultsContainer.className = 'card';
        
        // Create card header
        const cardHeader = document.createElement('div');
        cardHeader.className = 'card-header';
        cardHeader.innerHTML = `<h5>Analysis Results</h5>`;
        resultsContainer.appendChild(cardHeader);
        
        // Create card body
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        
        // Add APA text
        if (data.apa) {
            const apaDiv = document.createElement('div');
            apaDiv.className = 'mb-3';
            apaDiv.innerHTML = `<strong>APA Format:</strong> ${data.apa}`;
            cardBody.appendChild(apaDiv);
        }
        
        // Add statistics
        if (data.stats) {
            const statsDiv = document.createElement('div');
            statsDiv.className = 'mb-3';
            statsDiv.innerHTML = `<strong>Statistics:</strong><pre>${JSON.stringify(data.stats, null, 2)}</pre>`;
            cardBody.appendChild(statsDiv);
        }
        
        // Add sample size
        if (data.n) {
            const nDiv = document.createElement('div');
            nDiv.innerHTML = `<strong>Sample Size:</strong> ${data.n}`;
            cardBody.appendChild(nDiv);
        }
        
        resultsContainer.appendChild(cardBody);
        
        // Add export buttons
        const cardFooter = document.createElement('div');
        cardFooter.className = 'card-footer d-flex gap-2';
        cardFooter.innerHTML = `
            <button id="export-csv-btn" class="btn btn-sm btn-secondary">Export CSV</button>
            <button id="export-html-btn" class="btn btn-sm btn-secondary">Export HTML Report</button>
            <button id="export-pdf-btn" class="btn btn-sm btn-secondary">Export PDF Report</button>
        `;
        resultsContainer.appendChild(cardFooter);
        
        // Add results to page
        resultsBox.appendChild(resultsContainer);
        
        // Add event listeners to new export buttons
        document.getElementById('export-csv-btn').addEventListener('click', function() {
            const params = buildExportParams();
            window.location.href = `/analytics/data.csv?${params}`;
        });
        
        document.getElementById('export-html-btn').addEventListener('click', function() {
            const params = buildExportParams();
            window.open(`/analytics/report.html?${params}`, '_blank');
        });
        
        document.getElementById('export-pdf-btn').addEventListener('click', function() {
            const params = buildExportParams();
            window.location.href = `/analytics/report.pdf?${params}`;
        });
    }
    
    function buildExportParams() {
        // Build query parameters for export URLs
        const params = new URLSearchParams();
        
        params.append('test', testSelect.value);
        params.append('dv', dvSelect.value);
        
        if (secondaryVarSelect.value) {
            params.append('secondary_variable', secondaryVarSelect.value);
        }
        
        if (genderFilter.value && genderFilter.value !== 'all') {
            params.append('gender', genderFilter.value);
        }
        
        if (ageMinInput.value) {
            params.append('age_min', ageMinInput.value);
        }
        
        if (ageMaxInput.value) {
            params.append('age_max', ageMaxInput.value);
        }
        
        if (dateFromInput.value) {
            params.append('date_from', dateFromInput.value);
        }
        
        if (dateToInput.value) {
            params.append('date_to', dateToInput.value);
        }
        
        return params.toString();
    }
    
    function enableExportButtons() {
        if (exportCsvBtn) exportCsvBtn.disabled = false;
        if (exportHtmlBtn) exportHtmlBtn.disabled = false;
        if (exportPdfBtn) exportPdfBtn.disabled = false;
    }
    
    function disableExportButtons() {
        if (exportCsvBtn) exportCsvBtn.disabled = true;
        if (exportHtmlBtn) exportHtmlBtn.disabled = true;
        if (exportPdfBtn) exportPdfBtn.disabled = true;
    }
});
