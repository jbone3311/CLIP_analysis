#!/usr/bin/env python3
"""
Web Interface for Image Analysis with CLIP and LLM

A modern Flask web application providing a user-friendly interface
for uploading images, viewing results, and managing configurations.
"""

import os
import json
import sys
import webbrowser
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from directory_processor import DirectoryProcessor
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'Images'
OUTPUT_FOLDER = 'Output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Global variables
processing_status = {}
processing_threads = {}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_analysis_files():
    """Get list of analysis files"""
    analysis_files = []
    if os.path.exists(OUTPUT_FOLDER):
        for file in os.listdir(OUTPUT_FOLDER):
            if file.endswith('_analysis.json'):
                file_path = os.path.join(OUTPUT_FOLDER, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        analysis_files.append({
                            'filename': file,
                            'original_image': data.get('file_info', {}).get('filename', 'Unknown'),
                            'status': data.get('processing_info', {}).get('status', 'unknown'),
                            'processing_time': data.get('processing_info', {}).get('processing_time', 0),
                            'date_processed': data.get('file_info', {}).get('date_processed', ''),
                            'file_size': data.get('file_info', {}).get('file_size', 0),
                            'has_clip': bool(data.get('analysis', {}).get('clip')),
                            'has_llm': bool(data.get('analysis', {}).get('llm')),
                            'has_metadata': bool(data.get('analysis', {}).get('metadata'))
                        })
                except Exception as e:
                    print(f"Error loading {file}: {e}")
    return sorted(analysis_files, key=lambda x: x['date_processed'], reverse=True)

def get_image_files():
    """Get list of uploaded images"""
    image_files = []
    if os.path.exists(UPLOAD_FOLDER):
        for root, dirs, files in os.walk(UPLOAD_FOLDER):
            for file in files:
                if allowed_file(file):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, UPLOAD_FOLDER)
                    image_files.append({
                        'filename': file,
                        'path': rel_path,
                        'full_path': file_path,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
    return sorted(image_files, key=lambda x: x['modified'], reverse=True)

def process_images_async():
    """Process images in background thread"""
    try:
        processor = DirectoryProcessor()
        processor.process_directory()
        processing_status['status'] = 'completed'
        processing_status['message'] = 'Processing completed successfully!'
    except Exception as e:
        processing_status['status'] = 'error'
        processing_status['message'] = f'Error during processing: {str(e)}'

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)  # Wait for server to start
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Browser opened automatically!")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("📱 Please open your browser and navigate to: http://localhost:5000")

@app.route('/')
def index():
    """Main dashboard"""
    analysis_files = get_analysis_files()
    image_files = get_image_files()
    
    # Get system stats
    total_images = len(image_files)
    total_analyses = len(analysis_files)
    completed_analyses = len([f for f in analysis_files if f['status'] == 'complete'])
    
    # Get recent activity
    recent_analyses = analysis_files[:5]
    
    return render_template('dashboard.html',
                         total_images=total_images,
                         total_analyses=total_analyses,
                         completed_analyses=completed_analyses,
                         recent_analyses=recent_analyses,
                         processing_status=processing_status)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle file uploads"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('file')
        uploaded_count = 0
        
        for file in files:
            if file.filename == '':
                continue
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Create subdirectory if specified
                subfolder = request.form.get('subfolder', '').strip()
                if subfolder:
                    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
                    os.makedirs(upload_path, exist_ok=True)
                    filepath = os.path.join(upload_path, filename)
                else:
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                try:
                    file.save(filepath)
                    uploaded_count += 1
                except Exception as e:
                    flash(f'Error saving {filename}: {str(e)}', 'error')
        
        if uploaded_count > 0:
            flash(f'Successfully uploaded {uploaded_count} file(s)', 'success')
        
        return redirect(url_for('upload'))
    
    return render_template('upload.html')

@app.route('/images')
def images():
    """View uploaded images"""
    image_files = get_image_files()
    return render_template('images.html', images=image_files)

@app.route('/results')
def results():
    """View analysis results"""
    analysis_files = get_analysis_files()
    return render_template('results.html', analyses=analysis_files)

@app.route('/result/<filename>')
def view_result(filename):
    """View specific analysis result"""
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        flash('Analysis file not found', 'error')
        return redirect(url_for('results'))
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return render_template('result_detail.html', data=data, filename=filename)
    except Exception as e:
        flash(f'Error loading analysis: {str(e)}', 'error')
        return redirect(url_for('results'))

@app.route('/process', methods=['GET', 'POST'])
def process():
    """Process images"""
    if request.method == 'POST':
        if processing_status.get('status') == 'processing':
            flash('Processing already in progress', 'warning')
            return redirect(url_for('process'))
        
        # Start processing in background
        processing_status['status'] = 'processing'
        processing_status['message'] = 'Starting image processing...'
        processing_status['start_time'] = datetime.now().isoformat()
        
        thread = threading.Thread(target=process_images_async)
        thread.daemon = True
        thread.start()
        processing_threads['main'] = thread
        
        flash('Processing started! Check status for updates.', 'success')
        return redirect(url_for('process'))
    
    return render_template('process.html', status=processing_status)

@app.route('/status')
def status():
    """Get processing status"""
    return jsonify(processing_status)

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration management"""
    if request.method == 'POST':
        try:
            # Update configuration
            config_data = request.get_json()
            config_manager.update_config(config_data)
            flash('Configuration updated successfully', 'success')
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    # Get current configuration
    current_config = config_manager.get_config()
    return render_template('config.html', config=current_config)

@app.route('/download/<filename>')
def download_result(filename):
    """Download analysis result"""
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found', 'error')
        return redirect(url_for('results'))

@app.route('/api/analysis/<filename>')
def api_analysis(filename):
    """API endpoint to get analysis data"""
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    print("🌐 Starting Web Interface...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"📁 Output folder: {OUTPUT_FOLDER}")
    print("🚀 Server starting at http://localhost:5000")
    
    # Start browser opening in background thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 