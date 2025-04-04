#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Article data model for NewsAPI responses.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List


class Article:
    """Data model for a news article."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize article from NewsAPI data.
        
        Args:
            data: Raw article data from NewsAPI.
        """
        self.source_name = data.get('source', {}).get('name', '')
        self.author = data.get('author', '')
        self.title = data.get('title', '')
        self.description = data.get('description', '')
        self.url = data.get('url', '')
        self.url_to_image = data.get('urlToImage', '')
        self.published_at = self._parse_date(data.get('publishedAt', ''))
        self.content = data.get('content', '')
        self.country = data.get('country', '')
        self.api_endpoint = data.get('api_endpoint', '')
        
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object.
        
        Args:
            date_str: Date string from NewsAPI.
            
        Returns:
            Datetime object or None if parsing fails.
        """
        if not date_str:
            return None
            
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            try:
                return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
            except (ValueError, TypeError):
                return None
    
    @classmethod
    def from_api_response(cls, articles_data: List[Dict[str, Any]]) -> List['Article']:
        """Create a list of Article objects from NewsAPI response.
        
        Args:
            articles_data: List of article dictionaries from NewsAPI.
            
        Returns:
            List of Article objects.
        """
        return [cls(article) for article in articles_data]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Article to dictionary.
        
        Returns:
            Dictionary representation of the article.
        """
        return {
            'source_name': self.source_name,
            'author': self.author,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'url_to_image': self.url_to_image,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'content': self.content,
            'country': self.country,
            'api_endpoint': self.api_endpoint,
        }
    
    def __str__(self) -> str:
        """String representation of the article.
        
        Returns:
            Formatted article string.
        """
        published = self.published_at.strftime('%Y-%m-%d %H:%M') if self.published_at else 'Unknown date'
        return f"{self.title}\n{published} | {self.source_name}\n{self.url}"