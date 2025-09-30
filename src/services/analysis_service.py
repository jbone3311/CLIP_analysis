"""
Analysis Service - Handles analysis file operations and data processing
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from PIL import Image
import io
import base64


class AnalysisService:
    """Service for handling analysis file operations"""
    
    def __init__(self, output_folder: str, upload_folder: str):
        self.output_folder = output_folder
        self.upload_folder = upload_folder
    
    def get_analysis_files(self) -> List[Dict[str, Any]]:
        """Get list of analysis files with thumbnails"""
        analysis_files = []
        if os.path.exists(self.output_folder):
            for file in os.listdir(self.output_folder):
                if file.endswith('_analysis.json'):
                    file_path = os.path.join(self.output_folder, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                            # Try to find the original image and generate thumbnail
                            original_image = data.get('file_info', {}).get('filename', 'Unknown')
                            original_path = data.get('file_info', {}).get('directory', 'Images')
                            full_image_path = os.path.join(original_path, original_image)
                            
                            thumbnail_url = None
                            if os.path.exists(full_image_path):
                                thumbnail_url = self._get_thumbnail_data_url(full_image_path)
                            
                            analysis_files.append({
                                'filename': file,
                                'original_image': original_image,
                                'status': data.get('processing_info', {}).get('status', 'unknown'),
                                'processing_time': data.get('processing_info', {}).get('processing_time', 0),
                                'date_processed': data.get('file_info', {}).get('date_processed', ''),
                                'file_size': data.get('file_info', {}).get('file_size', 0),
                                'has_clip': bool(data.get('analysis', {}).get('clip')),
                                'has_llm': bool(data.get('analysis', {}).get('llm')),
                                'has_metadata': bool(data.get('analysis', {}).get('metadata')),
                                'thumbnail': thumbnail_url
                            })
                    except Exception as e:
                        print(f"Error loading {file}: {e}")
        return sorted(analysis_files, key=lambda x: x['date_processed'], reverse=True)
    
    def get_analysis_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get analysis data for a specific file"""
        file_path = os.path.join(self.output_folder, filename)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading analysis data for {filename}: {e}")
            return None
    
    def get_analysis_stats(self) -> Dict[str, int]:
        """Get analysis statistics"""
        analysis_files = self.get_analysis_files()
        total_analyses = len(analysis_files)
        completed_analyses = len([f for f in analysis_files if f['status'] == 'complete'])
        
        return {
            'total_analyses': total_analyses,
            'completed_analyses': completed_analyses,
            'pending_analyses': total_analyses - completed_analyses
        }
    
    def _create_thumbnail(self, image_path: str, size: tuple = (200, 200)) -> Optional[str]:
        """Create a thumbnail for an image"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Convert to base64 for inline display
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)
                
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error creating thumbnail for {image_path}: {e}")
            return None
    
    def _get_thumbnail_data_url(self, image_path: str) -> Optional[str]:
        """Get thumbnail as data URL"""
        thumbnail_data = self._create_thumbnail(image_path)
        if thumbnail_data:
            return f"data:image/jpeg;base64,{thumbnail_data}"
        return None 