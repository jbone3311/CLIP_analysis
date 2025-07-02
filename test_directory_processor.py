import pytest
import os
import json
import subprocess
from unittest.mock import patch, Mock, MagicMock
from directory_processor import DirectoryProcessor
from config import Config

class TestDirectoryProcessorInitialization:
    """Test cases for DirectoryProcessor initialization."""
    
    @patch.dict(os.environ, {
        'IMAGE_DIRECTORY': 'test_images',
        'USE_DATABASE': 'false',
        'USE_JSON': 'true'
    })
    def test_init_without_database(self):
        """Test DirectoryProcessor initialization without database."""
        config = Config()
        processor = DirectoryProcessor(config)
        
        assert processor.config == config
        assert processor.db is None
        
        processor.close()
    
    @patch.dict(os.environ, {
        'IMAGE_DIRECTORY': 'test_images',
        'USE_DATABASE': 'true',
        'DATABASE_PATH': 'test.db'
    })
    @patch('directory_processor.Database')
    def test_init_with_database(self, mock_database_class):
        """Test DirectoryProcessor initialization with database."""
        config = Config()
        processor = DirectoryProcessor(config)
        
        assert processor.config == config
        mock_database_class.assert_called_once_with(config.database_path)
        assert processor.db is not None
        
        processor.close()

class TestImageFileDiscovery:
    """Test cases for image file discovery and filtering."""
    
    @patch.dict(os.environ, {'USE_DATABASE': 'false', 'USE_JSON': 'false'})
    @patch('os.walk')
    def test_process_directory_finds_images(self, mock_walk, multiple_test_images):
        """Test that process_directory finds image files correctly."""
        # Mock os.walk to return test images
        mock_walk.return_value = [
            ('/test/dir', [], ['image1.jpg', 'image2.png', 'document.txt', 'image3.jpeg'])
        ]
        
        config = Config()
        config.image_directory = '/test/dir'
        
        with patch('os.path.join', side_effect=lambda *args: '/'.join(args)), \
             patch('os.path.isfile', return_value=True), \
             patch('os.path.splitext', side_effect=lambda x: (x.rsplit('.', 1)[0], '.' + x.rsplit('.', 1)[1])), \
             patch('os.getctime', return_value=1699999999.0), \
             patch('os.getsize', return_value=1024), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_subprocess.return_value.stdout = '{"test": "output"}'
            mock_subprocess.return_value.stderr = ''
            mock_subprocess.return_value.returncode = 0
            
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should process 3 image files (jpg, png, jpeg) but not txt
            # Verify subprocess was called for image processing
            assert mock_subprocess.call_count >= 3  # At least one call per image
            processor.close()

class TestJSONProcessing:
    """Test cases for JSON-based duplicate detection and processing."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'false',
        'USE_JSON': 'true',
        'ENABLE_CLIP_ANALYSIS': 'true',
        'ENABLE_LLM_ANALYSIS': 'false'
    })
    def test_skip_already_processed_json(self, temp_dir, sample_image_path):
        """Test that already processed images (with JSON) are skipped."""
        config = Config()
        config.image_directory = temp_dir
        
        # Create a JSON file for the image
        json_path = os.path.splitext(sample_image_path)[0] + '.json'
        with open(json_path, 'w') as f:
            json.dump({"already": "processed"}, f)
        
        with patch('subprocess.run') as mock_subprocess:
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should not call subprocess since image is already processed
            mock_subprocess.assert_not_called()
            processor.close()
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'false',
        'USE_JSON': 'true',
        'ENABLE_CLIP_ANALYSIS': 'true'
    })
    def test_process_new_image_json(self, temp_dir, sample_image_path):
        """Test processing new image without existing JSON."""
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.stdout = '{"test": "output"}'
            mock_subprocess.return_value.stderr = ''
            mock_subprocess.return_value.returncode = 0
            
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should call subprocess to process the image
            mock_subprocess.assert_called()
            processor.close()

class TestDatabaseProcessing:
    """Test cases for database-based duplicate detection and processing."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'true',
        'USE_JSON': 'false'
    })
    @patch('directory_processor.Database')
    def test_skip_already_processed_database(self, mock_database_class, temp_dir, sample_image_path):
        """Test skipping already processed images in database."""
        # Mock database to return that image is already processed
        mock_db = Mock()
        mock_db.is_processed_db.return_value = True
        mock_database_class.return_value = mock_db
        
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should not process since image is already in database
            mock_subprocess.assert_not_called()
            processor.close()
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'true',
        'USE_JSON': 'false'
    })
    @patch('directory_processor.Database')
    def test_process_new_image_database(self, mock_database_class, temp_dir, sample_image_path):
        """Test processing new image not in database."""
        # Mock database to return that image is not processed
        mock_db = Mock()
        mock_db.is_processed_db.return_value = False
        mock_db.get_image_id_db.return_value = 1
        mock_database_class.return_value = mock_db
        
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.stdout = '{"test": "output"}'
            mock_subprocess.return_value.stderr = ''
            mock_subprocess.return_value.returncode = 0
            
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should add image to database and process it
            mock_db.add_image.assert_called()
            mock_db.update_image_status.assert_called()
            mock_subprocess.assert_called()
            processor.close()

