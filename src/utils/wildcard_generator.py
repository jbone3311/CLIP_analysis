"""
Wildcard Generator for CLIP Analysis Results

This module generates wildcard files based on analysis results, organized by subfolder groups.
Wildcard files are named after the directory they represent and contain all the prompts
from images in that directory.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WildcardGenerator:
    """Generates wildcard files from CLIP analysis results"""
    
    def __init__(self, output_directory: str = "Output"):
        self.output_directory = output_directory
        self.wildcards_dir = os.path.join(output_directory, "wildcards")
        os.makedirs(self.wildcards_dir, exist_ok=True)
    
    def extract_group_from_path(self, file_path: str, base_directory: str) -> str:
        """
        Extract group name from file path based on subfolder structure.
        
        Args:
            file_path: Full path to the image file
            base_directory: Base directory containing the images
            
        Returns:
            Group name (subfolder name or 'root' if in base directory)
        """
        try:
            # Get relative path from base directory
            rel_path = os.path.relpath(file_path, base_directory)
            
            # Split path into components
            path_parts = Path(rel_path).parts
            
            # If file is directly in base directory, use 'root'
            if len(path_parts) == 1:
                return 'root'
            
            # Return the first subfolder name as the group
            return path_parts[0]
            
        except Exception as e:
            logger.warning(f"Could not extract group from {file_path}: {e}")
            return 'unknown'
    
    def extract_prompts_from_result(self, result: Dict[str, Any]) -> List[str]:
        """
        Extract all prompts from a CLIP analysis result.
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            List of extracted prompts
        """
        prompts = []
        
        try:
            # Handle different result structures
            if isinstance(result, dict):
                # Check for analysis_results
                if 'analysis_results' in result:
                    analysis_data = result['analysis_results']
                    if isinstance(analysis_data, str):
                        try:
                            analysis_data = json.loads(analysis_data)
                        except:
                            analysis_data = {}
                    
                    # Extract prompts from different modes
                    for mode, mode_data in analysis_data.items():
                        if isinstance(mode_data, dict):
                            # Look for prompt field
                            if 'prompt' in mode_data:
                                prompt = mode_data['prompt']
                                if prompt and isinstance(prompt, str):
                                    prompts.append(prompt.strip())
                            
                            # Look for prompts field (array)
                            elif 'prompts' in mode_data:
                                mode_prompts = mode_data['prompts']
                                if isinstance(mode_prompts, list):
                                    for p in mode_prompts:
                                        if isinstance(p, str) and p.strip():
                                            prompts.append(p.strip())
                
                # Check for llm_results
                if 'llm_results' in result:
                    llm_data = result['llm_results']
                    if isinstance(llm_data, str):
                        try:
                            llm_data = json.loads(llm_data)
                        except:
                            llm_data = {}
                    
                    if isinstance(llm_data, dict):
                        for prompt_id, prompt_data in llm_data.items():
                            if isinstance(prompt_data, dict) and 'content' in prompt_data:
                                content = prompt_data['content']
                                if content and isinstance(content, str):
                                    prompts.append(content.strip())
            
            # Remove duplicates while preserving order
            seen = set()
            unique_prompts = []
            for prompt in prompts:
                if prompt not in seen:
                    seen.add(prompt)
                    unique_prompts.append(prompt)
            
            return unique_prompts
            
        except Exception as e:
            logger.warning(f"Could not extract prompts from result: {e}")
            return []
    
    def create_wildcard_content(self, prompts: List[str], group_name: str) -> str:
        """
        Create wildcard file content from prompts.
        
        Args:
            prompts: List of prompts to include
            group_name: Name of the group/directory
            
        Returns:
            Formatted wildcard content
        """
        if not prompts:
            return f"# {group_name} - No prompts found\n"
        
        content = f"# {group_name} Wildcard File\n"
        content += f"# Generated from {len(prompts)} images\n"
        content += f"# Group: {group_name}\n\n"
        
        for i, prompt in enumerate(prompts, 1):
            # Clean up the prompt
            clean_prompt = prompt.strip()
            if clean_prompt:
                # Remove any existing wildcard formatting
                clean_prompt = re.sub(r'\{[^}]*\}', '', clean_prompt)
                clean_prompt = re.sub(r'\[[^\]]*\]', '', clean_prompt)
                clean_prompt = clean_prompt.strip()
                
                if clean_prompt:
                    content += f"{clean_prompt}\n"
        
        return content
    
    def generate_wildcards_from_results(self, results: List[Dict[str, Any]], base_directory: str) -> Dict[str, str]:
        """
        Generate wildcard files from analysis results.
        
        Args:
            results: List of analysis result dictionaries
            base_directory: Base directory containing the images
            
        Returns:
            Dictionary mapping group names to wildcard file paths
        """
        # Group results by directory
        grouped_results = defaultdict(list)
        
        for result in results:
            try:
                # Get file path from result
                filename = result.get('filename', '')
                directory = result.get('directory', '')
                
                if filename and directory:
                    # Construct full file path
                    file_path = os.path.join(directory, filename)
                    
                    # Extract group from path
                    group = self.extract_group_from_path(file_path, base_directory)
                    
                    # Add to grouped results
                    grouped_results[group].append(result)
                    
            except Exception as e:
                logger.warning(f"Could not process result: {e}")
                continue
        
        # Generate wildcard files for each group
        wildcard_files = {}
        
        for group_name, group_results in grouped_results.items():
            try:
                # Extract all prompts from this group
                all_prompts = []
                for result in group_results:
                    prompts = self.extract_prompts_from_result(result)
                    all_prompts.extend(prompts)
                
                # Create wildcard content
                wildcard_content = self.create_wildcard_content(all_prompts, group_name)
                
                # Create filename (sanitize group name)
                safe_group_name = re.sub(r'[^\w\-_]', '_', group_name)
                wildcard_filename = f"{safe_group_name}.txt"
                wildcard_path = os.path.join(self.wildcards_dir, wildcard_filename)
                
                # Write wildcard file
                with open(wildcard_path, 'w', encoding='utf-8') as f:
                    f.write(wildcard_content)
                
                wildcard_files[group_name] = wildcard_path
                logger.info(f"Generated wildcard file for group '{group_name}': {wildcard_path}")
                
            except Exception as e:
                logger.error(f"Failed to generate wildcard for group '{group_name}': {e}")
                continue
        
        return wildcard_files
    
    def generate_combined_wildcard(self, results: List[Dict[str, Any]], base_directory: str) -> str:
        """
        Generate a combined wildcard file with all prompts.
        
        Args:
            results: List of analysis result dictionaries
            base_directory: Base directory containing the images
            
        Returns:
            Path to the combined wildcard file
        """
        try:
            # Extract all prompts from all results
            all_prompts = []
            for result in results:
                prompts = self.extract_prompts_from_result(result)
                all_prompts.extend(prompts)
            
            # Create combined wildcard content
            wildcard_content = self.create_wildcard_content(all_prompts, "combined")
            
            # Create combined wildcard file
            combined_filename = "combined_all.txt"
            combined_path = os.path.join(self.wildcards_dir, combined_filename)
            
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write(wildcard_content)
            
            logger.info(f"Generated combined wildcard file: {combined_path}")
            return combined_path
            
        except Exception as e:
            logger.error(f"Failed to generate combined wildcard: {e}")
            return ""
    
    def generate_group_combinations(self, results: List[Dict[str, Any]], base_directory: str) -> Dict[str, str]:
        """
        Generate wildcard files for combinations of groups.
        
        Args:
            results: List of analysis result dictionaries
            base_directory: Base directory containing the images
            
        Returns:
            Dictionary mapping combination names to wildcard file paths
        """
        # First, get individual group wildcards
        group_wildcards = self.generate_wildcards_from_results(results, base_directory)
        
        if len(group_wildcards) < 2:
            return {}
        
        # Generate combinations of 2-3 groups
        group_names = list(group_wildcards.keys())
        combination_files = {}
        
        # Combinations of 2 groups
        for i in range(len(group_names)):
            for j in range(i + 1, len(group_names)):
                group1, group2 = group_names[i], group_names[j]
                combo_name = f"{group1}_{group2}"
                
                try:
                    # Combine prompts from both groups
                    all_prompts = []
                    
                    # Read prompts from both wildcard files
                    for group in [group1, group2]:
                        wildcard_path = group_wildcards[group]
                        if os.path.exists(wildcard_path):
                            with open(wildcard_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Extract prompts (lines that don't start with #)
                                lines = content.split('\n')
                                for line in lines:
                                    line = line.strip()
                                    if line and not line.startswith('#'):
                                        all_prompts.append(line)
                    
                    # Create combination wildcard
                    wildcard_content = self.create_wildcard_content(all_prompts, combo_name)
                    combo_filename = f"{combo_name}.txt"
                    combo_path = os.path.join(self.wildcards_dir, combo_filename)
                    
                    with open(combo_path, 'w', encoding='utf-8') as f:
                        f.write(wildcard_content)
                    
                    combination_files[combo_name] = combo_path
                    logger.info(f"Generated combination wildcard: {combo_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to generate combination {combo_name}: {e}")
                    continue
        
        return combination_files
    
    def generate_wildcards_from_database(self, db_manager) -> Dict[str, str]:
        """
        Generate wildcard files from database results.
        
        Args:
            db_manager: Database manager instance
            
        Returns:
            Dictionary mapping group names to wildcard file paths
        """
        try:
            # Get all results from database
            results = db_manager.get_all_results()
            
            if not results:
                logger.warning("No results found in database")
                return {}
            
            # Use the first result to determine base directory
            base_directory = results[0].get('directory', 'Images')
            
            # Generate wildcards
            return self.generate_wildcards_from_results(results, base_directory)
            
        except Exception as e:
            logger.error(f"Failed to generate wildcards from database: {e}")
            return {}

def main():
    """Test the wildcard generator"""
    # Example usage
    generator = WildcardGenerator("Output")
    
    # Example results
    example_results = [
        {
            'filename': 'image1.jpg',
            'directory': 'Images/landscapes',
            'analysis_results': json.dumps({
                'best': {'prompt': 'A beautiful mountain landscape with snow peaks'},
                'fast': {'prompt': 'Mountain landscape'}
            })
        },
        {
            'filename': 'image2.jpg',
            'directory': 'Images/portraits',
            'analysis_results': json.dumps({
                'best': {'prompt': 'A professional portrait of a woman'},
                'fast': {'prompt': 'Portrait photo'}
            })
        }
    ]
    
    # Generate wildcards
    wildcard_files = generator.generate_wildcards_from_results(example_results, 'Images')
    print(f"Generated wildcard files: {wildcard_files}")
    
    # Generate combined wildcard
    combined_file = generator.generate_combined_wildcard(example_results, 'Images')
    print(f"Combined wildcard file: {combined_file}")

if __name__ == "__main__":
    main() 