"""
Image Service - Handles image file operations and uploads
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
import io
import base64
from src.utils.logger import get_global_logger

logger = get_global_logger()


class ImageService:
    """Service for handling image file operations"""
    
    def __init__(self, upload_folder: str, allowed_extensions: set):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions
    
    def get_image_files(self) -> List[Dict[str, Any]]:
        """Get list of uploaded images with thumbnails"""
        image_files = []
        if os.path.exists(self.upload_folder):
            for root, dirs, files in os.walk(self.upload_folder):
                for file in files:
                    if self._allowed_file(file):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, self.upload_folder)
                        
                        # Generate thumbnail
                        thumbnail_url = self._get_thumbnail_data_url(file_path)
                        
                        image_files.append({
                            'filename': file,
                            'path': rel_path,
                            'full_path': file_path,
                            'size': os.path.getsize(file_path),
                            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                            'thumbnail': thumbnail_url
                        })
        return sorted(image_files, key=lambda x: x['modified'], reverse=True)
    
    def save_uploaded_file(self, file) -> Optional[str]:
        """Save an uploaded file"""
        if file and file.filename:
            filename = secure_filename(file.filename)
            if filename and self._allowed_file(filename):
                file_path = os.path.join(self.upload_folder, filename)
                file.save(file_path)
                return filename
        return None
    
    def get_image_stats(self) -> Dict[str, int]:
        """Get image statistics"""
        image_files = self.get_image_files()
        total_images = len(image_files)
        total_size = sum(img['size'] for img in image_files)
        
        return {
            'total_images': total_images,
            'total_size': total_size,
            'average_size': total_size // total_images if total_images > 0 else 0
        }
    
    def _allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
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