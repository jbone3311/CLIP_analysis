#!/usr/bin/env python3
"""
Refactored Web Interface for Image Analysis with CLIP and LLM

A modern Flask web application with modular architecture providing
a user-friendly interface for uploading images, viewing results, and managing configurations.
"""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path
from typing import Dict, Any

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.processors.directory_processor import DirectoryProcessor
from src.database.db_manager import DatabaseManager
from src.analyzers.llm_manager import LLMManager
from src.services.analysis_service import AnalysisService
from src.services.image_service import ImageService
from src.services.config_service import ConfigService
from src.routes.main_routes import init_main_routes
from src.routes.api_routes import init_api_routes
from src.utils.logger import get_global_logger
from src.utils.error_handler import handle_errors, ErrorCategory, error_context
from dotenv import load_dotenv

logger = get_global_logger()


class WebInterface:
    """Refactored web interface with modular architecture"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        logger.info("Initializing Web Interface", data={'project_root': self.project_root})
        
        # Load environment variables
        load_dotenv()
        
        # Configuration
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        self.max_content_length = 50 * 1024 * 1024  # 50MB max file size
        self.web_port = int(os.getenv('WEB_PORT', '5050'))
        
        # Initialize services
        self.config_service = ConfigService(self.project_root)
        self.analysis_service = AnalysisService(
            output_folder=os.path.join(self.project_root, 'Output'),
            upload_folder=os.path.join(self.project_root, 'Images')
        )
        self.image_service = ImageService(
            upload_folder=os.path.join(self.project_root, 'Images'),
            allowed_extensions=self.allowed_extensions
        )
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.llm_manager = LLMManager()
        
        # Processing state
        self.processing_status = {'status': 'idle', 'message': 'Ready to process'}
        self.processing_threads = {}
        
        # Create Flask app
        self.app = self._create_app()
        
        # Initialize routes
        self._init_routes()
        
        logger.info("Web Interface initialized successfully")
    
    def _create_app(self) -> Flask:
        """Create and configure Flask application"""
        app = Flask(__name__, 
                    template_folder='templates',
                    static_folder='static')
        app.secret_key = 'your-secret-key-here'  # Change this in production
        
        # Configure app
        app.config['UPLOAD_FOLDER'] = os.path.join(self.project_root, 'Images')
        app.config['MAX_CONTENT_LENGTH'] = self.max_content_length
        
        return app
    
    def _init_routes(self):
        """Initialize all routes"""
        # Initialize main routes
        init_main_routes(
            self.app, 
            self.analysis_service, 
            self.image_service,
            self.processing_status,
            self.db_manager,
            self.llm_manager
        )
        
        # Initialize API routes
        init_api_routes(
            self.app,
            self.analysis_service,
            self.image_service,
            self.config_service,
            self.db_manager,
            self.llm_manager,
            os.path.join(self.project_root, 'Output')
        )
        
        # Add remaining routes that need special handling
        self._add_special_routes()
    
    def _add_special_routes(self):
        """Add routes that need special handling or access to instance variables"""
        
        @self.app.route('/upload', methods=['POST'])
        def upload_post():
            """Handle file uploads"""
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            filename = self.image_service.save_uploaded_file(file)
            if filename:
                flash(f'File {filename} uploaded successfully!', 'success')
            else:
                flash('Invalid file type', 'error')
            
            return redirect(url_for('upload'))
        
        @self.app.route('/result/<path:filename>')
        def view_result(filename):
            """View specific analysis result"""
            data = self.analysis_service.get_analysis_data(filename)
            if data is None:
                flash('Analysis file not found', 'error')
                return redirect(url_for('results'))
            
            return render_template('result_detail.html', data=data, filename=filename)
        
        @self.app.route('/download/<path:filename>')
        def download_result(filename):
            """Download analysis result"""
            file_path = os.path.join(self.project_root, 'Output', filename)
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
            else:
                flash('File not found', 'error')
                return redirect(url_for('results'))
        
        @self.app.route('/config', methods=['GET', 'POST'])
        def config():
            """Configuration management"""
            if request.method == 'POST':
                try:
                    config_data = request.get_json()
                    if self.config_service.update_config(config_data):
                        return jsonify({'status': 'success', 'message': 'Configuration saved successfully'})
                    else:
                        return jsonify({'status': 'error', 'message': 'Failed to save configuration'})
                except Exception as e:
                    return jsonify({'status': 'error', 'message': str(e)})
            
            # Get current configuration
            current_config = self.config_service.get_config()
            return render_template('config.html', config=current_config)
        
        @self.app.route('/process', methods=['POST'])
        def process_post():
            """Start image processing"""
            if self.processing_status.get('status') == 'processing':
                flash('Processing already in progress', 'warning')
                return redirect(url_for('process'))
            
            # Start processing in background
            self.processing_status['status'] = 'processing'
            self.processing_status['message'] = 'Starting image processing...'
            self.processing_status['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            thread = threading.Thread(target=self._process_images_async)
            thread.daemon = True
            thread.start()
            self.processing_threads['main'] = thread
            
            flash('Processing started! Check status for updates.', 'success')
            return redirect(url_for('process'))
        
        @self.app.route('/status')
        def status():
            """Get processing status"""
            return jsonify(self.processing_status)
    
    def _process_images_async(self):
        """Process images in background thread"""
        try:
            config = self.config_service.get_processing_config()
            processor = DirectoryProcessor(config)
            processor.process_directory()
            self.processing_status['status'] = 'completed'
            self.processing_status['message'] = 'Processing completed successfully!'
        except Exception as e:
            self.processing_status['status'] = 'error'
            self.processing_status['message'] = f'Error during processing: {str(e)}'
    
    def _open_browser(self):
        """Open browser after a short delay"""
        time.sleep(1.5)  # Wait for server to start
        try:
            webbrowser.open(f'http://localhost:{self.web_port}')
            print("🌐 Browser opened automatically!")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"📱 Please open your browser and navigate to: http://localhost:{self.web_port}")
    
    def run(self, debug: bool = True, host: str = '0.0.0.0', port: int = None):
        """Run the web interface"""
        if port is None:
            port = self.web_port
        
        # Create necessary directories
        os.makedirs(os.path.join(self.project_root, 'Images'), exist_ok=True)
        os.makedirs(os.path.join(self.project_root, 'Output'), exist_ok=True)
        
        print("🌐 Starting Refactored Web Interface...")
        print(f"📁 Project root: {self.project_root}")
        print(f"📁 Upload folder: {os.path.join(self.project_root, 'Images')}")
        print(f"📁 Output folder: {os.path.join(self.project_root, 'Output')}")
        print(f"🚀 Server starting at http://localhost:{port}")
        
        # Start browser opening in background thread
        browser_thread = threading.Thread(target=self._open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        self.app.run(debug=debug, host=host, port=port)


def create_app():
    """Factory function to create Flask app for testing"""
    interface = WebInterface()
    return interface.app


if __name__ == '__main__':
    interface = WebInterface()
    interface.run() 