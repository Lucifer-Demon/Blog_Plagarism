#!/usr/bin/env python3
"""
Add Sample Data to Django Database
Simple script to add sample training data to your plagiarism detection system.
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Plagiarism_Checker.settings')
django.setup()

from plagiarismchecker.models import ReferenceDocument

def add_sample_data():
    """Add sample data to ReferenceDocument model."""
    
    # Check if sample data exists
    data_file = "sample_datasets/training_data.json"
    if not os.path.exists(data_file):
        print(f"Sample data not found at {data_file}")
        print("Please run: python simple_dataset_setup.py first")
        return
    
    print(f"Loading sample data from {data_file}...")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Add only original documents to reference database
    original_docs = [d for d in data if d['type'] == 'original']
    added_count = 0
    skipped_count = 0
    
    print(f"Processing {len(original_docs)} original documents...")
    
    for doc in original_docs:
        # Check if document already exists
        if ReferenceDocument.objects.filter(title=doc['title']).exists():
            skipped_count += 1
            continue
        
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
    
    total_docs = ReferenceDocument.objects.count()
    
    print(f"\nDatabase update complete!")
    print(f"Added: {added_count} new documents")
    print(f"Skipped: {skipped_count} existing documents") 
    print(f"Total reference documents in database: {total_docs}")
    
    if added_count > 0:
        print(f"\nYour plagiarism detection system now has enhanced reference data!")
        print("Test the 'Check File' and 'Check Plagiarism' functions to see improved accuracy.")

if __name__ == "__main__":
    print("=== Adding Sample Data to Django Database ===")
    add_sample_data()
