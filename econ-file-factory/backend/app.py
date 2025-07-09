import os
import io
import zipfile
import json
from flask import Flask, request, send_file, jsonify
import pandas as pd
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import load_dotenv
from pipeline import DataHarmonizationPipeline

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'zip'}
MAX_FILES = 20
UPLOAD_FOLDER = 'uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_files(file_storage):
    """Extracts files from a ZIP or returns the file itself if not a ZIP."""
    filename = secure_filename(file_storage.filename)
    if filename.endswith('.zip'):
        with zipfile.ZipFile(file_storage) as z:
            return [
                (name, io.BytesIO(z.read(name)))
                for name in z.namelist()
                if allowed_file(name)
            ]
    else:
        return [(filename, file_storage.stream)]

def read_to_dataframe(filename, file_stream):
    if filename.endswith('.csv'):
        return pd.read_csv(file_stream)
    elif filename.endswith('.xlsx'):
        return pd.read_excel(file_stream)
    else:
        return None

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    print(f"Received {len(files)} file(s) for wrangling...")
    if len(files) == 0:
        return jsonify({'error': 'No files uploaded.'}), 400
    if len(files) > MAX_FILES:
        return jsonify({'error': f'Maximum {MAX_FILES} files allowed per upload.'}), 400

    file_streams = []
    filenames = []
    for file_storage in files:
        if not file_storage.filename or not allowed_file(file_storage.filename):
            continue
        filename = secure_filename(str(file_storage.filename))
        if filename.endswith('.zip'):
            file_storage.stream.seek(0)
            with zipfile.ZipFile(file_storage.stream) as z:
                for name in z.namelist():
                    if allowed_file(name):
                        file_stream = io.BytesIO(z.read(name))
                        file_streams.append(file_stream)
                        filenames.append(name)
        else:
            file_storage.stream.seek(0)
            file_streams.append(file_storage.stream)
            filenames.append(filename)

    if not file_streams:
        return jsonify({'error': 'No valid data files found.'}), 400

    # Get OpenAI settings from environment or request
    api_key = os.getenv('OPENAI_API_KEY')
    use_openai = request.form.get('use_openai', 'true').lower() == 'true'
    if 'api_key' in request.form and request.form['api_key']:
        api_key = request.form['api_key']

    pipeline = DataHarmonizationPipeline(api_key=api_key, use_openai=use_openai)
    result = pipeline.run(file_streams, filenames)

    if not result.get('success', False):
        return jsonify({'error': result.get('error', 'Unknown error'), 'audit_trail': result.get('audit_trail', {})}), 500

    master_clean = result['master_df']
    dupes = result['duplicates_df']
    audit_report = result['audit_report']
    # output_file = result['output_file']  # Not used directly here

    # Output to CSV in memory
    output = io.StringIO()
    master_clean.to_csv(output, index=False, na_rep='NaN')

    # Add duplicate records section
    output.write('\n# Duplicate Records\n')
    if not dupes.empty:
        dupes.to_csv(output, index=False, na_rep='NaN')

    # Add audit report section (as JSON for now)
    output.write('\n# Audit Report\n')
    output.write(json.dumps(audit_report, indent=2))

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='cleaned.csv'
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'openai_configured': bool(os.getenv('OPENAI_API_KEY'))
    })

if __name__ == '__main__':
    app.run(debug=True) 