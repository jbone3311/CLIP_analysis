"""
Main Routes - Dashboard and core page routes
"""

from flask import Blueprint, render_template
from src.services.analysis_service import AnalysisService
from src.services.image_service import ImageService

main_bp = Blueprint('main', __name__)


def init_main_routes(app, analysis_service: AnalysisService, image_service: ImageService, processing_status: dict = None, db_manager = None, llm_manager = None):
    """Initialize main routes with services"""
    
    @app.route('/')
    def index():
        """Main dashboard"""
        analysis_files = analysis_service.get_analysis_files()
        image_files = image_service.get_image_files()
        
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
                             processing_status=processing_status or {})
    
    @app.route('/upload')
    def upload():
        """Upload page"""
        return render_template('upload.html')
    
    @app.route('/images')
    def images():
        """View uploaded images"""
        image_files = image_service.get_image_files()
        return render_template('images.html', images=image_files)
    
    @app.route('/results')
    def results():
        """View analysis results"""
        analysis_files = analysis_service.get_analysis_files()
        return render_template('results.html', analyses=analysis_files)
    
    @app.route('/process')
    def process():
        """Process page"""
        # Get current processing status
        current_status = processing_status or {'status': 'idle', 'message': 'Ready to process'}
        return render_template('process.html', processing_status=current_status)
    
    @app.route('/database')
    def database():
        """Database browser page"""
        # Get all results from database
        results = db_manager.get_all_results() if db_manager else []
        return render_template('database.html', results=results)
    
    @app.route('/llm-config')
    def llm_config():
        """LLM configuration page"""
        # Get LLM models and connection status
        configured_models = db_manager.get_llm_models() if db_manager else []
        available_models = llm_manager.get_all_available_models() if llm_manager else []
        
        # Check connection status (simplified for now)
        ollama_connected = False
        openai_connected = False
        anthropic_connected = False
        google_connected = False
        grok_connected = False
        
        return render_template('llm_config.html',
                             configured_models=configured_models,
                             available_models=available_models,
                             ollama_connected=ollama_connected,
                             openai_connected=openai_connected,
                             anthropic_connected=anthropic_connected,
                             google_connected=google_connected,
                             grok_connected=grok_connected)
    
    @app.route('/prompts')
    def prompts():
        """Prompt management page"""
        import os
        import json
        
        # Load prompts from the prompts.json file
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        prompts_file = os.path.join(project_root, 'src', 'config', 'prompts.json')
        prompts_data = {}
        
        if os.path.exists(prompts_file):
            try:
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    prompts_data = json.load(f)
            except Exception as e:
                print(f"Error loading prompts: {e}")
        
        return render_template('prompts.html', prompts=prompts_data) 