class TestSubprocessExecution:
    """Test cases for subprocess execution and command building."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'false',
        'USE_JSON': 'false',
        'ENABLE_CLIP_ANALYSIS': 'true',
        'ENABLE_CAPTION': 'true',
        'ENABLE_BEST': 'true',
        'ENABLE_FAST': 'false',
        'ENABLE_CLASSIC': 'false',
        'ENABLE_NEGATIVE': 'false'
    })
    def test_clip_command_construction(self, temp_dir, sample_image_path):
        """Test that CLIP analysis commands are constructed correctly."""
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.stdout = '{"test": "output"}'
            mock_subprocess.return_value.stderr = ''
            mock_subprocess.return_value.returncode = 0
            
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Verify subprocess was called with correct command
            mock_subprocess.assert_called()
            call_args = mock_subprocess.call_args[0][0]
            
            assert 'python' in call_args
            assert 'analysis_interrogate.py' in call_args
            assert sample_image_path in call_args
            processor.close()
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'false',
        'USE_JSON': 'false',
        'ENABLE_LLM_ANALYSIS': 'true',
        'LLM_1_TITLE': 'Test Model'
    })
    def test_llm_command_construction(self, temp_dir, sample_image_path):
        """Test that LLM analysis commands are constructed correctly."""
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.stdout = '{"test": "output"}'
            mock_subprocess.return_value.stderr = ''
            mock_subprocess.return_value.returncode = 0
            
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should call subprocess for both CLIP and LLM
            assert mock_subprocess.call_count >= 2
            
            # Check that LLM command was called
            calls = mock_subprocess.call_args_list
            llm_call = None
            for call in calls:
                if 'analysis_LLM.py' in str(call):
                    llm_call = call
                    break
            
            assert llm_call is not None
            processor.close()

class TestErrorHandling:
    """Test cases for error handling during processing."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'false',
        'USE_JSON': 'false'
    })
    def test_subprocess_error_handling(self, temp_dir, sample_image_path):
        """Test handling of subprocess errors."""
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            # Mock subprocess to raise CalledProcessError
            mock_subprocess.side_effect = subprocess.CalledProcessError(
                1, ['python', 'analysis_interrogate.py'], stderr='Error message'
            )
            
            processor = DirectoryProcessor(config)
            # Should not crash, just log error and continue
            processor.process_directory()
            processor.close()
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'true',
        'USE_JSON': 'false'
    })
    @patch('directory_processor.Database')
    def test_database_error_handling(self, mock_database_class, temp_dir, sample_image_path):
        """Test handling of database errors."""
        # Mock database to raise an exception
        mock_db = Mock()
        mock_db.add_image.side_effect = Exception("Database error")
        mock_database_class.return_value = mock_db
        
        config = Config()
        config.image_directory = temp_dir
        
        processor = DirectoryProcessor(config)
        # Should handle database errors gracefully
        processor.process_directory()
        processor.close()
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'false',
        'USE_JSON': 'false'
    })
    def test_file_access_error_handling(self, temp_dir):
        """Test handling of file access errors."""
        config = Config()
        config.image_directory = '/nonexistent/directory'
        
        processor = DirectoryProcessor(config)
        # Should handle directory not found gracefully
        processor.process_directory()
        processor.close()

