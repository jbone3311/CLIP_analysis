#!/usr/bin/env python3
"""
Setup script for Image Analysis with CLIP and LLM
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    with open(this_directory / "requirements.txt", "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="image-analysis-clip-llm",
    version="2.0.0",
    author="jbone3311",
    description="Advanced image analysis using CLIP and LLM technologies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jbone3311/CLIP_analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "image-analysis=main:main",
            "clip-analyzer=src.analyzers.clip_analyzer:main",
            "llm-analyzer=src.analyzers.llm_analyzer:main",
            "config-manager=src.config.config_manager:main",
            "results-viewer=src.viewers.results_viewer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.ini", "*.md"],
    },
    keywords="image analysis, CLIP, LLM, AI, computer vision, machine learning",
    project_urls={
        "Source": "https://github.com/jbone3311/CLIP_analysis",
        "Documentation": "https://github.com/jbone3311/CLIP_analysis#readme",
    },
) 