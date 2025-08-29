"""
Django Management Command for Dataset Integration
Run with: python manage.py integrate_datasets
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import json
import os
from pathlib import Path
from plagiarismchecker.models import ReferenceDocument, TrainedDatasetModel, DatasetDocument

class Command(BaseCommand):
    help = 'Integrate processed datasets into the plagiarism detection system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset-file',
            type=str,
            default='processed_datasets/combined_training_data.json',
            help='Path to the processed dataset JSON file'
        )
        parser.add_argument(
            '--dataset-name',
            type=str,
            default='combined_dataset',
            help='Name for the dataset in the database'
        )
    
    def handle(self, *args, **options):
        dataset_file = options['dataset_file']
        dataset_name = options['dataset_name']
        
        self.stdout.write(f"Integrating dataset: {dataset_name}")
        self.stdout.write(f"From file: {dataset_file}")
        
        # Load processed data
        if not os.path.exists(dataset_file):
            self.stdout.write(
                self.style.ERROR(f"Dataset file not found: {dataset_file}")
            )
            self.stdout.write("Please run dataset_preprocessor.py first")
            return
        
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.stdout.write(f"Loaded {len(data)} documents")
        
        # Add to reference documents
        self.add_reference_documents(data)
        
        # Create dataset documents
        self.create_dataset_documents(data, dataset_name)
        
        self.stdout.write(
            self.style.SUCCESS(f"Dataset integration complete!")
        )
    
    def add_reference_documents(self, data):
        """Add original documents to ReferenceDocument model."""
        self.stdout.write("Adding reference documents...")
        
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
        
        self.stdout.write(f"Added {added_count} new reference documents")
        self.stdout.write(f"Total reference documents: {ReferenceDocument.objects.count()}")
    
    def create_dataset_documents(self, data, dataset_name):
        """Create DatasetDocument entries."""
        self.stdout.write(f"Creating dataset documents for {dataset_name}...")
        
        # Clear existing documents for this dataset
        deleted_count = DatasetDocument.objects.filter(dataset_name=dataset_name).count()
        DatasetDocument.objects.filter(dataset_name=dataset_name).delete()
        if deleted_count > 0:
            self.stdout.write(f"Cleared {deleted_count} existing documents")
        
        # Create new documents
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
        self.stdout.write(f"Created {len(documents)} dataset documents")
        
        # Create TrainedDatasetModel entry (without actual TF-IDF training for now)
        trained_model, created = TrainedDatasetModel.objects.get_or_create(
            dataset_name=dataset_name,
            defaults={
                'vectorizer_path': f'models/{dataset_name}/tfidf_vectorizer.pkl',
                'description': f'Dataset with {len(documents)} documents from various sources',
                'document_count': len(documents)
            }
        )
        
        if not created:
            trained_model.document_count = len(documents)
            trained_model.save()
        
        self.stdout.write(f"TrainedDatasetModel {'created' if created else 'updated'}")
