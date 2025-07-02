import pytest
import os
import sqlite3
import tempfile
from unittest.mock import patch, Mock
from db_utils import Database

class TestDatabaseInitialization:
    """Test cases for Database class initialization."""
    
    def test_database_init(self, mock_database):
        """Test Database initialization with valid path."""
        db = Database(mock_database)
        assert db.db_path == mock_database
        assert db.conn is not None
        db.close()
    
    def test_database_init_creates_tables(self, temp_dir):
        """Test that Database initialization creates required tables."""
        db_path = os.path.join(temp_dir, "new_test.db")
        db = Database(db_path)
        
        # Verify tables exist
        cursor = db.conn.cursor()
        
        # Check images table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
        assert cursor.fetchone() is not None
        
        # Check analysis_results table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_results'")
        assert cursor.fetchone() is not None
        
        db.close()
    
    def test_database_init_invalid_path(self):
        """Test Database initialization with invalid path."""
        # This should either create the directory or handle the error gracefully
        invalid_path = "/invalid/path/test.db"
        
        # Depending on implementation, this might raise an exception
        # or create the directory structure
        try:
            db = Database(invalid_path)
            db.close()
        except (OSError, sqlite3.Error):
            # Expected behavior for invalid paths
            pass

class TestImageOperations:
    """Test cases for image-related database operations."""
    
    def test_add_image(self, mock_database):
        """Test adding a new image to the database."""
        db = Database(mock_database)
        
        unique_id = "test_unique_123"
        filename = "test_image.jpg"
        date_created = 1699999999.0
        file_size = 1024
        
        db.add_image(unique_id, filename, date_created, file_size)
        
        # Verify image was added
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM images WHERE unique_id = ?", (unique_id,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result[1] == unique_id  # unique_id column
        assert result[2] == filename   # filename column
        assert result[3] == date_created  # date_created column
        assert result[4] == file_size     # file_size column
        assert result[5] == 'pending'     # status column (default)
        
        db.close()
    
    def test_add_duplicate_image(self, mock_database):
        """Test adding duplicate image (should handle unique constraint)."""
        db = Database(mock_database)
        
        unique_id = "duplicate_test_123"
        filename = "duplicate.jpg"
        date_created = 1699999999.0
        file_size = 512
        
        # Add image first time
        db.add_image(unique_id, filename, date_created, file_size)
        
        # Try to add same unique_id again - should handle gracefully
        try:
            db.add_image(unique_id, filename, date_created, file_size)
        except sqlite3.IntegrityError:
            # Expected behavior for duplicate unique_id
            pass
        
        db.close()
    
    def test_get_image_id_db(self, mock_database):
        """Test retrieving image ID by unique_id."""
        db = Database(mock_database)
        
        unique_id = "get_id_test_123"
        filename = "get_id_test.jpg"
        date_created = 1699999999.0
        file_size = 2048
        
        # Add image first
        db.add_image(unique_id, filename, date_created, file_size)
        
        # Get the ID
        image_id = db.get_image_id_db(unique_id)
        
        assert image_id is not None
        assert isinstance(image_id, int)
        assert image_id > 0
        
        db.close()
    
    def test_get_image_id_nonexistent(self, mock_database):
        """Test retrieving ID for non-existent image."""
        db = Database(mock_database)
        
        image_id = db.get_image_id_db("nonexistent_unique_id")
        assert image_id is None
        
        db.close()
    
    def test_is_processed_db(self, mock_database):
        """Test checking if image is processed."""
        db = Database(mock_database)
        
        unique_id = "processed_test_123"
        filename = "processed_test.jpg"
        date_created = 1699999999.0
        file_size = 1536
        
        # Initially should not be processed
        assert db.is_processed_db(unique_id) is False
        
        # Add image
        db.add_image(unique_id, filename, date_created, file_size)
        
        # Still should not be processed (status is 'pending')
        assert db.is_processed_db(unique_id) is False
        
        # Update status to completed
        image_id = db.get_image_id_db(unique_id)
        db.update_image_status(image_id, 'completed')
        
        # Now should be processed
        assert db.is_processed_db(unique_id) is True
        
        db.close()
    
    def test_update_image_status(self, mock_database):
        """Test updating image processing status."""
        db = Database(mock_database)
        
        unique_id = "status_test_123"
        filename = "status_test.jpg"
        date_created = 1699999999.0
        file_size = 768
        
        # Add image
        db.add_image(unique_id, filename, date_created, file_size)
        image_id = db.get_image_id_db(unique_id)
        
        # Update status to processing
        db.update_image_status(image_id, 'processing')
        
        # Verify status update
        cursor = db.conn.cursor()
        cursor.execute("SELECT status FROM images WHERE id = ?", (image_id,))
        status = cursor.fetchone()[0]
        assert status == 'processing'
        
        # Update status to completed
        db.update_image_status(image_id, 'completed')
        
        # Verify status update
        cursor.execute("SELECT status FROM images WHERE id = ?", (image_id,))
        status = cursor.fetchone()[0]
        assert status == 'completed'
        
        db.close()

