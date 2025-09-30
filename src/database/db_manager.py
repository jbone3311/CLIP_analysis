import sqlite3
import os
import json
from typing import Optional, Dict, Any, List
from src.utils.logger import get_global_logger
from src.utils.error_handler import handle_errors, ErrorCategory, error_context

logger = get_global_logger()

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'image_analysis.db')
        logger.info(f"Initializing database: {self.db_path}")
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    @handle_errors(category=ErrorCategory.DATABASE)
    def init_db(self):
        """Initialize the database with the required schema"""
        logger.debug("Creating database schema")
        with self.get_connection() as conn:
            # Create analysis_results table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    directory TEXT NOT NULL,
                    md5 TEXT NOT NULL,
                    model TEXT,
                    modes TEXT,
                    prompts TEXT,
                    analysis_results TEXT,
                    settings TEXT,
                    llm_results TEXT,
                    date_added TEXT,
                    UNIQUE(md5)
                )
            ''')
            
            # Create llm_models table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS llm_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    url TEXT,
                    api_key TEXT,
                    model_name TEXT,
                    prompts TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    date_added TEXT,
                    UNIQUE(name, type)
                )
            ''')
            conn.commit()
        logger.info("Database schema initialized successfully")

    @handle_errors(category=ErrorCategory.DATABASE)
    def insert_result(self, filename: str, directory: str, md5: str, model: str, 
                     modes: str, prompts: str, analysis_results: str, settings: str, llm_results: str = None):
        """Insert a new analysis result into the database"""
        logger.debug(f"Inserting result for file: {filename}", data={'md5': md5, 'model': model})
        with self.get_connection() as conn:
            conn.execute(
                '''INSERT OR REPLACE INTO analysis_results
                (filename, directory, md5, model, modes, prompts, analysis_results, settings, llm_results, date_added)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))''',
                (filename, directory, md5, model, modes, prompts, analysis_results, settings, llm_results)
            )
            conn.commit()
        logger.info(f"Successfully inserted result for: {filename}")

    def get_result_by_md5(self, md5: str) -> Optional[Dict[str, Any]]:
        """Get analysis result by MD5 hash"""
        with self.get_connection() as conn:
            cur = conn.execute('SELECT * FROM analysis_results WHERE md5 = ?', (md5,))
            row = cur.fetchone()
            if row:
                return self._row_to_dict(cur, row)
            return None

    def get_result_by_id(self, result_id: int) -> Optional[Dict[str, Any]]:
        """Get analysis result by ID"""
        with self.get_connection() as conn:
            cur = conn.execute('SELECT * FROM analysis_results WHERE id = ?', (result_id,))
            row = cur.fetchone()
            if row:
                return self._row_to_dict(cur, row)
            return None

    def get_result_by_filename(self, filename: str, directory: str) -> Optional[Dict[str, Any]]:
        """Get analysis result by filename and directory"""
        with self.get_connection() as conn:
            cur = conn.execute('SELECT * FROM analysis_results WHERE filename = ? AND directory = ?', 
                             (filename, directory))
            row = cur.fetchone()
            if row:
                return self._row_to_dict(cur, row)
            return None

    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all analysis results ordered by date added"""
        with self.get_connection() as conn:
            cur = conn.execute('SELECT * FROM analysis_results ORDER BY date_added DESC')
            rows = cur.fetchall()
            return [self._row_to_dict(cur, row) for row in rows]

    def _row_to_dict(self, cur, row) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        columns = [desc[0] for desc in cur.description]
        data = dict(zip(columns, row))
        
        # Parse JSON fields
        for key in ['modes', 'prompts', 'analysis_results', 'settings', 'llm_results']:
            if data.get(key):
                try:
                    data[key] = json.loads(data[key])
                except Exception:
                    pass
        return data

    def delete_result(self, result_id: int) -> bool:
        """Delete an analysis result by ID"""
        try:
            with self.get_connection() as conn:
                conn.execute('DELETE FROM analysis_results WHERE id = ?', (result_id,))
                conn.commit()
            return True
        except Exception:
            return False

    def clear_database(self) -> bool:
        """Clear all results from the database"""
        try:
            with self.get_connection() as conn:
                conn.execute('DELETE FROM analysis_results')
                conn.commit()
            return True
        except Exception:
            return False

    def insert_llm_model(self, name: str, type: str, url: str = None, api_key: str = None, model_name: str = None, prompts: str = None):
        """Insert a new LLM model configuration"""
        with self.get_connection() as conn:
            conn.execute(
                '''INSERT OR REPLACE INTO llm_models
                (name, type, url, api_key, model_name, prompts, is_active, date_added)
                VALUES (?, ?, ?, ?, ?, ?, 1, datetime('now'))''',
                (name, type, url, api_key, model_name, prompts)
            )
            conn.commit()

    def get_llm_models(self) -> List[Dict[str, Any]]:
        """Get all LLM model configurations"""
        with self.get_connection() as conn:
            cur = conn.execute('SELECT * FROM llm_models WHERE is_active = 1 ORDER BY name')
            rows = cur.fetchall()
            return [self._row_to_dict(cur, row) for row in rows]

    def delete_llm_model(self, model_id: int) -> bool:
        """Delete an LLM model configuration"""
        try:
            with self.get_connection() as conn:
                conn.execute('UPDATE llm_models SET is_active = 0 WHERE id = ?', (model_id,))
                conn.commit()
            return True
        except Exception:
            return False

    def update_llm_model_prompts(self, model_id: int, prompts: str) -> bool:
        """Update prompts for an LLM model"""
        try:
            with self.get_connection() as conn:
                conn.execute('UPDATE llm_models SET prompts = ? WHERE id = ?', (prompts, model_id))
                conn.commit()
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            total = conn.execute('SELECT COUNT(*) FROM analysis_results').fetchone()[0]
            recent = conn.execute('SELECT COUNT(*) FROM analysis_results WHERE date_added >= datetime("now", "-7 days")').fetchone()[0]
            llm_models = conn.execute('SELECT COUNT(*) FROM llm_models WHERE is_active = 1').fetchone()[0]
            return {
                'total_results': total,
                'recent_results': recent,
                'llm_models': llm_models
            } 