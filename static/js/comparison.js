document.addEventListener('DOMContentLoaded', function() {
  console.log('Comparison.js loaded');

  // Initialize syntax highlighting
  if (typeof hljs !== 'undefined') {
    hljs.configure({
      languages: ['xml', 'json', 'csv'],
      ignoreUnescapedHTML: true
    });
    hljs.highlightAll();
    
    // Add custom CSS classes to XML elements based on changes
    highlightChanges();
  }

  // Global handleFiles function that can be called from any event handler
  window.handleTransformFile = function(files) {
    if (!files || files.length === 0) {
      console.error('No files to handle');
      return;
    }
    
    console.log('Handling files for transformation:', files);
    
    // Create FormData and upload all files
    const formData = new FormData();
    
    // Add all files to the form data
    for (let i = 0; i < files.length; i++) {
      formData.append('file', files[i]);
    }
    
    // Show file names that are being processed
    const fileNames = Array.from(files).map(f => f.name).join(', ');
    
    // Add Accept header to indicate this is an AJAX request
    const headers = new Headers({
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    });
    
    // Show loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
      <div class="spinner"></div>
      <p>Processing your file${files.length > 1 ? 's' : ''}: ${fileNames}</p>
    `;
    document.body.appendChild(loadingOverlay);
    
    console.log('Sending file to server for transformation');
    
    // Send the file to the server
    fetch('/upload', {
      method: 'POST',
      headers: headers,
      body: formData
    })
    .then(response => {
      console.log('Server response:', response);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Upload successful:', data);
      // Remove loading overlay
      loadingOverlay.remove();
      
      if (data.error) {
        // Display error message
        alert('Error: ' + data.error);
        return;
      }
      
      // Redirect to the new comparison page
      window.location.href = '/comparison/' + data.result_id;
    })
    .catch(error => {
      // Remove loading overlay
      loadingOverlay.remove();
      console.error('Error:', error);
      alert('Error uploading file: ' + error.message);
    });
  };

  // Fix button functionality
  const downloadBtn = document.querySelector('.btn-primary');
  const backBtn = document.querySelector('.btn-secondary');
  
  if (downloadBtn) {
    downloadBtn.addEventListener('click', function(e) {
      console.log('Download button clicked');
      // The button should work normally as it's an <a> tag with href
    });
  } else {
    console.error('Download button not found');
  }
  
  if (backBtn) {
    backBtn.addEventListener('click', function(e) {
      console.log('Back button clicked');
      // The button should work normally as it's an <a> tag with href
    });
  } else {
    console.error('Back button not found');
  }
  
  // Add drag and drop functionality
  // First try with dedicated drop zone, then full page
  const dropZone = document.getElementById('drop-zone');
  const dropArea = dropZone || document.querySelector('.drag-drop-info') || document.querySelector('.comparison-content');
  
  console.log('Drop elements:', {
    dropZone: dropZone,
    dropArea: dropArea
  });
  
  // We'll use the entire page as the drop area
  if (dropArea) {
    console.log('Drop area found:', dropArea);
    
    // Debug drag events
    document.body.addEventListener('dragenter', function(e) {
      console.log('Drag enter detected on body');
    });
    
    // Set up event listeners directly on the document
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      document.addEventListener(eventName, function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log(eventName + ' event on document');
        
        // Highlight drop area on dragenter and dragover
        if (eventName === 'dragenter' || eventName === 'dragover') {
          dropArea.classList.add('drag-highlight');
        }
        
        // Remove highlight on dragleave and drop
        if (eventName === 'dragleave' || eventName === 'drop') {
          dropArea.classList.remove('drag-highlight');
        }
        
        // Handle file drop
        if (eventName === 'drop') {
          handleDrop(e);
        }
      }, false);
    });
    
    // Also set up events directly on the drop area for better targeting
    dropArea.addEventListener('dragenter', function(e) {
      e.preventDefault();
      e.stopPropagation();
      dropArea.classList.add('drag-highlight');
      console.log('Drag enter on drop area');
    });
    
    dropArea.addEventListener('dragover', function(e) {
      e.preventDefault();
      e.stopPropagation();
      dropArea.classList.add('drag-highlight');
    });
    
    dropArea.addEventListener('dragleave', function(e) {
      e.preventDefault();
      e.stopPropagation();
      dropArea.classList.remove('drag-highlight');
      console.log('Drag leave on drop area');
    });
    
    dropArea.addEventListener('drop', function(e) {
      e.preventDefault();
      e.stopPropagation();
      dropArea.classList.remove('drag-highlight');
      console.log('Drop on drop area');
      handleDrop(e);
    });
    
    function handleDrop(e) {
      console.log('File dropped, handling drop event');
      const dt = e.dataTransfer;
      if (!dt) {
        console.error('No dataTransfer found in drop event');
        return;
      }
      
      const files = dt.files;
      console.log('Dropped files:', files);
      
      if (files && files.length > 0) {
        // Use the global function to handle the file
        window.handleTransformFile(files);
      } else {
        console.error('No files found in drop event');
      }
    }
  } else {
    console.error('No drop area found in the document');
  }
  
  // Add an upload button as a backup method
  const comparisonHeader = document.querySelector('.comparison-header');
  if (comparisonHeader) {
    const uploadBtn = document.createElement('a');
    uploadBtn.className = 'btn btn-secondary';
    uploadBtn.innerHTML = '<i class="fas fa-upload"></i> Upload New File';
    uploadBtn.style.marginLeft = '10px';
    
    // Add file input that will be triggered by the upload button
    const hiddenFileInput = document.createElement('input');
    hiddenFileInput.type = 'file';
    hiddenFileInput.style.display = 'none';
    hiddenFileInput.accept = '.xml,.json,.csv';
    document.body.appendChild(hiddenFileInput);
    
    uploadBtn.addEventListener('click', function(e) {
      e.preventDefault();
      hiddenFileInput.click();
    });
    
    hiddenFileInput.addEventListener('change', function() {
      if (this.files && this.files.length > 0) {
        // Use the global function to handle the file
        window.handleTransformFile(this.files);
      }
    });
    
    const actionsContainer = document.querySelector('.comparison-actions');
    if (actionsContainer) {
      actionsContainer.appendChild(uploadBtn);
    } else {
      comparisonHeader.appendChild(uploadBtn);
    }
  }

  // Set up the manual file upload button with direct event handling
  const manualUploadBtn = document.getElementById('manual-upload-btn');
  const manualFileUpload = document.getElementById('manual-file-upload');
  
  if (manualUploadBtn && manualFileUpload) {
    console.log('Manual upload elements found');
    
    // Direct click event for the button
    manualUploadBtn.onclick = function(e) {
      console.log('Manual upload button clicked directly');
      e.preventDefault();
      e.stopPropagation();
      manualFileUpload.click();
    };
    
    // Also add touchstart for mobile devices
    manualUploadBtn.addEventListener('touchstart', function(e) {
      console.log('Manual upload button touched');
      e.preventDefault();
      e.stopPropagation();
      manualFileUpload.click();
    }, true);
    
    manualFileUpload.addEventListener('change', function() {
      if (this.files && this.files.length > 0) {
        console.log('File selected via manual upload:', this.files[0].name);
        // Use the global function to handle the file upload and transformation
        window.handleTransformFile(this.files);
      }
    });
  } else {
    console.error('Manual upload elements not found', { 
      btn: manualUploadBtn, 
      input: manualFileUpload 
    });
  }

  // Make the drop-zone clickable but prevent clicks on the button from triggering the zone's click handler
  if (dropZone && manualFileUpload) {
    dropZone.addEventListener('click', function(e) {
      // Only trigger if NOT clicking on the button or its children
      if (e.target === manualUploadBtn || manualUploadBtn.contains(e.target)) {
        console.log('Button clicked in drop zone - not triggering zone click');
        return;
      }
      
      console.log('Drop zone clicked');
      manualFileUpload.click();
    });
  }
});

// Function to highlight changes in XML/JSON content
function highlightChanges() {
  // Get the changes from the page if available
  const changeItems = document.querySelectorAll('.change-item');
  if (!changeItems.length) return;
  
  const resultCode = document.querySelector('.result-code code');
  if (!resultCode) return;
  
  // Process each change type
  changeItems.forEach(changeItem => {
    const changeType = changeItem.classList.contains('added') ? 'added' : 
                       changeItem.classList.contains('removed') ? 'removed' : 
                       changeItem.classList.contains('modified') ? 'modified' : null;
    
    if (!changeType) return;
    
    // Get the description text which may contain element names
    const description = changeItem.querySelector('.change-description').textContent;
    
    // Extract element names from descriptions using regex
    const elementMatches = description.match(/<([^>]+)>/g);
    if (!elementMatches) return;
    
    elementMatches.forEach(match => {
      // Remove < and > symbols
      const elementName = match.replace(/<|>/g, '');
      
      // Find these elements in the code and add highlighting
      const elementRegex = new RegExp(`<${elementName}[^>]*>.*?<\/${elementName}>`, 'g');
      const codeHTML = resultCode.innerHTML;
      
      // Add highlighting classes based on change type
      const replacementClass = changeType === 'added' ? 'add-highlight' : 
                              changeType === 'removed' ? 'remove-highlight' : 
                              'modify-highlight';
      
      resultCode.innerHTML = codeHTML.replace(
        elementRegex, 
        match => `<span class="${replacementClass}">${match}</span>`
      );
    });
  });
} 