from flask import Flask, request, jsonify, send_file, render_template_string
import os
import subprocess
from werkzeug.utils import secure_filename
import tempfile
import uuid

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.mp4'}

# Store temporary file paths for download
temp_files = {}

def allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

@app.route('/')
def index():
    # Serve the HTML file
    try:
        with open('index.html', 'r') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "Frontend file (index.html) not found", 404

@app.route('/api/convert', methods=['POST'])
def convert_endpoint():
    format_ = request.form.get('format', 'mp3').lower()
    if format_ not in ['mp3', 'wav', 'm4a']:
        return jsonify({"error": "Invalid format"}), 400

    uploaded_files = request.files.getlist('files[]')
    results = []

    output_folder = tempfile.mkdtemp()

    for file in uploaded_files:
        if not allowed_file(file.filename):
            results.append({
                "name": file.filename,
                "status": "error",
                "message": "Unsupported file type"
            })
            continue

        safe_name = secure_filename(file.filename)
        input_path = os.path.join(output_folder, safe_name)
        file.save(input_path)

        base_name = os.path.splitext(safe_name)[0]
        output_file = os.path.join(output_folder, f"{base_name}.{format_}")

        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", input_path, output_file],
                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True
            )
            
            # Generate unique file ID for download
            file_id = str(uuid.uuid4())
            temp_files[file_id] = output_file
            
            results.append({
                "name": file.filename,
                "status": "success",
                "message": "Converted successfully",
                "download_url": f"/download/{file_id}"
            })
        except subprocess.CalledProcessError:
            results.append({
                "name": file.filename,
                "status": "error",
                "message": "Conversion failed"
            })

    return jsonify({"results": results})

@app.route('/download/<file_id>')
def download_file(file_id):
    if file_id not in temp_files:
        return jsonify({"error": "File not found"}), 404
    
    file_path = temp_files[file_id]
    if not os.path.exists(file_path):
        return jsonify({"error": "File no longer exists"}), 404
    
    # Clean up after sending
    def remove_file():
        try:
            os.remove(file_path)
            del temp_files[file_id]
        except:
            pass
    
    return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Changed port to avoid conflict
