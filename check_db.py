#!/usr/bin/env python3
"""Simple script to check database contents"""

import sqlite3
import json

def check_database():
    """Check what's in the database"""
    conn = sqlite3.connect('image_analysis.db')
    cursor = conn.cursor()
    
    print("=== Database Contents ===")
    
    # Check analysis_results table
    cursor.execute("SELECT * FROM analysis_results")
    rows = cursor.fetchall()
    
    print(f"\nFound {len(rows)} analysis results:")
    for i, row in enumerate(rows):
        print(f"\n--- Result {i+1} ---")
        print(f"ID: {row[0]}")
        print(f"Filename: {row[1]}")
        print(f"Directory: {row[2]}")
        print(f"MD5: {row[3]}")
        print(f"Model: {row[4]}")
        print(f"Modes: {row[5]}")
        print(f"Prompts: {row[6]}")
        
        # Try to parse JSON fields
        try:
            analysis = json.loads(row[7]) if row[7] else {}
            print(f"Analysis results keys: {list(analysis.keys()) if analysis else 'None'}")
            
            # Show CLIP results
            if 'clip' in analysis:
                clip_data = analysis['clip']
                print(f"CLIP results: {clip_data}")
            
            # Show LLM results
            if 'llm' in analysis:
                llm_data = analysis['llm']
                print(f"LLM results: {llm_data}")
                
        except Exception as e:
            print(f"Error parsing analysis results: {e}")
            print(f"Raw analysis results: {row[7][:200]}..." if row[7] else 'None')
            
        try:
            llm_results = json.loads(row[9]) if row[9] else {}
            print(f"LLM results keys: {list(llm_results.keys()) if llm_results else 'None'}")
            if llm_results:
                for model, result in llm_results.items():
                    print(f"  {model}: {result}")
        except Exception as e:
            print(f"Error parsing LLM results: {e}")
            print(f"Raw LLM results: {row[9][:200]}..." if row[9] else 'None')
    
    # Check llm_models table
    cursor.execute("SELECT * FROM llm_models WHERE is_active = 1")
    llm_rows = cursor.fetchall()
    
    print(f"\n=== LLM Models ({len(llm_rows)}) ===")
    for row in llm_rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Type: {row[2]}, URL: {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    check_database() 