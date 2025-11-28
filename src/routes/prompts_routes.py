"""
Prompt Management API endpoints
Handles CRUD operations for prompts, import/export, and testing
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from ..utils.logger import get_logger

logger = get_logger(__name__)
prompts_bp = Blueprint('prompts', __name__)

# Configuration
PROMPTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src', 'config', 'prompts.json')

def load_prompts() -> Dict[str, Any]:
    """Load prompts from JSON file"""
    try:
        if os.path.exists(PROMPTS_FILE):
            with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Prompts file not found: {PROMPTS_FILE}")
            return {}
    except Exception as e:
        logger.error(f"Error loading prompts: {e}")
        return {}

def save_prompts(prompts: Dict[str, Any]) -> bool:
    """Save prompts to JSON file"""
    try:
        os.makedirs(os.path.dirname(PROMPTS_FILE), exist_ok=True)
        with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, indent=2, ensure_ascii=False)
        logger.info(f"Prompts saved to {PROMPTS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving prompts: {e}")
        return False

def validate_prompt(prompt_data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate prompt data"""
    required_fields = ['TITLE', 'PROMPT_TEXT', 'CATEGORY', 'TEMPERATURE', 'MAX_TOKENS']
    
    for field in required_fields:
        if field not in prompt_data:
            return False, f"Missing required field: {field}"
    
    if not prompt_data['TITLE'].strip():
        return False, "Title cannot be empty"
    
    if not prompt_data['PROMPT_TEXT'].strip():
        return False, "Prompt text cannot be empty"
    
    if not (0 <= prompt_data['TEMPERATURE'] <= 1):
        return False, "Temperature must be between 0 and 1"
    
    if not (100 <= prompt_data['MAX_TOKENS'] <= 8000):
        return False, "Max tokens must be between 100 and 8000"
    
    valid_categories = [
        'comprehensive', 'detection', 'color', 'artistic', 
        'generation', 'technical', 'psychological', 'database'
    ]
    
    if prompt_data['CATEGORY'] not in valid_categories:
        return False, f"Invalid category. Must be one of: {', '.join(valid_categories)}"
    
    return True, ""

