// Main JavaScript for XML/JSON Transformation Service

document.addEventListener('DOMContentLoaded', function() {
    console.log('App.js loaded');

    // Initialize site-wide accordions
    initAccordions();

    // Get DOM elements
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const dropArea = document.getElementById('drop-area');
    const resultsContainer = document.getElementById('results-container');
    const statusEl = document.getElementById('status');
    const resultContent = document.getElementById('result-content');
    const originalContent = document.getElementById('original-content');
    const transformedContent = document.getElementById('transformed-content');
    const processingTime = document.getElementById('processing-time');
    const loader = document.querySelector('.loader');
    const multipleResultsContainer = document.getElementById('multiple-results-container');
    const schemaSelect = document.getElementById('schema-select');
    const customSchemaInput = document.getElementById('custom-schema');
    const transformationStatus = document.getElementById('transformation-status');
    const selectedSchemaSpan = document.getElementById('selected-schema');
    const submitBtn = document.getElementById('submit-btn');
    const fileSelectBtn = document.getElementById('file-select-btn');
    const fileList = document.getElementById('file-list');
    const transformBtn = document.getElementById('transform-btn');
    const transformLoader = document.getElementById('transform-loader');
    
    console.log('DOM elements:', {
        uploadForm: !!uploadForm,
        fileInput: !!fileInput,
        dropArea: !!dropArea,
        submitBtn: !!submitBtn
    });
    
    // Initialize variables for tracking uploaded files and results
    let uploadedFiles = [];
    let resultEntries = {};
    
    // Current result ID for polling
    let currentResultId = null;
    let statusCheckInterval = null;
    let pendingTransformations = [];
    
    // Add drag and drop functionality if drop area exists
    if (dropArea) {
        console.log('Setting up drag and drop');
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        dropArea.addEventListener('drop', handleDrop, false);
        
        // Handle file select button
        if (fileSelectBtn) {
            fileSelectBtn.addEventListener('click', function() {
                fileInput.click();
            });
        }
        
        // Handle file input change
        if (fileInput) {
            fileInput.addEventListener('change', function() {
                handleFilesWithLogging(this.files);
            });
        }
        
        // Handle form submission
        if (uploadForm) {
            uploadForm.addEventListener('submit', function(e) {
                e.preventDefault(); // Prevent the default form submission
                
                updateAgentOutput("Starting file transformation process...");
                
                if (uploadedFiles.length === 0) {
                    updateAgentOutput("No files selected for transformation", "error");
                    alert('Please select at least one file to transform.');
                    return false;
                }
                
                // Show loading spinner
                if (transformLoader) {
                    transformLoader.classList.remove('d-none');
                }
                
                updateAgentOutput(`Preparing to transform ${uploadedFiles.length} files...`);
                
                // Create FormData object
                const formData = new FormData();
                
                // Add all uploaded files to the FormData
                uploadedFiles.forEach((file, index) => {
                    updateAgentOutput(`Adding file to request: ${file.name}`);
                    formData.append('file', file);
                });
                
                // Add any other form data if needed
                if (schemaSelect && schemaSelect.value) {
                    updateAgentOutput(`Using schema: ${schemaSelect.value}`);
                    formData.append('schema_path', schemaSelect.value);
                }
                
                // Send the request
                updateAgentOutput("Sending files to server for processing...");
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        updateAgentOutput(`Server returned error: ${response.status} ${response.statusText}`, "error");
                        throw new Error(`Server error: ${response.status}`);
                    }
                    
                    updateAgentOutput("Server received files successfully", "success");
                    return response.json();
                })
                .then(data => {
                    if (data === null) {
                        updateAgentOutput("No response data received", "warning");
                        return;
                    }
                    
                    if (data && data.error) {
                        // Handle error
                        updateAgentOutput(`Error: ${data.error}`, "error");
                        alert(data.error);
                        if (transformLoader) {
                            transformLoader.classList.add('d-none');
                        }
                        return;
                    }
                    
                    // Handle successful response
                    updateAgentOutput(`Transformation complete! Processed ${data.result_ids ? data.result_ids.length : 0} files successfully`, "success");
                    console.log('Upload successful:', data);
                    
                    // Update recent transformations instead of redirecting
                    updateAgentOutput("Refreshing recent transformations table...");
                    fetchAndUpdateRecentTransformations();
                    
                    // Hide loader and show success message
                    if (transformLoader) {
                        transformLoader.classList.add('d-none');
                    }
                    
                    // Show processing status in the agent output section
                    updateAgentOutput("All operations completed successfully. View results in Recent Transformations section below.", "success");
                    
                    // Show the results section if hidden
                    const resultsSection = document.getElementById('results-section');
                    if (resultsSection) {
                        resultsSection.classList.remove('d-none');
                        resultsSection.classList.add('active');
                        
                        // If we have a results container, populate it
                        if (data.result_ids && data.result_ids.length > 0) {
                            const resultsContent = document.getElementById('results-content');
                            if (resultsContent) {
                                updateAgentOutput("Displaying result summaries...");
                                resultsContent.innerHTML = '';
                                
                                data.result_ids.forEach(resultId => {
                                    const resultCard = document.createElement('div');
                                    resultCard.className = 'card mb-3';
                                    resultCard.innerHTML = `
                                        <div class="card-body">
                                            <h5 class="card-title">Transformation Result</h5>
                                            <p class="card-text">Result ID: ${resultId}</p>
                                            <a href="/comparison/${resultId}" class="btn btn-primary">View Details</a>
                                        </div>
                                    `;
                                    resultsContent.appendChild(resultCard);
                                });
                            }
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    updateAgentOutput(`Error during transformation: ${error.message}`, "error");
                    if (transformLoader) {
                        transformLoader.classList.add('d-none');
                    }
                });
            });
        }
    }
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        dropArea.classList.add('drag-highlight');
        dropArea.classList.add('dragging');
    }
    
    function unhighlight() {
        dropArea.classList.remove('drag-highlight');
        dropArea.classList.remove('dragging');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFilesWithLogging(files);
    }
    
    function handleFiles(files) {
        if (files.length > 0) {
            // Clear file list if it already has files
            if (fileList.children.length > 0) {
                fileList.innerHTML = '';
            }
            
            // Clear the uploaded files array
            uploadedFiles = [];
            
            // Add each file to the list
            Array.from(files).forEach(file => {
                addFileToList(file);
                uploadedFiles.push(file); // Store the actual file object
            });
            
            // Enable transform button
            if (transformBtn) {
                transformBtn.disabled = false;
            }
        }
    }
    
    function addFileToList(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        // Determine file icon based on type
        let fileIconClass = 'fa-file';
        if (file.name.endsWith('.csv')) {
            fileIconClass = 'fa-file-csv';
        } else if (file.name.endsWith('.json')) {
            fileIconClass = 'fa-file-code';
        } else if (file.name.endsWith('.xml')) {
            fileIconClass = 'fa-file-code';
        }
        
        // Format file size
        const fileSize = formatFileSize(file.size);
        
        fileItem.innerHTML = `
            <div class="file-icon"><i class="fas ${fileIconClass}"></i></div>
            <div class="file-name">${file.name}</div>
            <div class="file-size">${fileSize}</div>
            <div class="file-remove"><i class="fas fa-times"></i></div>
        `;
        
        // Add remove functionality
        const removeBtn = fileItem.querySelector('.file-remove');
        removeBtn.addEventListener('click', function() {
            // Remove file from UI
            fileItem.remove();
            
            // Remove file from uploadedFiles array
            const fileIndex = uploadedFiles.findIndex(f => f.name === file.name && f.size === file.size);
            if (fileIndex !== -1) {
                uploadedFiles.splice(fileIndex, 1);
            }
            
            // Disable transform button if no files left
            if (fileList.children.length === 0 && transformBtn) {
                transformBtn.disabled = true;
            }
        });
        
        // Add to file list
        fileList.appendChild(fileItem);
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Handle selected schema file
    if (customSchemaInput) {
        customSchemaInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                selectedSchemaSpan.textContent = this.files[0].name;
            }
        });
    }
    
    // Toggle sidebar on mobile
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }
    
    // Initialize charts if they exist
    function initCharts() {
        // Initialize transformation types chart
        const typesChart = document.getElementById('transformation-types-chart');
        if (typesChart) {
            const typesCtx = typesChart.getContext('2d');
            new Chart(typesCtx, {
                type: 'pie',
                data: {
                    labels: ['XML to XML', 'JSON to XML', 'CSV to XML'],
                    datasets: [{
                        data: [55, 30, 15],
                        backgroundColor: ['#4BBEB3', '#4B86B4', '#ADCBE3']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        }

        // Initialize performance chart
        const perfChart = document.getElementById('performance-chart');
        if (perfChart) {
            const perfCtx = perfChart.getContext('2d');
            new Chart(perfCtx, {
                type: 'line',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Processing Time (ms)',
                        data: [120, 115, 130, 100, 95, 88, 105],
                        borderColor: '#4BBEB3',
                        tension: 0.4,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        }
    }
    
    // Initialize charts if Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        initCharts();
    } else {
        // Wait for Chart.js to load
        window.addEventListener('load', function() {
            if (typeof Chart !== 'undefined') {
                initCharts();
            }
        });
    }
    
    // Function to fetch and update the recent transformations table
    function fetchAndUpdateRecentTransformations() {
        updateAgentOutput("Fetching latest transformation data...");
        
        fetch('/api/latest-transformations')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response error: ${response.status}`);
                }
                updateAgentOutput("Received transformation data from server", "success");
                return response.json();
            })
            .then(data => {
                // Update the recent transformations table
                updateAgentOutput(`Processing ${data.transformations.length} transformation records...`);
                updateRecentTransformationsTable(data.transformations);
                
                // Update dashboard stats if needed
                if (data.stats) {
                    updateAgentOutput("Updating dashboard statistics...");
                    updateDashboardStats(data.stats);
                }
                
                updateAgentOutput("Transformations table updated successfully!", "success");
            })
            .catch(error => {
                console.error('Error fetching transformations:', error);
                updateAgentOutput(`Error fetching transformations: ${error.message}`, "error");
            });
    }
    
    // Function to update the recent transformations table
    function updateRecentTransformationsTable(transformations) {
        const tableBody = document.querySelector('.table-responsive tbody');
        if (!tableBody) return;
        
        // Clear the table
        tableBody.innerHTML = '';
        
        // Add each transformation to the table
        transformations.forEach(transform => {
            const row = document.createElement('tr');
            
            // ID cell
            const idCell = document.createElement('td');
            idCell.innerHTML = `<span class="badge bg-dark">${transform.id.substring(0, 8)}</span>`;
            row.appendChild(idCell);
            
            // File type cell
            const fileTypeCell = document.createElement('td');
            let badgeClass = 'badge bg-secondary';
            if (transform.file_type === 'xml') badgeClass = 'badge bg-primary';
            else if (transform.file_type === 'json') badgeClass = 'badge bg-success';
            else if (transform.file_type === 'csv') badgeClass = 'badge bg-info';
            fileTypeCell.innerHTML = `<span class="${badgeClass} text-white">${transform.file_type.toUpperCase()}</span>`;
            row.appendChild(fileTypeCell);
            
            // Status cell
            const statusCell = document.createElement('td');
            let statusClass = '';
            let statusIcon = '';
            if (transform.status === 'completed') {
                statusClass = 'status-completed';
                statusIcon = 'fa-check-circle';
            } else if (transform.status === 'error') {
                statusClass = 'status-failed';
                statusIcon = 'fa-times-circle';
            } else {
                statusClass = 'status-processing';
                statusIcon = 'fa-spinner';
            }
            statusCell.innerHTML = `<span class="status-badge ${statusClass}"><i class="fas ${statusIcon} me-1"></i>${transform.status}</span>`;
            row.appendChild(statusCell);
            
            // Time cell
            const timeCell = document.createElement('td');
            timeCell.textContent = transform.formatted_time || new Date(transform.timestamp * 1000).toLocaleString();
            row.appendChild(timeCell);
            
            // Duration cell
            const durationCell = document.createElement('td');
            if (transform.duration) {
                durationCell.innerHTML = `<span class="fw-bold">${(transform.duration * 1000).toFixed(2)}</span> ms`;
            } else {
                durationCell.textContent = 'N/A';
            }
            row.appendChild(durationCell);
            
            // Size cell
            const sizeCell = document.createElement('td');
            sizeCell.textContent = transform.size ? `${transform.size} chars` : 'N/A';
            row.appendChild(sizeCell);
            
            // Actions cell
            const actionsCell = document.createElement('td');
            actionsCell.className = 'text-center';
            actionsCell.innerHTML = `
                <button class="btn btn-sm btn-primary view-btn" data-id="${transform.id}">
                    <i class="fas fa-eye me-1"></i> View
                </button>
                <button class="btn btn-sm btn-outline-secondary ms-2 download-btn" data-id="${transform.id}">
                    <i class="fas fa-download"></i>
                </button>
            `;
            row.appendChild(actionsCell);
            
            tableBody.appendChild(row);
        });
        
        // Add event listeners to the view buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                window.location.href = `/comparison/${id}`;
            });
        });
        
        // Add event listeners to the download buttons
        document.querySelectorAll('.download-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                window.location.href = `/download/${id}`;
            });
        });
    }
    
    // Function to update the agent output section
    function updateAgentOutput(message, type = 'info') {
        const agentOutput = document.getElementById('agent-output');
        if (!agentOutput) return;
        
        // Create a new message element
        const messageElement = document.createElement('div');
        messageElement.className = `agent-message ${type}`;
        
        // Set the message text
        messageElement.innerHTML = `
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
            <span class="message">${message}</span>
        `;
        
        // Add the message to the output
        agentOutput.appendChild(messageElement);
        
        // Scroll to the bottom
        agentOutput.scrollTop = agentOutput.scrollHeight;
        
        // Also log to console for debugging
        console.log(`[Agent] ${type.toUpperCase()}: ${message}`);
    }

    // Update the function that displays transformation results to use the new clean design without boxes
    function displayTransformationResults(result) {
        if (!resultsContainer) return;
        
        // Clear previous results
        resultsContainer.innerHTML = '';
        
        // Create the card structure
        const resultCard = document.createElement('div');
        resultCard.className = 'card rounded-4 w-100';
        
        // Create card header with title and options
        const cardHeader = document.createElement('div');
        cardHeader.className = 'card-header';
        
        const headerContent = document.createElement('div');
        headerContent.className = 'd-flex align-items-center justify-content-between';
        
        const resultTitle = document.createElement('h5');
        resultTitle.className = 'mb-0';
        resultTitle.innerHTML = '<i class="material-icons-outlined align-middle me-2">check_circle</i>Transformation Results';
        
        const dropdownDiv = document.createElement('div');
        dropdownDiv.className = 'dropdown';
        dropdownDiv.innerHTML = `
            <a href="javascript:;" class="dropdown-toggle-nocaret options dropdown-toggle" data-bs-toggle="dropdown">
                <i class="material-icons-outlined">more_vert</i>
            </a>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="/download/${result.id || result.result_id}"><i class="material-icons-outlined fs-5 align-middle me-2">download</i>Download Result</a></li>
                <li><a class="dropdown-item" href="/"><i class="material-icons-outlined fs-5 align-middle me-2">dashboard</i>Dashboard</a></li>
                <li><a class="dropdown-item" href="javascript:window.print()"><i class="material-icons-outlined fs-5 align-middle me-2">print</i>Print Results</a></li>
            </ul>
        `;
        
        headerContent.appendChild(resultTitle);
        headerContent.appendChild(dropdownDiv);
        
        const resultDescription = document.createElement('p');
        resultDescription.className = 'text-secondary mb-3';
        resultDescription.textContent = `Detailed view of transformation output - ID: ${(result.id || result.result_id || '').substring(0, 8)}`;
        
        cardHeader.appendChild(headerContent);
        cardHeader.appendChild(resultDescription);
        
        // Create card body with metrics in horizontal layout
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        
        const row = document.createElement('div');
        row.className = 'row g-3';
        
        const col = document.createElement('div');
        col.className = 'col-12';
        
        const metricsContainer = document.createElement('div');
        metricsContainer.className = 'd-flex flex-wrap justify-content-between align-items-center';
        
        // Input Type item
        const inputTypeItem = document.createElement('div');
        inputTypeItem.className = 'metrics-item me-4 mb-3';
        inputTypeItem.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="metrics-icon me-3">
                    <i class="material-icons-outlined">input</i>
                </div>
                <div>
                    <p class="mb-0 text-secondary">Input Type</p>
                    <h4 class="mb-0 mt-1">${result.source_type || 'unknown'}</h4>
                </div>
            </div>
        `;
        
        // Output Type item
        const outputTypeItem = document.createElement('div');
        outputTypeItem.className = 'metrics-item me-4 mb-3';
        outputTypeItem.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="metrics-icon me-3">
                    <i class="material-icons-outlined">output</i>
                </div>
                <div>
                    <p class="mb-0 text-secondary">Output Type</p>
                    <h4 class="mb-0 mt-1">${result.result_type || 'xml'}</h4>
                </div>
            </div>
        `;
        
        // Processing Date item
        const processingDateItem = document.createElement('div');
        processingDateItem.className = 'metrics-item me-4 mb-3';
        processingDateItem.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="metrics-icon me-3">
                    <i class="material-icons-outlined">event</i>
                </div>
                <div>
                    <p class="mb-0 text-secondary">Processing Date</p>
                    <h4 class="mb-0 mt-1">${new Date().toLocaleString()}</h4>
                </div>
            </div>
        `;
        
        // Duration item
        const durationItem = document.createElement('div');
        durationItem.className = 'metrics-item me-4 mb-3';
        durationItem.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="metrics-icon me-3">
                    <i class="material-icons-outlined">timer</i>
                </div>
                <div>
                    <p class="mb-0 text-secondary">Duration</p>
                    <h4 class="mb-0 mt-1">${((result.duration || result.processing_time || 0.1) * 1000).toFixed(2)}ms</h4>
                </div>
            </div>
        `;
        
        // Action buttons
        const actionButtons = document.createElement('div');
        actionButtons.className = 'action-buttons mb-3';
        actionButtons.innerHTML = `
            <div class="d-flex gap-2">
                <a href="/download/${result.id || result.result_id}" class="btn btn-light rounded-3 d-flex align-items-center justify-content-center">
                    <i class="material-icons-outlined align-middle me-1">download</i> Download
                </a>
                <a href="/" class="btn btn-outline-light rounded-3 d-flex align-items-center justify-content-center">
                    <i class="material-icons-outlined align-middle me-1">dashboard</i> Dashboard
                </a>
            </div>
        `;
        
        // Add all elements to container
        metricsContainer.appendChild(inputTypeItem);
        metricsContainer.appendChild(outputTypeItem);
        metricsContainer.appendChild(processingDateItem);
        metricsContainer.appendChild(durationItem);
        metricsContainer.appendChild(actionButtons);
        
        // Build the DOM structure
        col.appendChild(metricsContainer);
        row.appendChild(col);
        cardBody.appendChild(row);
        resultCard.appendChild(cardHeader);
        resultCard.appendChild(cardBody);
        
        // Add to results container
        resultsContainer.appendChild(resultCard);
    }

    // Initialize accordions
    function initAccordions() {
        document.querySelectorAll('.esb-accordion-header').forEach(header => {
            header.addEventListener('click', function() {
                // Get the parent accordion item
                const accordionItem = this.parentElement;
                
                // Check if this is a fixed (non-collapsible) accordion
                if (accordionItem.classList.contains('fixed-accordion')) {
                    return; // Do nothing for fixed accordions
                }
                
                // Toggle active class on the clicked accordion
                accordionItem.classList.toggle('active');
            });
        });
    }

    // Function to update dashboard stats
    function updateDashboardStats(stats) {
        const statCards = document.querySelectorAll('.stat-card .value');
        if (statCards.length >= 3) {
            if (stats.total) statCards[0].textContent = stats.total.toLocaleString();
            if (stats.avgTime) statCards[1].textContent = stats.avgTime + 's';
            if (stats.successRate) statCards[2].textContent = stats.successRate + '%';
        }
    }

    // Set up refresh button for recent transformations
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            updateAgentOutput("Refreshing recent transformations...");
            fetchAndUpdateRecentTransformations();
        });
    }
    
    // Initial load of transformations
    fetchAndUpdateRecentTransformations();

    // Function to handle file upload with more detailed logging
    function handleFilesWithLogging(files) {
        updateAgentOutput(`Processing ${files.length} files for upload...`);
        
        // List the files being uploaded for debugging
        Array.from(files).forEach((file, index) => {
            updateAgentOutput(`File ${index+1}: ${file.name} (${formatFileSize(file.size)})`, "info");
        });
        
        // Call the original handleFiles function
        handleFiles(files);
    }
}); 