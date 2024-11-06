## Description

A Chrome plugin, built using Flask, leverages an OpenVINO backend to efficiently summarize any webpage via a URL or any PDF via an upload. The plugin utilizes Langchain tools for tasks such as text splitting and managing a vectorstore.

## Prerequisites

1. **Install the below necessary tools/packages:**
   - [Git on Windows](https://git-scm.com/downloads)
   - [Miniforge](https://conda-forge.org/download/)
   - [Google Chrome for Windows](https://www.google.com/chrome/?brand=OZZY&ds_kid=43700080794581137&gad_source=1&gclid=Cj0KCQiAoae5BhCNARIsADVLzZdwNNB5nIyjZ8OyCzg6h_cCig1eoaYquUSEd7BAigJhTzps1Kxuop8aArE6EALw_wcB&gclsrc=aw.ds)

2. **Clone the Repository**
   ```
   git clone -b OpenVINO-backend https://github.com/AlekhyaVemuri/Text-Summarizer.git
   ```
   
3. **Create a Conda Environment:**
   - Run the command:
     ```
     conda create -n summarizer_plugin python=3.11 libuv
     ```
     ```
     conda activate summarizer_plugin
     ```

4. **Install Dependencies:**
   - Execute:
     ```
     cd Text-Summarizer
     ```
     ```
     pip install -r requirements.txt
     ```
     
     >**Note**: Run your terminal as admin to avoid any permission issues.
     

5. **Download and Convert the Huggingface Model to OpenVINO IR Format:**
   - Log in to Huggingface:
     ```
     huggingface-cli login
     ```
   - Generate a token from Huggingface. For private or gated models, refer to [Huggingface documentation](https://huggingface.co/docs/hub/en/models-gated).
   - Convert the model using `optimum-cli`:
     ```
     mkdir models
     cd models
     optimum-cli export openvino --model meta-llama/Llama-2-7b-chat-hf --weight-format int4 ov_llama_2
     optimum-cli export openvino --model Qwen/Qwen2-7B-Instruct --weight-format int4 ov_qwen7b
     
     ```
     >**Note**: [Raise access request](https://www.llama.com/llama-downloads) for Llama models as it is a gated repository.

6. In code.py, around line numbers 53 and 55 (or wherever the model paths are referenced), update the code to explicitly set the paths to your local model files.Replace **"Path to ov_llama_2 folder"/ "Path to ov_qwen7b folder"** with the actual path to your model folder on your local machine.Ensure proper file permissions so the script can access the model files.


8. **Load the Extension:**
   - In Chrome Developer mode, use the "Load Unpacked Extension" option to add the plugin. Refer to [Chrome’s development documentation](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#load-unpacked) for further details.
     
     <img width="308" alt="image" src="https://github.com/user-attachments/assets/99a95942-93ea-4ec4-9ea8-6c10bcb98235">
9. **Pin the Extension:**

   <img width="245" alt="image" src="https://github.com/user-attachments/assets/9ed9a0de-56da-4e5b-a5f0-41297e06b8a7">



## Sample Structure

The directory contains:
- **backend:** Includes `code.py` and `server.py` for processing text from webpages or PDFs and managing Flask-related operations.
- **extension:** Contains `manifest.json` for the Chrome extension along with `popup.html`, `popup.js`, and `style.css` for the user interface.

## Steps to Run the Plugin

1. **Start the Flask Server:**
   - Navigate to the backend folder:
     ```
     cd Text-Summarizer/backend
     python server.py
     ```

2. **Open the Chrome Browser:**
   - Activate & Pin the loaded extension.
   - Plugin UI looks as follows:

      <img width="286" alt="image" src="https://github.com/user-attachments/assets/37349acc-ff37-437b-928a-673ca4ad3986">

   
3. **Select an OpenVINO Model:**
   - Choose an OpenVINO IR format model previously converted from Huggingface.

     <img width="286" alt="image" src="https://github.com/user-attachments/assets/953050c9-c64c-4ce6-831d-626a52547d0b">


4. **Interact with the UI:**
   - Choose either **Web Page** or **PDF** post selecting one of the converted OV models:

     <img width="285" alt="image" src="https://github.com/user-attachments/assets/065022e9-c9a2-474c-ae4e-5a2f298a9934">


     - **Web Summarizer:**
       1. Enter the URL of the webpage to summarize.
       2. Click the "Summarize" button.
       3. After summarization, the text appears, and users can ask follow-up questions.

          <img width="287" alt="image" src="https://github.com/user-attachments/assets/5f308ad3-b5bc-4b3e-9d29-b8002dc88e29">



     - **PDF Summarizer:**
       1. Upload a PDF file.
       2. Click "Upload & Summarize."
       3. After summarization, the text appears, and users can ask additional questions.

          <img width="290" alt="image" src="https://github.com/user-attachments/assets/4d6e3ce0-1650-4cd0-a073-0e84891518a3">
      
       4. Sample output post summarization.
          
          <img width="300" alt="image" src="https://github.com/user-attachments/assets/ea05eca2-fa53-4b17-9c85-67a692607376">


5. **Reload the Page:**  
   - Refresh the webpage or re-open the plugin to restart.
