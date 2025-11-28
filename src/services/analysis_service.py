"""
Analysis Service - Handles analysis file operations and data processing
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from PIL import Image, UnidentifiedImageError
import io
import base64
from src.utils.logger import get_global_logger

logger = get_global_logger()


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
                            
                            # Build full path - handle both relative and absolute paths
                            if os.path.isabs(original_path):
                                full_image_path = os.path.join(original_path, original_image)
                            else:
                                # Try relative to upload folder first, then as absolute
                                full_image_path = os.path.join(self.upload_folder, original_path, original_image)
                                if not os.path.exists(full_image_path):
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
                    except (OSError, IOError, FileNotFoundError) as e:
                        logger.warning(f"Failed to load analysis file {file} (file error): {e}")
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.warning(f"Failed to load analysis file {file} (JSON error): {e}")
                    except Exception as e:
                        logger.warning(f"Failed to load analysis file {file} (unexpected error): {e}")
        return sorted(analysis_files, key=lambda x: x['date_processed'], reverse=True)
    
    def get_analysis_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get analysis data for a specific file"""
        file_path = os.path.join(self.output_folder, filename)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (OSError, IOError, FileNotFoundError) as e:
            logger.warning(f"Failed to load analysis data for {filename} (file error): {e}")
            return None
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to load analysis data for {filename} (JSON error): {e}")
            return None
        except Exception as e:
            logger.warning(f"Failed to load analysis data for {filename} (unexpected error): {e}")
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
        # Validate file exists and is not empty
        if not os.path.exists(image_path):
            logger.debug(f"Thumbnail skipped: file does not exist: {image_path}")
            return None
        
        # Check file size (images should be at least 100 bytes)
        try:
            file_size = os.path.getsize(image_path)
            if file_size < 100:
                logger.debug(f"Thumbnail skipped: file too small ({file_size} bytes): {image_path}")
                return None
        except OSError as e:
            logger.debug(f"Thumbnail skipped: cannot access file: {image_path}: {e}")
            return None
        
        try:
            with Image.open(image_path) as img:
                # Verify it's actually an image
                img.verify()
            
            # Reopen for processing (verify() closes the image)
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
        except (FileNotFoundError, OSError) as e:
            logger.debug(f"Thumbnail skipped: file error for {image_path}: {e}")
            return None
        except UnidentifiedImageError as e:
            logger.debug(f"Thumbnail skipped: not a valid image file {image_path}: {e}")
            return None
        except (ValueError, TypeError) as e:
            logger.debug(f"Thumbnail skipped: image processing error for {image_path}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error creating thumbnail for {image_path}: {e}")
            return None
    
    def _get_thumbnail_data_url(self, image_path: str) -> Optional[str]:
        """Get thumbnail as data URL"""
        thumbnail_data = self._create_thumbnail(image_path)
        if thumbnail_data:
            return f"data:image/jpeg;base64,{thumbnail_data}"
        return None 