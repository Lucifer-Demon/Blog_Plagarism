
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
            try:
                # Add source info to title for identification
                enhanced_title = f"{doc['title']} [{doc['source']}]"
                ReferenceDocument.objects.create(
                    title=enhanced_title,
                    content=doc['content']
                )
                added_count += 1
                print(f"Added: {doc['title'][:50]}...")
                
            except Exception as e:
                print(f"Error adding document '{doc['title']}': {e}")
    
    print(f"Added {added_count} new reference documents")
    print(f"Total reference documents: {ReferenceDocument.objects.count()}")

if __name__ == "__main__":
    json_file = "sample_datasets/training_data.json"
    if os.path.exists(json_file):
        add_to_database(json_file)
    else:
        print(f"Data file not found: {json_file}")
        print("Please run simple_dataset_setup.py first")
