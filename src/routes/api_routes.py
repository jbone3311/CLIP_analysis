"""
API Routes - REST API endpoints
"""

from flask import Blueprint, request, jsonify, send_file, flash, redirect, url_for
import os
import json
from src.services.analysis_service import AnalysisService
from src.services.image_service import ImageService
from src.services.config_service import ConfigService
from src.database.db_manager import DatabaseManager
from src.analyzers.llm_manager import LLMManager

api_bp = Blueprint('api', __name__)


def init_api_routes(app, analysis_service: AnalysisService, image_service: ImageService, 
                   config_service: ConfigService, db_manager: DatabaseManager, 
                   llm_manager: LLMManager, output_folder: str):
    """Initialize API routes with services"""
    
    @app.route('/api/analysis/<path:filename>')
    def api_analysis(filename):
        """API endpoint to get analysis data"""
        data = analysis_service.get_analysis_data(filename)
        if data is None:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify(data)
    
    @app.route('/api/config', methods=['POST'])
    def api_config_update():
        """API endpoint to update configuration"""
        try:
            config_data = request.get_json()
            if config_service.update_config(config_data):
                return jsonify({'status': 'success', 'message': 'Configuration saved successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to save configuration'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/api/config', methods=['GET'])
    def api_config_get():
        """API endpoint to get current configuration"""
        return jsonify(config_service.get_config())
    
    @app.route('/api/upload', methods=['POST'])
    def api_upload():
        """API endpoint to handle file uploads"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = image_service.save_uploaded_file(file)
        if filename:
            return jsonify({'status': 'success', 'filename': filename})
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    
    @app.route('/api/download/<path:filename>')
    def api_download(filename):
        """API endpoint to download analysis result"""
        file_path = os.path.join(output_folder, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    
    @app.route('/api/database/results')
    def api_database_results():
        """API endpoint to get all database results"""
        try:
            results = db_manager.get_all_results()
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/database/result/<int:result_id>')
    def api_database_result(result_id):
        """API endpoint to get database result by ID"""
        try:
            result = db_manager.get_result_by_id(result_id)
            if result:
                # Parse JSON fields
                result['modes'] = json.loads(result['modes']) if result['modes'] else []
                result['prompts'] = json.loads(result['prompts']) if result['prompts'] else {}
                result['analysis_results'] = json.loads(result['analysis_results']) if result['analysis_results'] else {}
                result['settings'] = json.loads(result['settings']) if result['settings'] else {}
                result['llm_results'] = json.loads(result['llm_results']) if result['llm_results'] else {}
                return jsonify(result)
            else:
                return jsonify({'error': 'Result not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/llm/models')
    def api_llm_models():
        """API endpoint to get available LLM models"""
        try:
            models = llm_manager.get_all_available_models()
            return jsonify(models)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/llm/configured')
    def api_llm_configured():
        """API endpoint to get configured LLM models"""
        try:
            models = db_manager.get_llm_models()
            return jsonify(models)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/llm/add', methods=['POST'])
    def api_llm_add():
        """API endpoint to add LLM model"""
        try:
            data = request.get_json()
            model_id = db_manager.add_llm_model(
                provider=data['provider'],
                model_name=data['model_name'],
                prompts=data.get('prompts', {})
            )
            return jsonify({'status': 'success', 'model_id': model_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/llm/delete/<int:model_id>', methods=['DELETE'])
    def api_llm_delete(model_id):
        """API endpoint to delete LLM model"""
        try:
            db_manager.delete_llm_model(model_id)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/llm/update-prompts/<int:model_id>', methods=['POST'])
    def api_llm_update_prompts(model_id):
        """API endpoint to update LLM model prompts"""
        try:
            data = request.get_json()
            db_manager.update_llm_model_prompts(model_id, data['prompts'])
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/status')
    def api_status():
        """API endpoint to get processing status"""
        # This would need to be passed from the main app
        return jsonify({'status': 'idle', 'message': 'No processing in progress'})
    
    # Prompts API routes
    @app.route('/api/prompts', methods=['GET'])
    def api_prompts_get():
        """Get all prompts"""
        try:
            from src.routes.prompts_routes import load_prompts
            prompts = load_prompts()
            return jsonify({
                'success': True,
                'prompts': prompts,
                'count': len(prompts)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/prompts/<prompt_id>', methods=['GET'])
    def api_prompts_get_one(prompt_id):
        """Get a specific prompt"""
        try:
            from src.routes.prompts_routes import load_prompts
            prompts = load_prompts()
            
            if prompt_id not in prompts:
                return jsonify({
                    'success': False,
                    'error': 'Prompt not found'
                }), 404
            
            return jsonify({
                'success': True,
                'prompt': prompts[prompt_id]
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/prompts', methods=['POST'])
    def api_prompts_create():
        """Create a new prompt"""
        try:
            from src.routes.prompts_routes import load_prompts, save_prompts, validate_prompt
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            prompt_id = data.get('promptId')
            prompt_data = data.get('prompt')
            
            if not prompt_id or not prompt_data:
                return jsonify({
                    'success': False,
                    'error': 'Missing promptId or prompt data'
                }), 400
            
            # Validate prompt data
            is_valid, error_msg = validate_prompt(prompt_data)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 400
            
            prompts = load_prompts()
            
            if prompt_id in prompts:
                return jsonify({
                    'success': False,
                    'error': 'Prompt ID already exists'
                }), 409
            
            # Add metadata
            from datetime import datetime
            prompt_data['CREATED_AT'] = datetime.now().isoformat()
            prompt_data['UPDATED_AT'] = datetime.now().isoformat()
            
            prompts[prompt_id] = prompt_data
            
            if save_prompts(prompts):
                return jsonify({
                    'success': True,
                    'prompt_id': prompt_id,
                    'message': 'Prompt created successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to save prompt'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/prompts/<prompt_id>', methods=['PUT'])
    def api_prompts_update(prompt_id):
        """Update an existing prompt"""
        try:
            from src.routes.prompts_routes import load_prompts, save_prompts, validate_prompt
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            prompt_data = data.get('prompt')
            if not prompt_data:
                return jsonify({
                    'success': False,
                    'error': 'Missing prompt data'
                }), 400
            
            # Validate prompt data
            is_valid, error_msg = validate_prompt(prompt_data)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 400
            
            prompts = load_prompts()
            
            if prompt_id not in prompts:
                return jsonify({
                    'success': False,
                    'error': 'Prompt not found'
                }), 404
            
            # Update metadata
            from datetime import datetime
            prompt_data['UPDATED_AT'] = datetime.now().isoformat()
            prompt_data['CREATED_AT'] = prompts[prompt_id].get('CREATED_AT', datetime.now().isoformat())
            
            prompts[prompt_id] = prompt_data
            
            if save_prompts(prompts):
                return jsonify({
                    'success': True,
                    'message': 'Prompt updated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to save prompt'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
    def api_prompts_delete(prompt_id):
        """Delete a prompt"""
        try:
            from src.routes.prompts_routes import load_prompts, save_prompts
            prompts = load_prompts()
            
            if prompt_id not in prompts:
                return jsonify({
                    'success': False,
                    'error': 'Prompt not found'
                }), 404
            
            deleted_prompt = prompts.pop(prompt_id)
            
            if save_prompts(prompts):
                return jsonify({
                    'success': True,
                    'message': 'Prompt deleted successfully',
                    'deleted_prompt': deleted_prompt
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to save prompts after deletion'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/prompts/import', methods=['POST'])
    def api_prompts_import():
        """Import prompts from JSON data"""
        try:
            from src.routes.prompts_routes import load_prompts, save_prompts, validate_prompt
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            prompts = load_prompts()
            imported_count = 0
            errors = []
            
            for prompt_id, prompt_data in data.items():
                try:
                    # Validate prompt data
                    is_valid, error_msg = validate_prompt(prompt_data)
                    if not is_valid:
                        errors.append(f"Prompt {prompt_id}: {error_msg}")
                        continue
                    
                    # Add metadata if not present
                    from datetime import datetime
                    if 'CREATED_AT' not in prompt_data:
                        prompt_data['CREATED_AT'] = datetime.now().isoformat()
                    prompt_data['UPDATED_AT'] = datetime.now().isoformat()
                    
                    prompts[prompt_id] = prompt_data
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Prompt {prompt_id}: {str(e)}")
            
            if save_prompts(prompts):
                return jsonify({
                    'success': True,
                    'imported_count': imported_count,
                    'errors': errors,
                    'message': f'Successfully imported {imported_count} prompts'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to save imported prompts'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/prompts/export', methods=['GET'])
    def api_prompts_export():
        """Export all prompts as JSON"""
        try:
            from src.routes.prompts_routes import load_prompts
            from datetime import datetime
            prompts = load_prompts()
            return jsonify({
                'success': True,
                'prompts': prompts,
                'export_timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/prompts/<prompt_id>/test', methods=['POST'])
    def api_prompts_test(prompt_id):
        """Test a prompt with an image"""
        try:
            from src.routes.prompts_routes import load_prompts, generate_simulated_response
            prompts = load_prompts()
            
            if prompt_id not in prompts:
                return jsonify({
                    'success': False,
                    'error': 'Prompt not found'
                }), 404
            
            prompt = prompts[prompt_id]
            
            # Check if image file was uploaded
            if 'image' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No image file provided'
                }), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No image file selected'
                }), 400
            
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
            if not ('.' in file.filename and 
                    file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP, WEBP'
                }), 400
            
            # For now, just return a simulated response
            # In a real implementation, you would process the image with CLIP and LLM
            import time
            time.sleep(1)  # Simulate processing time
            
            simulated_response = generate_simulated_response(prompt)
            
            return jsonify({
                'success': True,
                'prompt_id': prompt_id,
                'prompt_title': prompt['TITLE'],
                'test_image': file.filename,
                'response': simulated_response,
                'processing_time': 1.0,
                'timestamp': datetime.now().isoformat()
            })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/prompts/stats', methods=['GET'])
    def api_prompts_stats():
        """Get statistics about prompts"""
        try:
            from src.routes.prompts_routes import load_prompts
            from datetime import datetime
            prompts = load_prompts()
            
            stats = {
                'total_prompts': len(prompts),
                'categories': {},
                'avg_temperature': 0,
                'avg_max_tokens': 0,
                'recent_updates': []
            }
            
            total_temp = 0
            total_tokens = 0
            
            for prompt_id, prompt in prompts.items():
                # Category stats
                category = prompt.get('CATEGORY', 'unknown')
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
                
                # Temperature and tokens
                total_temp += prompt.get('TEMPERATURE', 0)
                total_tokens += prompt.get('MAX_TOKENS', 0)
                
                # Recent updates
                updated_at = prompt.get('UPDATED_AT')
                if updated_at:
                    stats['recent_updates'].append({
                        'prompt_id': prompt_id,
                        'title': prompt.get('TITLE', ''),
                        'updated_at': updated_at
                    })
            
            if prompts:
                stats['avg_temperature'] = round(total_temp / len(prompts), 2)
                stats['avg_max_tokens'] = round(total_tokens / len(prompts))
            
            # Sort recent updates by date
            stats['recent_updates'].sort(key=lambda x: x['updated_at'], reverse=True)
            stats['recent_updates'] = stats['recent_updates'][:10]  # Top 10
            
            return jsonify({
                'success': True,
                'stats': stats
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500 