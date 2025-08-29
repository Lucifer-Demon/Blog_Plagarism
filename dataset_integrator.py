#!/usr/bin/env python3
"""
Dataset Integrator for Django Plagiarism Detection System
Integrates processed datasets into the Django database and trains TF-IDF models.
"""

import os
import sys
import django
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import numpy as np

# Add the Django project to Python path
project_path = Path(__file__).parent
sys.path.append(str(project_path))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Plagiarism_Checker.settings')
django.setup()

# Import Django models
from plagiarismchecker.models import ReferenceDocument, TrainedDatasetModel, DatasetDocument

class DatasetIntegrator:
    def __init__(self):
        self.processed_dir = Path("processed_datasets")
        self.models_dir = Path("trained_models")
        self.models_dir.mkdir(exist_ok=True)
    
    def load_processed_data(self, filename="combined_training_data.json"):
        """Load processed dataset from JSON file."""
        file_path = self.processed_dir / filename
        if not file_path.exists():
            print(f"Processed data not found at {file_path}")
            print("Please run dataset_preprocessor.py first")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} documents from {filename}")
        return data
    
    def add_to_reference_documents(self, data):
        """Add original documents to ReferenceDocument model for local checking."""
        print("Adding documents to ReferenceDocument model...")
        
        original_docs = [d for d in data if d['type'] == 'original']
        added_count = 0
        
        for doc in original_docs:
            # Check if document already exists
            existing = ReferenceDocument.objects.filter(
                title=doc['title']
            ).first()
            
            if not existing:
                ReferenceDocument.objects.create(
                    title=doc['title'],
                    content=doc['content'],
                    source_url=doc.get('url', ''),
                    description=f"From {doc['source']} dataset"
                )
                added_count += 1
        
        print(f"Added {added_count} new reference documents")
        print(f"Total reference documents in database: {ReferenceDocument.objects.count()}")
    
    def create_dataset_documents(self, data, dataset_name):
        """Create DatasetDocument entries for training."""
        print(f"Creating DatasetDocument entries for {dataset_name}...")
        
        # Clear existing documents for this dataset
        DatasetDocument.objects.filter(dataset_name=dataset_name).delete()
        
        documents = []
        for doc in data:
            documents.append(DatasetDocument(
                dataset_name=dataset_name,
                title=doc['title'],
                content=doc['content'],
                source_type=doc['source'],
                is_plagiarized=(doc['type'] == 'plagiarized')
            ))
        
        # Bulk create for efficiency
        DatasetDocument.objects.bulk_create(documents, batch_size=100)
        print(f"Created {len(documents)} dataset documents")
    
    def train_tfidf_model(self, data, dataset_name):
        """Train TF-IDF model on the dataset."""
        print(f"Training TF-IDF model for {dataset_name}...")
        
        # Prepare training texts
        texts = [doc['content'] for doc in data if doc['content']]
        
        if len(texts) < 10:
            print(f"Not enough texts ({len(texts)}) to train a meaningful model")
            return None
        
        # Train TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 3),  # Unigrams, bigrams, and trigrams
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.95  # Ignore terms that appear in more than 95% of documents
        )
        
        print(f"Training on {len(texts)} documents...")
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Save the trained model
        model_dir = self.models_dir / dataset_name
        model_dir.mkdir(exist_ok=True)
        
        vectorizer_path = model_dir / "tfidf_vectorizer.pkl"
        matrix_path = model_dir / "tfidf_matrix.pkl"
        
        joblib.dump(vectorizer, vectorizer_path)
        joblib.dump(tfidf_matrix, matrix_path)
        
        print(f"Model saved to {model_dir}")
        
        # Create or update TrainedDatasetModel entry
        trained_model, created = TrainedDatasetModel.objects.get_or_create(
            dataset_name=dataset_name,
            defaults={
                'vectorizer_path': str(vectorizer_path),
                'description': f"TF-IDF model trained on {len(texts)} documents from {dataset_name}",
                'document_count': len(texts)
            }
        )
        
        if not created:
            trained_model.vectorizer_path = str(vectorizer_path)
            trained_model.document_count = len(texts)
            trained_model.save()
        
        print(f"TrainedDatasetModel {'created' if created else 'updated'} for {dataset_name}")
        return vectorizer_path
    
    def integrate_dataset(self, dataset_name="combined_dataset"):
        """Complete integration process for a dataset."""
        print(f"\n=== Integrating Dataset: {dataset_name} ===")
        
        # Load processed data
        data = self.load_processed_data()
        if not data:
            return False
        
        # Add to reference documents (for local checking)
        self.add_to_reference_documents(data)
        
        # Create dataset documents (for custom model training)
        self.create_dataset_documents(data, dataset_name)
        
        # Train TF-IDF model
        model_path = self.train_tfidf_model(data, dataset_name)
        
        if model_path:
            print(f"\n✅ Dataset integration complete!")
            print(f"Dataset name: {dataset_name}")
            print(f"Documents: {len(data)}")
            print(f"Model path: {model_path}")
            return True
        else:
            print(f"\n❌ Dataset integration failed!")
            return False
    
    def create_sample_datasets(self):
        """Create separate datasets for different sources."""
        data = self.load_processed_data()
        if not data:
            return
        
        # Group by source
        sources = {}
        for doc in data:
            source = doc['source']
            if source not in sources:
                sources[source] = []
            sources[source].append(doc)
        
        # Create separate datasets for each source
        for source, docs in sources.items():
            if len(docs) >= 10:  # Only create dataset if enough documents
                dataset_name = f"{source}_dataset"
                print(f"\nCreating {dataset_name} with {len(docs)} documents...")
                
                self.create_dataset_documents(docs, dataset_name)
                self.train_tfidf_model(docs, dataset_name)

def main():
    integrator = DatasetIntegrator()
    
    print("=== Dataset Integration Options ===")
    print("1. Integrate all data as combined dataset")
    print("2. Create separate datasets by source (Wikipedia, ArXiv, etc.)")
    print("3. Both options")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        integrator.integrate_dataset("combined_dataset")
    elif choice == "2":
        integrator.create_sample_datasets()
    elif choice == "3":
        integrator.integrate_dataset("combined_dataset")
        integrator.create_sample_datasets()
    else:
        print("Invalid choice. Running combined dataset integration...")
        integrator.integrate_dataset("combined_dataset")
    
    print("\n=== Integration Complete ===")
    print("Your plagiarism detection system now has:")
    print(f"- {ReferenceDocument.objects.count()} reference documents")
    print(f"- {TrainedDatasetModel.objects.count()} trained models")
    print(f"- {DatasetDocument.objects.count()} dataset documents")

if __name__ == "__main__":
    main()
