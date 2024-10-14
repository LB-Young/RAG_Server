from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
import shutil
from llm_client import LLMClient
from file_processor import FileProcessor

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = './upload_files/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

llm_client = LLMClient()
file_processor = FileProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == '123456':
        session['logged_in'] = True
        return redirect(url_for('chat'))
    return 'Invalid credentials'

@app.route('/chat')
def chat():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('chat.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_files = request.files.getlist('file')
    if not uploaded_files:
        return jsonify({'error': 'No file part'})
    
    processed_files = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            chunks = file_processor.process_file(file_path)
            processed_files.append({'filename': filename, 'chunks': len(chunks)})
    
    if processed_files:
        return jsonify({'message': 'Files processed successfully', 'files': processed_files})
    return jsonify({'error': 'No valid files uploaded'})

@app.route('/delete_file', methods=['POST'])
def delete_file():
    filename = request.json['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
    elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
    file_processor.remove_file_content(filename)
    return jsonify({'message': 'File deleted successfully'})

@app.route('/chat', methods=['POST'])
def process_chat():
    user_input = request.json['message']
    context = file_processor.get_context(user_input)
    prompt = f"Context: {context}\n\nQuestion: {user_input}"
    response = llm_client.ado_requests(prompt)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
