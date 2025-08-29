#!/usr/bin/env python3
"""
Dataset Downloader for Plagiarism Detection Training
Downloads and prepares datasets for integration with the plagiarism checker system.
"""

import os
import requests
import zipfile
import json
from pathlib import Path

def download_file(url, filename):
    """Download a file from URL with progress indication."""
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end='', flush=True)
    print(f"\n{filename} downloaded successfully!")

def download_pan_dataset():
    """Download PAN 2011 Plagiarism Detection Dataset."""
    base_dir = Path("datasets/pan2011")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # PAN 2011 dataset URLs (these are example URLs - you may need to find current links)
    datasets = {
        "pan11-plagiarism-detection-training-corpus.zip": 
            "https://zenodo.org/record/3250095/files/pan11-plagiarism-detection-training-corpus.zip",
        "pan11-plagiarism-detection-test-corpus.zip":
            "https://zenodo.org/record/3250095/files/pan11-plagiarism-detection-test-corpus.zip"
    }
    
    for filename, url in datasets.items():
        filepath = base_dir / filename
        if not filepath.exists():
            try:
                download_file(url, filepath)
                
                # Extract the zip file
                print(f"Extracting {filename}...")
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(base_dir)
                print(f"Extracted {filename}")
                
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
                print("Note: You may need to manually download from PAN website")
        else:
            print(f"{filename} already exists, skipping download")

def download_wikipedia_sample():
    """Download a sample of Wikipedia articles for reference corpus."""
    base_dir = Path("datasets/wikipedia")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Wikipedia API to get random articles
    api_url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
    articles = []
    
    print("Downloading 100 random Wikipedia articles...")
    for i in range(100):
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                articles.append({
                    'title': data.get('title', ''),
                    'extract': data.get('extract', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                })
                print(f"\rDownloaded {i+1}/100 articles", end='', flush=True)
        except Exception as e:
            print(f"\nError downloading article {i+1}: {e}")
    
    # Save articles to JSON file
    output_file = base_dir / "wikipedia_articles.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(articles)} articles to {output_file}")

def download_arxiv_sample():
    """Download sample ArXiv papers using ArXiv API."""
    base_dir = Path("datasets/arxiv")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # ArXiv API for recent computer science papers
    api_url = "http://export.arxiv.org/api/query"
    params = {
        'search_query': 'cat:cs.AI OR cat:cs.CL OR cat:cs.LG',
        'start': 0,
        'max_results': 50,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    print("Downloading ArXiv paper abstracts...")
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        # Parse XML response (simplified - you might want to use xml.etree.ElementTree)
        content = response.text
        
        # Save raw XML
        output_file = base_dir / "arxiv_papers.xml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Saved ArXiv data to {output_file}")
        
    except Exception as e:
        print(f"Error downloading ArXiv data: {e}")

if __name__ == "__main__":
    print("=== Dataset Downloader for Plagiarism Detection ===")
    print()
    
    print("Available datasets:")
    print("1. PAN 2011 Plagiarism Detection Dataset")
    print("2. Wikipedia Sample (100 articles)")
    print("3. ArXiv Sample (50 papers)")
    print("4. All datasets")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        download_pan_dataset()
    elif choice == "2":
        download_wikipedia_sample()
    elif choice == "3":
        download_arxiv_sample()
    elif choice == "4":
        download_pan_dataset()
        download_wikipedia_sample()
        download_arxiv_sample()
    else:
        print("Invalid choice. Please run the script again.")
    
    print("\n=== Download Complete ===")
    print("Next steps:")
    print("1. Run dataset_preprocessor.py to clean and prepare the data")
    print("2. Run dataset_integrator.py to add data to your Django system")
