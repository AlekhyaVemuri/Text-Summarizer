from flask import Flask, request, jsonify
from flask_cors import CORS
from code import web_out, pdf_out
import tempfile
import os

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# URL processing code
@app.route('/process-url', methods=['POST'])
def process_url():
    data = request.get_json()
    url = data.get('url')
    model_id = data.get('model_id', 'NousResearch/Llama-2-7b-chat-hf')  

    if not url:
        return jsonify({'message': 'No URL provided'}), 400
    
    response_message = str(web_out([url], model_id))
    
    return jsonify({"message": response_message})

# PDF processing code
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({"message": "No PDF file found"}), 400
    
    pdf_file = request.files['pdf']
    model_id = request.form.get('model_id', 'NousResearch/Llama-2-7b-chat-hf')  

    if pdf_file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if pdf_file and pdf_file.content_type == 'application/pdf':
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                pdf_file.save(temp_pdf.name)
                temp_pdf_path = temp_pdf.name
                print(temp_pdf_path)
            
            response_message = str(pdf_out(temp_pdf_path, model_id))  
            
            os.remove(temp_pdf_path)

            return jsonify({"message": response_message})

        except Exception as e:
            return jsonify({"message": f"Error processing PDF: {str(e)}"}), 500

    else:
        return jsonify({"message": "Invalid file type. Please upload a PDF."}), 400

if __name__ == '__main__':
    app.run(port=5000)
