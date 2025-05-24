from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import logging
import subprocess
from werkzeug.utils import secure_filename
from exam_processor import separate_exam_by_day as smu_export_processor
from exam_grp_proc import separate_exam_by_day as smart_scan_processor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/')
def home():
    return "Server is running!"

@app.route('/test', methods=['GET', 'OPTIONS'])
def test():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
        return response
    
    logger.info("Test endpoint called")
    return jsonify({"status": "Server is running!", "message": "Connection successful"})

# Configure maximum file size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/smu-export', methods=['POST'])
def smu_export():
    logger.info("Received request to /api/smu-export")
    if 'file' not in request.files:
        logger.error("No file in request")
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.error("Empty filename")
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        file_path = None
        try:
            logger.info(f"Processing file: {file.filename}")
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logger.info(f"File saved to: {file_path}")

            # Process the file using SMU export processor
            success, message = smu_export_processor(file_path)
            
            if success:
                logger.info("File processed successfully")
                # Ouvrir le dossier après succès
                try:
                    os.system('explorer "C:\\Exam_GRP_SMUAPP"')
                except Exception as e:
                    logger.error(f"Failed to open folder: {str(e)}")
                
                return jsonify({
                    'message': message,
                    'details': 'Files have been created in C:\\Exam_GRP_SMUAPP',
                    'openFolder': True
                })
            else:
                logger.error(f"Processing failed: {message}")
                return jsonify({'error': message}), 400
                
        except Exception as e:
            logger.exception("Error during file processing")
            return jsonify({
                'error': f'Error processing file: {str(e)}'
            }), 500
        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
    else:
        logger.error("Invalid file type")
        return jsonify({'error': 'Invalid file type. Please upload an Excel file (.xlsx, .xls) or CSV file.'}), 400

@app.route('/api/smart-scan-export', methods=['POST'])
def smart_scan_export():
    logger.info("Received request to /api/smart-scan-export")
    if 'file' not in request.files:
        logger.error("No file in request")
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.error("Empty filename")
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        file_path = None
        try:
            logger.info(f"Processing file: {file.filename}")
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logger.info(f"File saved to: {file_path}")
            
            # Process the file using Smart Scan processor
            success, message = smart_scan_processor(file_path)
            
            if success:
                logger.info("Smart Scan export completed successfully")
                return jsonify({
                    'message': 'Smart Scan export completed successfully',
                    'details': 'Files have been created in C:\\Exam_DAY_Smart'
                })
            else:
                logger.error(f"Smart Scan processing failed: {message}")
                return jsonify({'error': message}), 500
                
        except Exception as e:
            logger.exception("Error during file processing")
            return jsonify({
                'error': f'Error processing file: {str(e)}'
            }), 500
        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
    else:
        logger.error("Invalid file type")
        return jsonify({'error': 'Invalid file type. Please upload an Excel file (.xlsx, .xls) or CSV file.'}), 400

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=3001, debug=True)
