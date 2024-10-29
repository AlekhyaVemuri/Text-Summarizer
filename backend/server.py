import time
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from code import load_llm, web_out, pdf_out,pdf_query,url_query
import tempfile
import chromadb
 
app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

#Loading model 
@app.route('/select-model', methods=['POST'])
def select_model():
    """
        Model selection function which would further trigger Model compilation function.
    """
    global current_model
    data = request.get_json()
    model_id = data.get('model_id')
    if not model_id:
        return jsonify({'message': 'No model ID provided'}), 400
    # Load and compile the model once
    current_model = load_llm(model_id)
    if current_model:
        return jsonify({'message': f'Model {model_id} loaded successfully.'}), 200
    else:
        return jsonify({'message': 'Failed to load model.'}), 500

# @app.route('/stream-output', methods=['POST'])
def stream_output(process_function, *args):
    """
        Generator function to stream output from a process function.
    """
    for chunk in process_function(*args):
        if chunk is not None:
            # print(f"Sending chunk: {chunk}")  # Debugging
            yield f"{chunk}"
            # time.sleep(0.1)
 
# URL processing code
@app.route('/process-url', methods=['POST'])
def process_url():
    """
        Fetches URL from the plugin & triggers the URL summarization function.
    """
    data = request.get_json()
    url = data.get('url')
    # model_id = current_model  
    if not url:
        return jsonify({'message': 'No URL provided'}), 400

    chromadb.api.client.SharedSystemClient.clear_system_cache()
    return Response(stream_output(web_out, [url]), content_type='text/event-stream')
    
 
# PDF processing code
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """
        Once the PDF's uploaded, the PDF Summarization function's triggered.
    """
    if 'pdf' not in request.files:
        return jsonify({"message": "No PDF file found"}), 400
    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if pdf_file and pdf_file.content_type == 'application/pdf':
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                pdf_file.save(temp_pdf.name)
                temp_pdf_path = temp_pdf.name
                print(temp_pdf_path)
           
            chromadb.api.client.SharedSystemClient.clear_system_cache()
            return Response(stream_output(pdf_out, temp_pdf_path), content_type='text/event-stream')
        except Exception as e:
            return jsonify({"message": f"Error processing PDF: {str(e)}"}), 500
    else:
        return jsonify({"message": "Invalid file type. Please upload a PDF."}), 400
 
#QA BoT code for pdf starts here
@app.route('/your_query_pdf', methods=['POST'])
def pdf_process_query():
    data = request.get_json()
    model_id = current_model  
    query=data.get('query')
    if not data:
        return jsonify({'message':'no query provided'}),400
    response_message=str(pdf_query(query,model_id))
    return jsonify({'message': response_message})
 
#QA BoT for url starts here
@app.route('/your_query_url', methods=['POST'])
def url_process_query():
    data = request.get_json()
    print(data)
    model_id = request.form.get('model_id')  
    query=data.get('query')
    if not data:
        return jsonify({'message':'no query provided'}),400
    response_message=str(url_query(query,model_id))
    print(response_message)
    return jsonify({'message': response_message}) 
 
if __name__ == '__main__':
    app.run(port=5000)
 