class TestStatusTracking:
    """Test cases for processing status tracking."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'true',
        'USE_JSON': 'false'
    })
    @patch('directory_processor.Database')
    def test_status_updates_success(self, mock_database_class, temp_dir, sample_image_path):
        """Test that status is updated correctly for successful processing."""
        mock_db = Mock()
        mock_db.is_processed_db.return_value = False
        mock_db.get_image_id_db.return_value = 1
        mock_database_class.return_value = mock_db
        
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.stdout = '{"test": "output"}'
            mock_subprocess.return_value.stderr = ''
            mock_subprocess.return_value.returncode = 0
            
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should update status to processing and then completed
            status_calls = [call[0][1] for call in mock_db.update_image_status.call_args_list]
            assert 'processing' in status_calls
            assert 'completed' in status_calls
            processor.close()
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'true',
        'USE_JSON': 'false'
    })
    @patch('directory_processor.Database')
    def test_status_updates_failure(self, mock_database_class, temp_dir, sample_image_path):
        """Test that status is updated correctly for failed processing."""
        mock_db = Mock()
        mock_db.is_processed_db.return_value = False
        mock_db.get_image_id_db.return_value = 1
        mock_database_class.return_value = mock_db
        
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.side_effect = subprocess.CalledProcessError(
                1, ['python', 'analysis_interrogate.py'], stderr='Error'
            )
            
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should update status to failed
            status_calls = [call[0][1] for call in mock_db.update_image_status.call_args_list]
            assert 'failed' in status_calls
            processor.close()

class TestConfigurationOptions:
    """Test cases for different configuration combinations."""
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'false',
        'USE_JSON': 'true',
        'ENABLE_CLIP_ANALYSIS': 'false',
        'ENABLE_LLM_ANALYSIS': 'false'
    })
    def test_no_analysis_enabled(self, temp_dir, sample_image_path):
        """Test behavior when no analysis types are enabled."""
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should not call any analysis if none are enabled
            mock_subprocess.assert_not_called()
            processor.close()
    
    @patch.dict(os.environ, {
        'USE_DATABASE': 'true',
        'USE_JSON': 'true'
    })
    @patch('directory_processor.Database')
    def test_dual_storage_mode(self, mock_database_class, temp_dir, sample_image_path):
        """Test using both database and JSON storage."""
        mock_db = Mock()
        mock_db.is_processed_db.return_value = False
        mock_db.get_image_id_db.return_value = 1
        mock_database_class.return_value = mock_db
        
        config = Config()
        config.image_directory = temp_dir
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.stdout = '{"test": "output"}'
            mock_subprocess.return_value.stderr = ''
            mock_subprocess.return_value.returncode = 0
            
            processor = DirectoryProcessor(config)
            processor.process_directory()
            
            # Should use both storage methods
            mock_db.add_image.assert_called()
            # JSON file should be created (tested indirectly through no early exit)
            processor.close()

class TestCleanup:
    """Test cases for resource cleanup."""
    
    @patch.dict(os.environ, {'USE_DATABASE': 'true'})
    @patch('directory_processor.Database')
    def test_close_database_connection(self, mock_database_class):
        """Test that database connection is closed properly."""
        mock_db = Mock()
        mock_database_class.return_value = mock_db
        
        config = Config()
        processor = DirectoryProcessor(config)
        processor.close()
        
        # Should close database connection
        mock_db.close.assert_called_once()
    
    @patch.dict(os.environ, {'USE_DATABASE': 'false'})
    def test_close_without_database(self):
        """Test closing processor without database."""
        config = Config()
        processor = DirectoryProcessor(config)
        
        # Should not crash when closing without database
        processor.close()

class TestDirectoryTraversal:
    """Test cases for directory traversal functionality."""
    
    @patch.dict(os.environ, {'USE_DATABASE': 'false', 'USE_JSON': 'false'})
    def test_recursive_directory_processing(self, temp_dir):
        """Test that subdirectories are processed recursively."""
        # Create nested directory structure with images
        subdir = os.path.join(temp_dir, 'subdir')
        os.makedirs(subdir)
        
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                (temp_dir, ['subdir'], ['image1.jpg']),
                (subdir, [], ['image2.png', 'image3.jpeg'])
            ]
            
            config = Config()
            config.image_directory = temp_dir
            
            with patch('subprocess.run') as mock_subprocess, \
                 patch('os.path.isfile', return_value=True), \
                 patch('os.getctime', return_value=1699999999.0), \
                 patch('os.getsize', return_value=1024):
                
                mock_subprocess.return_value.stdout = '{"test": "output"}'
                mock_subprocess.return_value.stderr = ''
                mock_subprocess.return_value.returncode = 0
                
                processor = DirectoryProcessor(config)
                processor.process_directory()
                
                # Should process images from both directories
                assert mock_subprocess.call_count >= 3  # 3 images total
                processor.close()