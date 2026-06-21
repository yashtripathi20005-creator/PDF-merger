
## File 5: `setup.py` (Optional - for packaging)

```python
"""
Setup script for PDF Merger & Splitter Tool
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pdf-merger-splitter",
    version="1.0.0",
    author="[Your Name]",
    author_email="[your.email@example.com]",
    description="A comprehensive PDF merger and splitter tool with GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pdf-merger-splitter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "PyPDF2>=3.0.0",
        "tkinterdnd2>=0.3.0",
    ],
    entry_points={
        "console_scripts": [
            "pdf-merger-splitter=pdf_merger_splitter:main",
        ],
    },
)
