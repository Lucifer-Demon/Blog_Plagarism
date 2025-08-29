#!/usr/bin/env python3
"""
Dataset Preprocessor for Plagiarism Detection Training
Cleans and prepares downloaded datasets for integration with the plagiarism checker system.
"""

import os
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import unicodedata
from typing import List, Dict, Tuple

class DatasetPreprocessor:
    def __init__(self, base_dir="datasets"):
        self.base_dir = Path(base_dir)
        self.output_dir = Path("processed_datasets")
        self.output_dir.mkdir(exist_ok=True)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Normalize Unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # Replace non-breaking spaces and other whitespace
        text = text.replace('\xa0', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, max_words: int = 500) -> List[str]:
        """Split text into chunks of specified word count."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), max_words):
            chunk = ' '.join(words[i:i + max_words])
            if len(chunk.strip()) > 50:  # Only keep substantial chunks
                chunks.append(chunk)
        
        return chunks
    
    def process_wikipedia_data(self):
        """Process Wikipedia articles into training format."""
        input_file = self.base_dir / "wikipedia" / "wikipedia_articles.json"
        output_file = self.output_dir / "wikipedia_processed.json"
        
        if not input_file.exists():
            print(f"Wikipedia data not found at {input_file}")
            return
        
        print("Processing Wikipedia articles...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        processed_articles = []
        for article in articles:
            title = article.get('title', '')
            extract = article.get('extract', '')
            url = article.get('url', '')
            
            if extract and len(extract) > 100:
                cleaned_text = self.clean_text(extract)
                chunks = self.chunk_text(cleaned_text, max_words=300)
                
                for i, chunk in enumerate(chunks):
                    processed_articles.append({
                        'id': f"wiki_{len(processed_articles)}",
                        'title': f"{title} (Part {i+1})" if len(chunks) > 1 else title,
                        'content': chunk,
                        'source': 'wikipedia',
                        'url': url,
                        'type': 'original'  # Mark as non-plagiarized content
                    })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_articles, f, indent=2, ensure_ascii=False)
        
        print(f"Processed {len(processed_articles)} Wikipedia chunks to {output_file}")
        return processed_articles
    
    def process_arxiv_data(self):
        """Process ArXiv papers into training format."""
        input_file = self.base_dir / "arxiv" / "arxiv_papers.xml"
        output_file = self.output_dir / "arxiv_processed.json"
        
        if not input_file.exists():
            print(f"ArXiv data not found at {input_file}")
            return
        
        print("Processing ArXiv papers...")
        
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            
            processed_papers = []
            
            # Parse ArXiv XML format
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
                summary_elem = entry.find('.//{http://www.w3.org/2005/Atom}summary')
                id_elem = entry.find('.//{http://www.w3.org/2005/Atom}id')
                
                if title_elem is not None and summary_elem is not None:
                    title = title_elem.text.strip() if title_elem.text else ""
                    summary = summary_elem.text.strip() if summary_elem.text else ""
                    paper_id = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
                    
                    if summary and len(summary) > 100:
                        cleaned_text = self.clean_text(summary)
                        chunks = self.chunk_text(cleaned_text, max_words=400)
                        
                        for i, chunk in enumerate(chunks):
                            processed_papers.append({
                                'id': f"arxiv_{len(processed_papers)}",
                                'title': f"{title} (Abstract Part {i+1})" if len(chunks) > 1 else f"{title} (Abstract)",
                                'content': chunk,
                                'source': 'arxiv',
                                'url': paper_id,
                                'type': 'original'
                            })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_papers, f, indent=2, ensure_ascii=False)
            
            print(f"Processed {len(processed_papers)} ArXiv chunks to {output_file}")
            return processed_papers
            
        except Exception as e:
            print(f"Error processing ArXiv data: {e}")
            return []
    
    def create_plagiarized_samples(self, original_data: List[Dict]) -> List[Dict]:
        """Create artificially plagiarized samples for training."""
        print("Creating plagiarized samples...")
        
        plagiarized_samples = []
        
        for i, item in enumerate(original_data[:20]):  # Create samples from first 20 items
            content = item['content']
            
            # Method 1: Word substitution (simple paraphrasing)
            paraphrased = self.simple_paraphrase(content)
            if paraphrased != content:
                plagiarized_samples.append({
                    'id': f"plag_para_{i}",
                    'title': f"Paraphrased: {item['title']}",
                    'content': paraphrased,
                    'source': f"paraphrased_from_{item['source']}",
                    'original_id': item['id'],
                    'type': 'plagiarized'
                })
            
            # Method 2: Sentence reordering
            reordered = self.reorder_sentences(content)
            if reordered != content:
                plagiarized_samples.append({
                    'id': f"plag_reorder_{i}",
                    'title': f"Reordered: {item['title']}",
                    'content': reordered,
                    'source': f"reordered_from_{item['source']}",
                    'original_id': item['id'],
                    'type': 'plagiarized'
                })
            
            # Method 3: Partial copying (take 70% of content)
            words = content.split()
            if len(words) > 20:
                partial_content = ' '.join(words[:int(len(words) * 0.7)])
                plagiarized_samples.append({
                    'id': f"plag_partial_{i}",
                    'title': f"Partial: {item['title']}",
                    'content': partial_content,
                    'source': f"partial_from_{item['source']}",
                    'original_id': item['id'],
                    'type': 'plagiarized'
                })
        
        print(f"Created {len(plagiarized_samples)} plagiarized samples")
        return plagiarized_samples
    
    def simple_paraphrase(self, text: str) -> str:
        """Simple paraphrasing by word substitution."""
        # Basic synonym replacements
        replacements = {
            'important': 'significant',
            'show': 'demonstrate',
            'use': 'utilize',
            'help': 'assist',
            'make': 'create',
            'good': 'excellent',
            'bad': 'poor',
            'big': 'large',
            'small': 'tiny',
            'fast': 'quick',
            'slow': 'gradual'
        }
        
        words = text.split()
        for i, word in enumerate(words):
            clean_word = word.lower().strip('.,!?;:')
            if clean_word in replacements:
                # Preserve original capitalization and punctuation
                if word[0].isupper():
                    replacement = replacements[clean_word].capitalize()
                else:
                    replacement = replacements[clean_word]
                
                # Add back punctuation
                punct = ''.join(c for c in word if not c.isalnum())
                words[i] = replacement + punct
        
        return ' '.join(words)
    
    def reorder_sentences(self, text: str) -> str:
        """Reorder sentences to create plagiarized content."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 3:
            # Simple reordering: move last sentence to beginning
            reordered = [sentences[-1]] + sentences[:-1]
            return '. '.join(reordered) + '.'
        
        return text
    
    def process_all_datasets(self):
        """Process all available datasets."""
        all_data = []
        
        # Process Wikipedia
        wiki_data = self.process_wikipedia_data()
        if wiki_data:
            all_data.extend(wiki_data)
        
        # Process ArXiv
        arxiv_data = self.process_arxiv_data()
        if arxiv_data:
            all_data.extend(arxiv_data)
        
        # Create plagiarized samples
        if all_data:
            plagiarized_data = self.create_plagiarized_samples(all_data)
            all_data.extend(plagiarized_data)
        
        # Save combined dataset
        output_file = self.output_dir / "combined_training_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== Processing Complete ===")
        print(f"Total documents processed: {len(all_data)}")
        print(f"Original documents: {len([d for d in all_data if d['type'] == 'original'])}")
        print(f"Plagiarized samples: {len([d for d in all_data if d['type'] == 'plagiarized'])}")
        print(f"Combined dataset saved to: {output_file}")
        
        return all_data

if __name__ == "__main__":
    preprocessor = DatasetPreprocessor()
    preprocessor.process_all_datasets()
