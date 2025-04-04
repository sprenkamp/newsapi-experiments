#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data processing utilities for news articles.
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

# Add the src directory to the Python path to properly resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Article class directly (avoiding pandas import issues)
from src.models.article import Article


class DataProcessor:
    """Processor for news article data."""
    
    def __init__(self, output_dir: str = 'data'):
        """Initialize the data processor.
        
        Args:
            output_dir: Directory to save outputs.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process_articles(self, articles_data: List[Dict[str, Any]]) -> List[Article]:
        """Process raw article data into Article objects.
        
        Args:
            articles_data: Raw articles data from NewsAPI.
            
        Returns:
            List of Article objects.
        """
        # Convert to Article objects
        articles = Article.from_api_response(articles_data)
        
        # Remove duplicates based on URL
        unique_urls = set()
        unique_articles = []
        
        for article in articles:
            if article.url and article.url not in unique_urls:
                unique_urls.add(article.url)
                unique_articles.append(article)
                
        # Sort by published date (newest first)
        unique_articles.sort(
            key=lambda x: x.published_at if x.published_at else datetime.min, 
            reverse=True
        )
        
        return unique_articles
    
    def save_articles(self, articles: List[Article]) -> Dict[str, str]:
        """Save articles to JSON (and CSV if pandas is available).
        
        Args:
            articles: List of articles to save.
            
        Returns:
            Dictionary with paths to saved files.
        """
        if not articles:
            print("No articles to save.")
            return {}
            
        # Create timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f'cybersecurity_news_{timestamp}'
        
        # Save paths
        json_path = os.path.join(self.output_dir, f'{filename_base}.json')
        csv_path = os.path.join(self.output_dir, f'{filename_base}.csv')
        
        # Save to JSON (using list of dicts to maintain format)
        articles_dicts = [article.to_dict() for article in articles]
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(articles_dicts, f, ensure_ascii=False, indent=4)
        
        output_paths = {'json': json_path}
        
        # Try to save as CSV if pandas is available
        try:
            import pandas as pd
            # Convert to DataFrame
            df = pd.DataFrame(articles_dicts)
            # Save to CSV
            df.to_csv(csv_path, index=False, encoding='utf-8')
            output_paths['csv'] = csv_path
        except (ImportError, ValueError, Exception) as e:
            print(f"Warning: Could not save CSV due to pandas issue: {e}")
            print("Only JSON output will be available.")
            
        return output_paths
    
    def print_top_articles(self, articles: List[Article], limit: int = 5) -> None:
        """Print top articles in a readable format.
        
        Args:
            articles: List of Article objects.
            limit: Number of articles to print.
        """
        if not articles:
            print("No articles to display.")
            return
            
        print(f"\nTop {min(limit, len(articles))} recent cybersecurity news articles:")
        
        for i, article in enumerate(articles[:limit], 1):
            published = article.published_at.strftime('%Y-%m-%d %H:%M') if article.published_at else 'Unknown date'
            
            print(f"\n{i}. {article.title}")
            print(f"   Published: {published} by {article.source_name}")
            if article.description:
                print(f"   {article.description[:100]}..." if len(article.description) > 100 else f"   {article.description}")
            print(f"   {article.url}")