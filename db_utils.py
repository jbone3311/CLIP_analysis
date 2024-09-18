# db_utils.py

import sqlite3
import logging
from typing import Optional, List, Tuple

class Database:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unique_id TEXT UNIQUE,
                filename TEXT,
                date_created TIMESTAMP,
                file_size INTEGER,
                status TEXT,
                last_processed TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER,
                analyzer TEXT,
                prompt_id TEXT,
                result TEXT,
                FOREIGN KEY (image_id) REFERENCES images(id)
            )
        ''')
        self.conn.commit()

    def add_image(self, unique_id: str, filename: str, date_created: float, file_size: int):
        try:
            self.cursor.execute('''
                INSERT INTO images (unique_id, filename, date_created, file_size, status, last_processed)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (unique_id, filename, date_created, file_size, 'pending', None))
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.info(f"Image {filename} already exists in the database.")

    def get_pending_images(self) -> List[Tuple[int, str, str]]:
        self.cursor.execute('''
            SELECT id, unique_id, filename FROM images WHERE status != 'completed'
        ''')
        return self.cursor.fetchall()

    def update_image_status(self, image_id: int, status: str):
        self.cursor.execute('''
            UPDATE images SET status = ?, last_processed = CURRENT_TIMESTAMP WHERE id = ?
        ''', (status, image_id))
        self.conn.commit()

    def add_analysis_result(self, image_id: int, analyzer: str, prompt_id: Optional[str], result: str):
        self.cursor.execute('''
            INSERT INTO analysis_results (image_id, analyzer, prompt_id, result)
            VALUES (?, ?, ?, ?)
        ''', (image_id, analyzer, prompt_id, result))
        self.conn.commit()

    def is_processed_db(self, unique_id: str) -> bool:
        self.cursor.execute('SELECT status FROM images WHERE unique_id = ?', (unique_id,))
        result = self.cursor.fetchone()
        return result is not None and result[0] == 'completed'

    def get_image_id_db(self, unique_id: str) -> Optional[int]:
        self.cursor.execute('SELECT id FROM images WHERE unique_id = ?', (unique_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.conn.close()