@prompts_bp.route('/api/prompts', methods=['GET'])
def get_prompts():
    """Get all prompts"""
    try:
        prompts = load_prompts()
        return jsonify({
            'success': True,
            'prompts': prompts,
            'count': len(prompts)
        })
    except Exception as e:
        logger.error(f"Error getting prompts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prompts_bp.route('/api/prompts/<prompt_id>', methods=['GET'])
def get_prompt(prompt_id: str):
    """Get a specific prompt"""
    try:
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
        logger.error(f"Error getting prompt {prompt_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prompts_bp.route('/api/prompts', methods=['POST'])
def create_prompt():
    """Create a new prompt"""
    try:
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
        prompt_data['CREATED_AT'] = datetime.now().isoformat()
        prompt_data['UPDATED_AT'] = datetime.now().isoformat()
        
        prompts[prompt_id] = prompt_data
        
        if save_prompts(prompts):
            logger.info(f"Created prompt: {prompt_id}")
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
        logger.error(f"Error creating prompt: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prompts_bp.route('/api/prompts/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id: str):
    """Update an existing prompt"""
    try:
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
        prompt_data['UPDATED_AT'] = datetime.now().isoformat()
        prompt_data['CREATED_AT'] = prompts[prompt_id].get('CREATED_AT', datetime.now().isoformat())
        
        prompts[prompt_id] = prompt_data
        
        if save_prompts(prompts):
            logger.info(f"Updated prompt: {prompt_id}")
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
        logger.error(f"Error updating prompt {prompt_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prompts_bp.route('/api/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id: str):
    """Delete a prompt"""
    try:
        prompts = load_prompts()
        
        if prompt_id not in prompts:
            return jsonify({
                'success': False,
                'error': 'Prompt not found'
            }), 404
        
        deleted_prompt = prompts.pop(prompt_id)
        
        if save_prompts(prompts):
            logger.info(f"Deleted prompt: {prompt_id}")
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
        logger.error(f"Error deleting prompt {prompt_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prompts_bp.route('/api/prompts/import', methods=['POST'])
def import_prompts():
    """Import prompts from JSON data"""
    try:
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
                if 'CREATED_AT' not in prompt_data:
                    prompt_data['CREATED_AT'] = datetime.now().isoformat()
                prompt_data['UPDATED_AT'] = datetime.now().isoformat()
                
                prompts[prompt_id] = prompt_data
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Prompt {prompt_id}: {str(e)}")
        
        if save_prompts(prompts):
            logger.info(f"Imported {imported_count} prompts")
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
        logger.error(f"Error importing prompts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prompts_bp.route('/api/prompts/export', methods=['GET'])
def export_prompts():
    """Export all prompts as JSON"""
    try:
        prompts = load_prompts()
        return jsonify({
            'success': True,
            'prompts': prompts,
            'export_timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error exporting prompts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prompts_bp.route('/api/prompts/<prompt_id>/test', methods=['POST'])
def test_prompt(prompt_id: str):
    """Test a prompt with an image"""
    try:
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
        
        # Save uploaded file temporarily
        filename = secure_filename(f"test_{uuid.uuid4()}_{file.filename}")
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'temp')
        temp_path = os.path.join(temp_dir, filename)
        os.makedirs(temp_dir, exist_ok=True)
        file.save(temp_path)
        
        try:
            # Here you would integrate with your CLIP analysis and LLM processing
            # For now, we'll return a simulated response
            
            # Simulate processing time
            import time
            time.sleep(1)
            
            # Generate simulated response based on prompt category
            simulated_response = generate_simulated_response(prompt)
            
            return jsonify({
                'success': True,
                'prompt_id': prompt_id,
                'prompt_title': prompt['TITLE'],
                'test_image': filename,
                'response': simulated_response,
                'processing_time': 1.0,
                'timestamp': datetime.now().isoformat()
            })
            
        finally:
            # Clean up temporary file
            try:
                os.remove(temp_path)
            except (OSError, FileNotFoundError, PermissionError) as e:
                logger.warning(f"Failed to remove temporary file {temp_path}: {e}")
                
    except Exception as e:
        logger.error(f"Error testing prompt {prompt_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_simulated_response(prompt: Dict[str, Any]) -> str:
    """Generate a simulated response based on prompt category"""
    category = prompt.get('CATEGORY', 'comprehensive')
    
    responses = {
        'comprehensive': {
            'objects': [
                {'name': 'person', 'category': 'person', 'location': 'center', 'size': 'large', 'color': 'blue', 'details': 'wearing casual clothing'},
                {'name': 'chair', 'category': 'furniture', 'location': 'foreground', 'size': 'medium', 'color': 'brown', 'details': 'wooden chair'}
            ],
            'colors': [
                {'name': 'blue', 'hex': '#007bff', 'percentage': 30, 'description': 'dominant color'},
                {'name': 'brown', 'hex': '#8b4513', 'percentage': 25, 'description': 'furniture color'}
            ],
            'artistic_influences': ['realism', 'contemporary'],
            'general_analysis': 'A realistic portrait showing a person in casual attire sitting on a wooden chair.'
        },
        'detection': {
            'objects': [
                {'name': 'person', 'category': 'person', 'location': 'center', 'size': 'large', 'color': 'blue', 'details': 'wearing casual clothing', 'quantity': 1},
                {'name': 'chair', 'category': 'furniture', 'location': 'foreground', 'size': 'medium', 'color': 'brown', 'details': 'wooden chair', 'quantity': 1}
            ]
        },
        'color': {
            'colors': [
                {'name': 'blue', 'hex': '#007bff', 'percentage': 30, 'description': 'dominant color'},
                {'name': 'brown', 'hex': '#8b4513', 'percentage': 25, 'description': 'furniture color'}
            ],
            'theme': {
                'palette': 'earth tones with blue accent',
                'dominant_family': 'blue',
                'temperature': 'cool',
                'saturation': 'medium',
                'mood': 'calm and natural'
            }
        },
        'artistic': {
            'styles': ['realism', 'contemporary'],
            'artists': ['photographic realism'],
            'techniques': ['natural lighting', 'rule of thirds'],
            'period': 'contemporary',
            'cultural_influences': ['western portrait tradition']
        },
        'generation': 'A realistic portrait of a person in casual blue clothing sitting on a wooden chair, natural lighting, rule of thirds composition, high quality, detailed, photorealistic',
        'technical': {
            'quality': 'high resolution, sharp focus',
            'parameters': 'natural lighting, shallow depth of field',
            'composition': 'rule of thirds, balanced',
            'processing': 'minimal post-processing'
        },
        'psychological': {
            'emotions': ['calm', 'contemplative'],
            'mood': 'peaceful and natural',
            'symbolism': 'casual comfort',
            'impact': 'relaxing and approachable'
        },
        'database': {
            'categories': ['portrait', 'person', 'furniture'],
            'tags': ['person', 'chair', 'blue', 'brown', 'realism', 'portrait'],
            'classification': 'portrait photography',
            'keywords': ['person', 'chair', 'casual', 'realistic']
        }
    }
    
    return json.dumps(responses.get(category, {'message': 'Simulated response for testing'}), indent=2)

@prompts_bp.route('/api/prompts/stats', methods=['GET'])
def get_prompt_stats():
    """Get statistics about prompts"""
    try:
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
        logger.error(f"Error getting prompt stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 