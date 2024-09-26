document.addEventListener('DOMContentLoaded', function() {
    const selectModelStep = document.getElementById('selectModelStep');
    const summarizersStep = document.getElementById('summarizersStep');
    const modelSelect = document.getElementById('modelSelect');
    const selectModelButton = document.getElementById('selectModelButton');
    const urlInput = document.getElementById('urlInput');
    const sendUrlButton = document.getElementById('sendUrlButton');
    const responseElement = document.getElementById('responseElement');
    const pdfFileInput = document.getElementById('pdfFile');
    const uploadPdfButton = document.getElementById('uploadPdfButton');
    const fileNameElement = document.getElementById('fileName');
    const progressContainer = document.getElementById('progressContainer');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadPercentage = document.getElementById('uploadPercentage');
    const pdfResponseElement = document.getElementById('pdfResponseElement');
    const pdfQueryButton=document.getElementById('pdfQueryButton');
    const pdfQueryResponseElement = document.getElementById('pdfQueryResponseElement');
    const webSummarizerButton = document.getElementById('webSummarizerButton');
    const pdfSummarizerButton = document.getElementById('pdfSummarizerButton');
    const urlQueryButton=document.getElementById('urlQueryButton');
    const urlQueryResponseElement = document.getElementById('urlQueryResponseElement');
    const selectedModelElement = document.getElementById('selectedModel');

    // Step 1: Select Model
    selectModelButton.addEventListener('click', () => {
        const selectedModel = modelSelect.value;

        if (!selectedModel) {
            alert('Please select a model.');
            return;
        }

        // Hide the model selection and show the summarizers
        selectModelStep.classList.add('hidden');
        summarizersStep.classList.remove('hidden');
        selectedModelElement.textContent = `Selected model: ${selectedModel}`;
        
    });

    // Step 2: Web Summarizer
    sendUrlButton.addEventListener('click', () => {
        const url = urlInput.value;
        if (url.trim() === "") {
            responseElement.textContent = 'Please enter a valid URL.';
            return;
        }

        fetch('http://localhost:5000/process-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            responseElement.textContent = data.message || 'No response from server';
        })
        .catch(error => {
            responseElement.textContent = 'Error: ' + error.message;
        });
        
    });

    // Step 2: PDF Summarizer
    uploadPdfButton.addEventListener('click', () => {
        const file = pdfFileInput.files[0];
        

        if (file && file.type === 'application/pdf') {
            const formData = new FormData();
            formData.append('pdf', file);

            progressContainer.style.display = 'block';

            const xhr = new XMLHttpRequest();
            xhr.open('POST', 'http://localhost:5000/upload-pdf', true);

            // Update the progress bar and percentage
            xhr.upload.onprogress = function(event) {
                if (event.lengthComputable) {
                    const percentComplete = Math.round((event.loaded / event.total) * 100);
                    uploadProgress.style.width = percentComplete + '%';
                    uploadPercentage.textContent = percentComplete + '%';
                }
            };

            // Handle the response from the server
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    pdfResponseElement.textContent = response.message || 'Upload successful';
                    fileNameElement.textContent = `Uploaded File: ${file.name}`;
                } else {
                    pdfResponseElement.textContent = 'Upload failed. Please try again.';
                }
            };

            // Handle errors
            xhr.onerror = function() {
                pdfResponseElement.textContent = 'Error during upload. Please try again.';
            };

            // Send the form data with the file
            xhr.send(formData);
        } else {
            pdfResponseElement.textContent = 'Please select a valid PDF file.';
        }
    });
    //functionality for url query input
    urlQueryButton.addEventListener('click', () => {
        const query = urlQueryInput.value;
    
        if (query.trim() === "") {
            urlQueryResponseElement.textContent = 'Please enter a valid query.';
            return;
        }
    
        fetch('http://localhost:5000/your_query_url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            urlQueryResponseElement.textContent = data.message || 'No response from server';
        })
        .catch(error => {
            urlQueryResponseElement.textContent = 'Error: ' + error.message;
        });
    });
    //functionality for pdf query input
    pdfQueryButton.addEventListener('click', () => {
        const query = pdfQueryInput.value;
    
        if (query.trim() === "") {
            pdfQueryResponseElement.textContent = 'Please enter a valid query.';
            return;
        }
    
        fetch('http://localhost:5000/your_query_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            pdfQueryResponseElement.textContent = data.message || 'No response from server';
        })
        .catch(error => {
            pdfQueryResponseElement.textContent = 'Error: ' + error.message;
        });
    });

    

    // web Summarizer tab content
    document.getElementById('webSummarizerButton').addEventListener('click', function() {
        document.getElementById('webSummarizer').style.display = 'block';
        document.getElementById('pdfSummarizer').style.display = 'none';
    });

    //pdf summarizer tab content
    
    document.getElementById('pdfSummarizerButton').addEventListener('click', function() {
        document.getElementById('webSummarizer').style.display = 'none';
        document.getElementById('pdfSummarizer').style.display = 'block';
    });
});
