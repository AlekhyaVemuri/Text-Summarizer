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
    const pdfQueryInput = document.getElementById('pdfQueryInput');
    const pdfQueryButton=document.getElementById('pdfQueryButton');
    const answerListPdf = document.getElementById('answerListPdf');
    const selectedModelElement = document.getElementById('selectedModelElement');
    const loaderElement = document.querySelector('.loader');//loaders
    const urlQueryInput = document.getElementById('urlQueryInput');
    const urlQueryButton=document.getElementById('urlQueryButton');
    const answerList = document.getElementById('answerList');
    
    // Step 1: Select Model
    selectModelButton.addEventListener('click', () => {
        const selectedModel = modelSelect.value;
        
        if (!selectedModel) {
            alert('Please select a model.');
            return;
        }
        const modelName=selectedModel;
        if (modelName) {
            selectedModelElement.textContent = `Selected model: ${modelName}`;
          } else {
            console.error('Could not find the model name.');
          }
        
        // Hide the model selection and show the summarizers
            selectModelStep.classList.add('hidden');
            summarizersStep.classList.remove('hidden');
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
            urlQueryButton.classList.remove('hidden') ;
            urlQueryInput.classList.remove('hidden');
     
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
                    pdfQueryButton.classList.remove('hidden');
                    pdfQueryInput.classList.remove('hidden');
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

    
    //url query part

    async function fetchAnswer(query) {
        const response = await fetch('http://localhost:5000/your_query_url', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query: query })
        });
      
        if (!response.ok) {
          throw new Error('Error fetching answer: ' + response.statusText);
        }
        const data = await response.json();
        console.log(data.message);
        return data.message;
      }
      
        urlQueryButton.addEventListener('click', async () => {
            const query = urlQueryInput.value;
            if (!query) {
             return;
            }
      
            try {
            const answer = await fetchAnswer(query);
            const questionItem = document.createElement('li');
            questionItem.innerHTML = `<strong>Question:</strong> ${query}<br><strong>Answer:</strong> ${answer}`;
            answerList.appendChild(questionItem);
            urlQueryInput.value = '';
             } catch (error) {
                console.error(error);
            }
        });
    
    //functionality for pdf query input
    async function fetchAnswerPdf(query) {
        const response = await fetch('http://localhost:5000/your_query_pdf', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query: query })
        });
      
        if (!response.ok) {
          throw new Error('Error fetching answer: ' + response.statusText);
        }
        const data = await response.json();
        console.log(data.message);
        return data.message;
       }
      
        pdfQueryButton.addEventListener('click', async () => {
            const query = pdfQueryInput.value;
            if (!query) {
             return;
            }
    
            try {
            const answer = await fetchAnswerPdf(query);
            const questionItemPdf = document.createElement('li');
            questionItemPdf.innerHTML = `<strong>Question:</strong> ${query}<br><strong>Answer:</strong> ${answer}`;
            answerListPdf.appendChild(questionItemPdf);
            pdfQueryInput.value = '';
            } catch (error) {
                console.error(error);
            }
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
