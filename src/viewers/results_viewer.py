#!/usr/bin/env python3
"""
Results Viewer for Image Analysis with CLIP and LLM

This script provides a simple interface to view and explore analysis results.
It can display individual image results, generate summaries, and export data.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import argparse

def print_banner():
    """Print the application banner"""
    print("📊 Image Analysis Results Viewer")
    print("=" * 40)
    print()

def load_analysis_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load an analysis JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load {file_path}: {e}")
        return None

def find_analysis_files(directory: str) -> List[str]:
    """Find all analysis files in a directory"""
    analysis_files = []
    for file in os.listdir(directory):
        if file.endswith('_analysis.json'):
            analysis_files.append(os.path.join(directory, file))
    return sorted(analysis_files)

def display_file_info(data: Dict[str, Any]):
    """Display file information"""
    file_info = data.get('file_info', {})
    print(f"📁 File: {file_info.get('filename', 'Unknown')}")
    print(f"📂 Directory: {file_info.get('directory', 'Unknown')}")
    print(f"📅 Date Added: {file_info.get('date_added', 'Unknown')}")
    print(f"📅 Date Processed: {file_info.get('date_processed', 'Unknown')}")
    print(f"🔢 File Size: {file_info.get('file_size', 0):,} bytes")
    print(f"🔐 MD5: {file_info.get('md5', 'Unknown')[:16]}...")
    print()

def display_processing_info(data: Dict[str, Any]):
    """Display processing information"""
    proc_info = data.get('processing_info', {})
    print(f"⚙️  Processing Status: {proc_info.get('status', 'Unknown')}")
    print(f"⏱️  Processing Time: {proc_info.get('processing_time', 0):.2f} seconds")
    
    config = proc_info.get('config_used', {})
    print(f"🔍 CLIP Analysis: {'✅ Enabled' if config.get('clip_enabled') else '❌ Disabled'}")
    print(f"🤖 LLM Analysis: {'✅ Enabled' if config.get('llm_enabled') else '❌ Disabled'}")
    
    if config.get('clip_modes'):
        print(f"📋 CLIP Modes: {', '.join(config['clip_modes'])}")
    if config.get('llm_models'):
        print(f"🤖 LLM Models: {', '.join(map(str, config['llm_models']))}")
    if config.get('prompt_choices'):
        print(f"📝 Prompts: {', '.join(config['prompt_choices'])}")
    
    errors = proc_info.get('errors', [])
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors:
            print(f"   • {error.get('type', 'Unknown')}: {error.get('error', 'Unknown error')}")
    
    print()

def display_clip_results(data: Dict[str, Any]):
    """Display CLIP analysis results"""
    clip_data = data.get('analysis', {}).get('clip', {})
    if not clip_data:
        print("🔍 No CLIP analysis results found")
        return
    
    print("🔍 CLIP Analysis Results:")
    print("-" * 30)
    
    # Display prompt results
    for mode, result in clip_data.items():
        if isinstance(result, dict) and 'prompt' in result:
            print(f"📝 {mode.upper()} Prompt:")
            print(f"   {result['prompt'][:100]}{'...' if len(result['prompt']) > 100 else ''}")
            print()
    
    # Display analysis results if available
    analysis_results = data.get('analysis_results', {})
    if analysis_results:
        print("📊 Analysis Categories:")
        for category, items in analysis_results.items():
            if isinstance(items, dict):
                print(f"   {category.upper()}:")
                for item, score in list(items.items())[:5]:  # Show top 5
                    print(f"     • {item}: {score:.4f}")
                print()

def display_llm_results(data: Dict[str, Any]):
    """Display LLM analysis results"""
    llm_data = data.get('analysis', {}).get('llm', {})
    if not llm_data:
        print("🤖 No LLM analysis results found")
        return
    
    print("🤖 LLM Analysis Results:")
    print("-" * 30)
    
    for response in llm_data:
        prompt_id = response.get('prompt', 'Unknown')
        status = response.get('status', 'unknown')
        
        print(f"📝 Prompt: {prompt_id} ({status})")
        
        if status == 'success':
            result = response.get('result', {})
            choices = result.get('choices', [])
            if choices:
                content = choices[0].get('message', {}).get('content', '')
                print(f"   Response: {content[:200]}{'...' if len(content) > 200 else ''}")
                
                usage = result.get('usage', {})
                if usage:
                    print(f"   Tokens: {usage.get('prompt_tokens', 0)} + {usage.get('completion_tokens', 0)} = {usage.get('total_tokens', 0)}")
        else:
            error = response.get('error', 'Unknown error')
            print(f"   Error: {error}")
        
        print()

def display_metadata(data: Dict[str, Any]):
    """Display image metadata"""
    metadata = data.get('analysis', {}).get('metadata', {})
    if not metadata:
        print("📋 No metadata found")
        return
    
    print("📋 Image Metadata:")
    print("-" * 20)
    
    if 'width' in metadata and 'height' in metadata:
        print(f"📐 Dimensions: {metadata['width']} x {metadata['height']}")
    
    if 'format' in metadata:
        print(f"🖼️  Format: {metadata['format']}")
    
    if 'color_mode' in metadata:
        print(f"🎨 Color Mode: {metadata['color_mode']}")
    
    if 'aspect_ratio' in metadata:
        print(f"📏 Aspect Ratio: {metadata['aspect_ratio']:.2f}")
    
    if 'dpi' in metadata:
        dpi = metadata['dpi']
        if isinstance(dpi, (list, tuple)) and len(dpi) >= 2:
            print(f"🔍 DPI: {dpi[0]} x {dpi[1]}")
    
    print()

def view_single_file(file_path: str):
    """View a single analysis file"""
    data = load_analysis_file(file_path)
    if not data:
        return
    
    print_banner()
    print(f"📄 Viewing: {os.path.basename(file_path)}")
    print("=" * 50)
    print()
    
    display_file_info(data)
    display_processing_info(data)
    display_metadata(data)
    display_clip_results(data)
    display_llm_results(data)

def list_files(directory: str):
    """List all analysis files in a directory"""
    analysis_files = find_analysis_files(directory)
    
    if not analysis_files:
        print(f"❌ No analysis files found in {directory}")
        return
    
    print_banner()
    print(f"📁 Analysis Files in {directory}:")
    print("=" * 50)
    print()
    
    for i, file_path in enumerate(analysis_files, 1):
        data = load_analysis_file(file_path)
        if data:
            file_info = data.get('file_info', {})
            proc_info = data.get('processing_info', {})
            
            filename = file_info.get('filename', 'Unknown')
            status = proc_info.get('status', 'Unknown')
            processing_time = proc_info.get('processing_time', 0)
            
            status_emoji = "✅" if status == "complete" else "❌" if status == "failed" else "⏳"
            
            print(f"{i:2d}. {status_emoji} {filename}")
            print(f"    Status: {status} | Time: {processing_time:.2f}s")
            
            # Show what analyses were performed
            analyses = []
            if data.get('analysis', {}).get('clip'):
                analyses.append("CLIP")
            if data.get('analysis', {}).get('llm'):
                analyses.append("LLM")
            if data.get('analysis', {}).get('metadata'):
                analyses.append("Metadata")
            
            if analyses:
                print(f"    Analyses: {', '.join(analyses)}")
            print()

def generate_summary(directory: str, output_file: str = None):
    """Generate a summary of all analysis results"""
    analysis_files = find_analysis_files(directory)
    
    if not analysis_files:
        print(f"❌ No analysis files found in {directory}")
        return
    
    print_banner()
    print("📊 Generating Summary Report")
    print("=" * 40)
    print()
    
    summary = {
        "generated_at": datetime.now().isoformat(),
        "directory": directory,
        "total_files": len(analysis_files),
        "statistics": {
            "complete": 0,
            "failed": 0,
            "pending": 0
        },
        "analyses": {
            "clip": 0,
            "llm": 0,
            "metadata": 0
        },
        "files": []
    }
    
    total_processing_time = 0
    
    for file_path in analysis_files:
        data = load_analysis_file(file_path)
        if not data:
            continue
        
        file_info = data.get('file_info', {})
        proc_info = data.get('processing_info', {})
        analysis = data.get('analysis', {})
        
        status = proc_info.get('status', 'unknown')
        summary["statistics"][status] = summary["statistics"].get(status, 0) + 1
        
        if analysis.get('clip'):
            summary["analyses"]["clip"] += 1
        if analysis.get('llm'):
            summary["analyses"]["llm"] += 1
        if analysis.get('metadata'):
            summary["analyses"]["metadata"] += 1
        
        processing_time = proc_info.get('processing_time', 0)
        total_processing_time += processing_time
        
        file_summary = {
            "filename": file_info.get('filename'),
            "status": status,
            "processing_time": processing_time,
            "file_size": file_info.get('file_size', 0),
            "analyses_performed": []
        }
        
        if analysis.get('clip'):
            file_summary["analyses_performed"].append("CLIP")
        if analysis.get('llm'):
            file_summary["analyses_performed"].append("LLM")
        if analysis.get('metadata'):
            file_summary["analyses_performed"].append("Metadata")
        
        summary["files"].append(file_summary)
    
    # Display summary
    print(f"📁 Directory: {directory}")
    print(f"📊 Total Files: {summary['total_files']}")
    print(f"✅ Complete: {summary['statistics']['complete']}")
    print(f"❌ Failed: {summary['statistics']['failed']}")
    print(f"⏳ Pending: {summary['statistics']['pending']}")
    print()
    
    print("🔍 Analysis Types:")
    print(f"   CLIP: {summary['analyses']['clip']} files")
    print(f"   LLM: {summary['analyses']['llm']} files")
    print(f"   Metadata: {summary['analyses']['metadata']} files")
    print()
    
    if total_processing_time > 0:
        avg_time = total_processing_time / summary['total_files']
        print(f"⏱️  Total Processing Time: {total_processing_time:.2f}s")
        print(f"⏱️  Average Time per File: {avg_time:.2f}s")
        print()
    
    # Save summary if output file specified
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"✅ Summary saved to {output_file}")
        except Exception as e:
            print(f"❌ Failed to save summary: {e}")

def export_results(directory: str, output_file: str, format_type: str = "json"):
    """Export analysis results in various formats"""
    analysis_files = find_analysis_files(directory)
    
    if not analysis_files:
        print(f"❌ No analysis files found in {directory}")
        return
    
    print_banner()
    print(f"📤 Exporting Results ({format_type.upper()})")
    print("=" * 40)
    print()
    
    all_results = []
    
    for file_path in analysis_files:
        data = load_analysis_file(file_path)
        if data:
            all_results.append(data)
    
    if format_type.lower() == "json":
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f"✅ Exported {len(all_results)} results to {output_file}")
        except Exception as e:
            print(f"❌ Failed to export: {e}")
    
    elif format_type.lower() == "csv":
        import csv
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Filename', 'Status', 'Processing Time', 'File Size',
                    'CLIP Analysis', 'LLM Analysis', 'Metadata',
                    'Date Added', 'Date Processed'
                ])
                
                # Write data
                for data in all_results:
                    file_info = data.get('file_info', {})
                    proc_info = data.get('processing_info', {})
                    analysis = data.get('analysis', {})
                    
                    writer.writerow([
                        file_info.get('filename', ''),
                        proc_info.get('status', ''),
                        proc_info.get('processing_time', 0),
                        file_info.get('file_size', 0),
                        'Yes' if analysis.get('clip') else 'No',
                        'Yes' if analysis.get('llm') else 'No',
                        'Yes' if analysis.get('metadata') else 'No',
                        file_info.get('date_added', ''),
                        file_info.get('date_processed', '')
                    ])
            
            print(f"✅ Exported {len(all_results)} results to {output_file}")
        except Exception as e:
            print(f"❌ Failed to export: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="View and explore image analysis results")
    parser.add_argument("--directory", "-d", default="Output", 
                       help="Directory containing analysis files (default: Output)")
    parser.add_argument("--file", "-f", help="View a specific analysis file")
    parser.add_argument("--list", "-l", action="store_true", 
                       help="List all analysis files")
    parser.add_argument("--summary", "-s", action="store_true", 
                       help="Generate summary report")
    parser.add_argument("--export", "-e", help="Export results to file")
    parser.add_argument("--format", choices=["json", "csv"], default="json",
                       help="Export format (default: json)")
    parser.add_argument("--output", "-o", help="Output file for summary/export")
    
    args = parser.parse_args()
    
    if args.file:
        view_single_file(args.file)
    elif args.list:
        list_files(args.directory)
    elif args.summary:
        output_file = args.output or f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        generate_summary(args.directory, output_file)
    elif args.export:
        output_file = args.output or f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}"
        export_results(args.directory, output_file, args.format)
    else:
        # Default: list files
        list_files(args.directory)

if __name__ == "__main__":
    main() 