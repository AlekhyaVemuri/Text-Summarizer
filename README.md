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
   - Activate & Pin the loaded extension.
   
3. **Select an OpenVINO Model:**
   - Choose an OpenVINO IR format model previously converted from Huggingface.
   - <img width="250" alt="image" src="https://github.com/user-attachments/assets/cfeb665c-4c25-45cd-8ef8-f32efab46f78">


4. **Interact with the UI:**
   - Choose either **Web Page** or **PDF** post selecting one of the converted OV models:
   - <img width="263" alt="image" src="https://github.com/user-attachments/assets/022679a3-599f-43d9-9f6c-0d3ef8c94a89">

     - **Web Summarizer:**
       1. Enter the URL of the webpage to summarize.
       2. Click the "Summarize" button.
       3. After summarization, the text appears, and users can ask follow-up questions.

          <img width="262" alt="image" src="https://github.com/user-attachments/assets/91e7cd27-b097-4210-b613-c1231273c294">


     - **PDF Summarizer:**
       1. Upload a PDF file.
       2. Click "Upload & Summarize."
       3. After summarization, the text appears, and users can ask additional questions.

          <img width="265" alt="image" src="https://github.com/user-attachments/assets/c182a42f-3f83-450a-9ec7-d48144d0ef53">

5. **Reload the Page:**  
   - Refresh the webpage to restart the plugin.
