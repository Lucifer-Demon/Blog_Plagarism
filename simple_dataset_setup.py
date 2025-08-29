#!/usr/bin/env python3
"""
Simple Dataset Setup for Plagiarism Detection System
A simplified approach that works with your existing Django setup.
"""

import json
import requests
import os
from pathlib import Path

def download_sample_data():
    """Download sample training data from public APIs."""
    print("=== Downloading Sample Training Data ===")
    
    # Create directories
    datasets_dir = Path("sample_datasets")
    datasets_dir.mkdir(exist_ok=True)
    
    # 1. Download Wikipedia articles
    print("Downloading Wikipedia articles...")
    wikipedia_articles = []
    
    # Get random articles using Wikipedia API
    for i in range(20):  # Start with 20 articles
        try:
            url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                extract = data.get('extract', '')
                if extract and len(extract) > 100:
                    wikipedia_articles.append({
                        'title': data.get('title', f'Article {i+1}'),
                        'content': extract,
                        'source': 'wikipedia',
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        'type': 'original'
                    })
                    print(f"Downloaded: {data.get('title', 'Unknown')}")
        except Exception as e:
            print(f"Error downloading article {i+1}: {e}")
    
    # Save Wikipedia data
    wiki_file = datasets_dir / "wikipedia_sample.json"
    with open(wiki_file, 'w', encoding='utf-8') as f:
        json.dump(wikipedia_articles, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(wikipedia_articles)} Wikipedia articles to {wiki_file}")
    
    # 2. Create some sample academic content
    print("Creating sample academic content...")
    academic_samples = [
        {
            'title': 'Introduction to Machine Learning',
            'content': 'Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models that computer systems use to perform tasks without explicit instructions. It relies on patterns and inference instead of traditional programming approaches.',
            'source': 'academic_sample',
            'type': 'original'
        },
        {
            'title': 'Data Structures and Algorithms',
            'content': 'Data structures are ways of organizing and storing data in a computer so that it can be accessed and modified efficiently. Common data structures include arrays, linked lists, stacks, queues, trees, and graphs. Each has specific use cases and performance characteristics.',
            'source': 'academic_sample',
            'type': 'original'
        },
        {
            'title': 'Software Engineering Principles',
            'content': 'Software engineering is the systematic application of engineering approaches to the development of software. It involves requirements analysis, design, implementation, testing, and maintenance of software systems using structured methodologies.',
            'source': 'academic_sample',
            'type': 'original'
        }
    ]
    
    # Save academic samples
    academic_file = datasets_dir / "academic_samples.json"
    with open(academic_file, 'w', encoding='utf-8') as f:
        json.dump(academic_samples, f, indent=2, ensure_ascii=False)
    
    print(f"Created {len(academic_samples)} academic samples in {academic_file}")
    
    # 3. Create plagiarized versions
    print("Creating plagiarized samples...")
    plagiarized_samples = []
    
    all_original = wikipedia_articles + academic_samples
    
    for i, doc in enumerate(all_original[:10]):  # Create plagiarized versions of first 10
        content = doc['content']
        
        # Simple paraphrasing
        paraphrased = content.replace('is', 'represents').replace('the', 'a').replace('and', 'as well as')
        plagiarized_samples.append({
            'title': f"Paraphrased: {doc['title']}",
            'content': paraphrased,
            'source': f"paraphrased_from_{doc['source']}",
            'original_title': doc['title'],
            'type': 'plagiarized'
        })
    
    # Save plagiarized samples
    plag_file = datasets_dir / "plagiarized_samples.json"
    with open(plag_file, 'w', encoding='utf-8') as f:
        json.dump(plagiarized_samples, f, indent=2, ensure_ascii=False)
    
    print(f"Created {len(plagiarized_samples)} plagiarized samples in {plag_file}")
    
    # 4. Combine all data
    all_data = wikipedia_articles + academic_samples + plagiarized_samples
    combined_file = datasets_dir / "training_data.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSample dataset creation complete!")
    print(f"Total documents: {len(all_data)}")
    print(f"Original: {len([d for d in all_data if d['type'] == 'original'])}")
    print(f"Plagiarized: {len([d for d in all_data if d['type'] == 'plagiarized'])}")
    print(f"Combined file: {combined_file}")
    
    return str(combined_file)

def create_django_integration_script():
    """Create a simple script to add data to Django database."""
    script_content = '''
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Plagiarism_Checker.settings')
django.setup()

from plagiarismchecker.models import ReferenceDocument

def add_to_database(json_file):
    """Add sample data to ReferenceDocument model."""
    print(f"Loading data from {json_file}...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_docs = [d for d in data if d['type'] == 'original']
    added_count = 0
    
    for doc in original_docs:
        # Check if already exists
        if not ReferenceDocument.objects.filter(title=doc['title']).exists():
            ReferenceDocument.objects.create(
                title=doc['title'],
                content=doc['content'],
                source_url=doc.get('url', ''),
                description=f"From {doc['source']} dataset"
            )
            added_count += 1
    
    print(f"Added {added_count} new reference documents")
    print(f"Total reference documents: {ReferenceDocument.objects.count()}")

if __name__ == "__main__":
    json_file = "sample_datasets/training_data.json"
    if os.path.exists(json_file):
        add_to_database(json_file)
    else:
        print(f"Data file not found: {json_file}")
        print("Please run simple_dataset_setup.py first")
'''
    
    with open("add_to_database.py", 'w') as f:
        f.write(script_content)
    
    print("Created add_to_database.py script")

if __name__ == "__main__":
    print("=== Simple Dataset Setup ===")
    print("This will create sample training data for your plagiarism detection system.")
    print()
    
    # Download and create sample data
    json_file = download_sample_data()
    
    # Create Django integration script
    create_django_integration_script()
    
    print("\n=== Next Steps ===")
    print("1. Run: python add_to_database.py")
    print("   (This adds the sample data to your Django database)")
    print()
    print("2. Test your plagiarism checker with the new reference data")
    print()
    print("The sample data will improve the accuracy of:")
    print("- Check File function")
    print("- Check Plagiarism function") 
    print("- Local reference checking")
