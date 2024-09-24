## Description

A Chrome plugin, built using Flask, leverages an OpenVINO backend to efficiently summarize any webpage via a URL or any PDF via an upload. The plugin utilizes Langchain tools for tasks such as text splitting and managing a vectorstore.

## Prerequisites

1. **Create a Conda Environment:**
   - Run the command:  
     `conda create -n llm python=3.11 libuv`

2. **Install Dependencies:**
   - Execute:  
     `pip install -r requirements.txt`

3. **Download and Convert the Huggingface Model to OpenVINO IR Format:**
   - Log in to Huggingface:  
     `huggingface-cli login`
   - Generate a token from Huggingface. For private or gated models, refer to Huggingface Hub's documentation.
   - Convert the model using `optimum-cli`:
     ```
     optimum-cli export openvino --model meta-llama/Llama-2-7b-chat-hf --weight-format int8 ov_llama_2
     ```

4. **Clone the Repository and Load the Extension:**
   - In Chrome Developer mode, use the "Load Unpacked Extension" option to add the plugin. Refer to Chrome’s development documentation for further details.

## Sample Structure

The directory contains:
- **backend:** Includes `code.py` and `server.py` for processing text from webpages or PDFs and managing Flask-related operations.
- **extension:** Contains `manifest.json` for the Chrome extension along with `popup.html`, `popup.js`, and `style.css` for the user interface.

## Steps to Run the Plugin

1. **Start the Flask Server:**
   - Navigate to the backend folder:
     ```
     cd Quick-Gist/backend
     python server.py
     ```

2. **Open the Chrome Browser:**
   - Activate the loaded extension.

3. **Select an OpenVINO Model:**
   - Choose an OpenVINO IR format model previously converted from Huggingface.

4. **Interact with the UI:**
   - Choose either **Web Summarizer** or **PDF Summarizer**:
     - **Web Summarizer:**
       1. Enter the URL of the webpage to summarize.
       2. Click the "Summarize" button.
       3. After summarization, the text appears, and users can ask follow-up questions.
     - **PDF Summarizer:**
       1. Upload a PDF file.
       2. Click "Upload & Summarize."
       3. After summarization, the text appears, and users can ask additional questions.

5. **Reload the Page:**  
   - Refresh the webpage to restart the plugin.