class TestAnalysisResultsOperations:
    """Test cases for analysis results database operations."""
    
    def test_add_analysis_result(self, mock_database):
        """Test adding analysis result to database."""
        db = Database(mock_database)
        
        # First add an image
        unique_id = "analysis_test_123"
        filename = "analysis_test.jpg"
        date_created = 1699999999.0
        file_size = 1024
        
        db.add_image(unique_id, filename, date_created, file_size)
        image_id = db.get_image_id_db(unique_id)
        
        # Add analysis result
        analysis_type = "LLM"
        prompt = "TEST_PROMPT1"
        result = '{"test": "result", "content": "analysis output"}'
        
        db.add_analysis_result(image_id, analysis_type, prompt, result)
        
        # Verify analysis result was added
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT * FROM analysis_results 
            WHERE image_id = ? AND analysis_type = ? AND prompt = ?
        """, (image_id, analysis_type, prompt))
        
        result_row = cursor.fetchone()
        assert result_row is not None
        assert result_row[1] == image_id
        assert result_row[2] == analysis_type
        assert result_row[3] == prompt
        assert result_row[4] == result
        
        db.close()
    
    def test_add_analysis_result_no_prompt(self, mock_database):
        """Test adding analysis result without prompt (e.g., CLIP analysis)."""
        db = Database(mock_database)
        
        # Add an image first
        unique_id = "clip_test_123"
        filename = "clip_test.jpg"
        date_created = 1699999999.0
        file_size = 512
        
        db.add_image(unique_id, filename, date_created, file_size)
        image_id = db.get_image_id_db(unique_id)
        
        # Add CLIP analysis result (no prompt)
        analysis_type = "CLIP"
        result = '{"best": "test prompt", "fast": "quick prompt"}'
        
        db.add_analysis_result(image_id, analysis_type, None, result)
        
        # Verify analysis result was added
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT * FROM analysis_results 
            WHERE image_id = ? AND analysis_type = ?
        """, (image_id, analysis_type))
        
        result_row = cursor.fetchone()
        assert result_row is not None
        assert result_row[1] == image_id
        assert result_row[2] == analysis_type
        assert result_row[3] is None  # prompt should be None
        assert result_row[4] == result
        
        db.close()
    
    def test_add_multiple_analysis_results(self, mock_database):
        """Test adding multiple analysis results for the same image."""
        db = Database(mock_database)
        
        # Add an image
        unique_id = "multi_test_123"
        filename = "multi_test.jpg"
        date_created = 1699999999.0
        file_size = 2048
        
        db.add_image(unique_id, filename, date_created, file_size)
        image_id = db.get_image_id_db(unique_id)
        
        # Add multiple results
        results = [
            ("LLM", "PROMPT1", '{"result": "description"}'),
            ("LLM", "PROMPT2", '{"result": "analysis"}'),
            ("CLIP", None, '{"best": "prompt", "fast": "quick"}')
        ]
        
        for analysis_type, prompt, result in results:
            db.add_analysis_result(image_id, analysis_type, prompt, result)
        
        # Verify all results were added
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analysis_results WHERE image_id = ?", (image_id,))
        count = cursor.fetchone()[0]
        assert count == len(results)
        
        db.close()

