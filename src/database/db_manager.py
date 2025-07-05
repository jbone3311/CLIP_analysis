import sqlite3
import os
import json
from typing import Optional, Dict, Any, List

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'image_analysis.db')
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize the database with the required schema"""
        schema = '''
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
            date_added TEXT,
            UNIQUE(md5)
        );
        '''
        
        with self.get_connection() as conn:
            conn.execute(schema)
            conn.commit()

    def insert_result(self, filename: str, directory: str, md5: str, model: str, 
                     modes: str, prompts: str, analysis_results: str, settings: str):
        """Insert a new analysis result into the database"""
        with self.get_connection() as conn:
            conn.execute(
                '''INSERT OR REPLACE INTO analysis_results
                (filename, directory, md5, model, modes, prompts, analysis_results, settings, date_added)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))''',
                (filename, directory, md5, model, modes, prompts, analysis_results, settings)
            )
            conn.commit()

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
        for key in ['modes', 'prompts', 'analysis_results', 'settings']:
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

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            total = conn.execute('SELECT COUNT(*) FROM analysis_results').fetchone()[0]
            recent = conn.execute('SELECT COUNT(*) FROM analysis_results WHERE date_added >= datetime("now", "-7 days")').fetchone()[0]
            return {
                'total_results': total,
                'recent_results': recent
            } 