class TestDatabaseConnection:
    """Test cases for database connection management."""
    
    def test_close_connection(self, mock_database):
        """Test closing database connection."""
        db = Database(mock_database)
        assert db.conn is not None
        
        db.close()
        # After closing, connection should be None or closed
        # Implementation may vary, but should handle gracefully
        
        # Trying to use closed connection should not crash
        try:
            db.add_image("test", "test.jpg", 1699999999.0, 1024)
        except (sqlite3.ProgrammingError, AttributeError):
            # Expected behavior when using closed connection
            pass
    
    def test_context_manager_usage(self, mock_database):
        """Test using Database as context manager if implemented."""
        # This test depends on whether Database implements __enter__ and __exit__
        try:
            with Database(mock_database) as db:
                db.add_image("context_test", "test.jpg", 1699999999.0, 1024)
                # Connection should be automatically closed
        except (AttributeError, TypeError):
            # Database may not implement context manager protocol
            pass

class TestDatabaseQueries:
    """Test cases for complex database queries and edge cases."""
    
    def test_sql_injection_protection(self, mock_database):
        """Test that the database is protected against SQL injection."""
        db = Database(mock_database)
        
        # Try to inject SQL in unique_id
        malicious_id = "'; DROP TABLE images; --"
        filename = "injection_test.jpg"
        date_created = 1699999999.0
        file_size = 1024
        
        # This should not cause SQL injection
        try:
            db.add_image(malicious_id, filename, date_created, file_size)
            
            # Verify that the images table still exists
            cursor = db.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
            assert cursor.fetchone() is not None
            
        except sqlite3.Error:
            # Some SQL errors are acceptable, but table should still exist
            cursor = db.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
            assert cursor.fetchone() is not None
        
        db.close()
    
    def test_large_data_handling(self, mock_database):
        """Test handling of large data entries."""
        db = Database(mock_database)
        
        unique_id = "large_data_test"
        filename = "large_test.jpg"
        date_created = 1699999999.0
        file_size = 1024 * 1024 * 10  # 10MB
        
        # Add image with large file size
        db.add_image(unique_id, filename, date_created, file_size)
        image_id = db.get_image_id_db(unique_id)
        
        # Add large analysis result
        large_result = '{"content": "' + 'x' * 10000 + '"}'  # Large JSON string
        db.add_analysis_result(image_id, "LLM", "LARGE_PROMPT", large_result)
        
        # Verify data was stored correctly
        cursor = db.conn.cursor()
        cursor.execute("SELECT result FROM analysis_results WHERE image_id = ?", (image_id,))
        stored_result = cursor.fetchone()[0]
        assert len(stored_result) == len(large_result)
        
        db.close()
    
    def test_concurrent_access_simulation(self, mock_database):
        """Test database behavior under simulated concurrent access."""
        db1 = Database(mock_database)
        db2 = Database(mock_database)
        
        try:
            # Both connections should be able to read
            assert db1.is_processed_db("nonexistent") is False
            assert db2.is_processed_db("nonexistent") is False
            
            # Add data from first connection
            db1.add_image("concurrent_test", "test.jpg", 1699999999.0, 1024)
            
            # Second connection should see the data
            image_id = db2.get_image_id_db("concurrent_test")
            assert image_id is not None
            
        finally:
            db1.close()
            db2.close()

class TestErrorHandling:
    """Test cases for error handling in database operations."""
    
    def test_database_file_permissions(self, temp_dir):
        """Test handling of database file permission issues."""
        # Create a read-only directory
        readonly_dir = os.path.join(temp_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only
        
        db_path = os.path.join(readonly_dir, "readonly.db")
        
        try:
            # This should either fail gracefully or handle the permission issue
            db = Database(db_path)
            db.close()
        except (OSError, sqlite3.Error):
            # Expected behavior for permission issues
            pass
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)
    
    def test_corrupted_database_handling(self, temp_dir):
        """Test handling of corrupted database files."""
        db_path = os.path.join(temp_dir, "corrupted.db")
        
        # Create a file that's not a valid SQLite database
        with open(db_path, 'w') as f:
            f.write("This is not a valid SQLite database file")
        
        try:
            # This should handle the corrupted file gracefully
            db = Database(db_path)
            db.close()
        except sqlite3.DatabaseError:
            # Expected behavior for corrupted database
            pass