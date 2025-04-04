#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NewsAPI client wrapper for cybersecurity news in DACH region.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from newsapi import NewsApiClient


class NewsAPIWrapper:
    """Wrapper for NewsAPI client with cybersecurity specific functionality."""
    
    def __init__(self, api_key: str):
        """Initialize the NewsAPI client.
        
        Args:
            api_key: NewsAPI key.
        """
        self.api = NewsApiClient(api_key=api_key)
        self.dach_countries = ['de', 'at', 'ch']  # Germany, Austria, Switzerland
        self.cybersecurity_keywords = [
            'cybersecurity', 'cyber security', 'cyber-security',
            'hack', 'hacking', 'data breach', 'ransomware', 'malware',
            'phishing', 'cyber attack', 'cyber-attack', 'cyberangriff',
            'datenschutz', 'datenleck', 'cyberkriminalität', 'it-sicherheit',
            'datensicherheit', 'hackerangriff'
        ]
        
    def get_query_string(self) -> str:
        """Create a query string from keywords.
        
        Returns:
            Query string for NewsAPI.
        """
        return ' OR '.join(f'"{kw}"' for kw in self.cybersecurity_keywords)
    
    def get_dach_top_headlines(self) -> List[Dict[str, Any]]:
        """Get top cybersecurity headlines from DACH countries.
        
        Returns:
            List of articles.
        """
        all_articles = []
        query = self.get_query_string()
        
        for country in self.dach_countries:
            try:
                top_headlines = self.api.get_top_headlines(
                    q=query,
                    country=country,
                    category='technology',
                    language='de' if country in ['de', 'at', 'ch'] else 'en',
                    page_size=100
                )
                
                if top_headlines['status'] == 'ok':
                    articles = top_headlines['articles']
                    for article in articles:
                        article['country'] = country
                    all_articles.extend(articles)
                else:
                    print(f"Error fetching top headlines for {country}: {top_headlines}")
            except Exception as e:
                print(f"Exception when fetching news for {country}: {e}")
                continue
                
        return all_articles
    
    def get_dach_everything(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get all cybersecurity news from DACH sources.
        
        Args:
            days_back: Number of days to look back.
            
        Returns:
            List of articles.
        """
        query = self.get_query_string()
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            dach_domains = 'spiegel.de,faz.net,zeit.de,nzz.ch,derstandard.at,heise.de,golem.de,welt.de,sueddeutsche.de,diepresse.com,tagesanzeiger.ch'
            all_news = self.api.get_everything(
                q=query,
                domains=dach_domains,
                from_param=from_date,
                to=to_date,
                language='de',
                sort_by='relevancy',
                page_size=100
            )
            
            if all_news['status'] == 'ok':
                return all_news['articles']
            else:
                print(f"Error fetching all news: {all_news}")
                return []
        except Exception as e:
            print(f"Exception when fetching all news: {e}")
            return []
            
    def get_all_cybersecurity_news(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get all cybersecurity news from both top headlines and everything endpoint.
        
        Args:
            days_back: Number of days to look back for the everything endpoint.
            
        Returns:
            Combined list of articles.
        """
        top_headlines = self.get_dach_top_headlines()
        everything = self.get_dach_everything(days_back=days_back)
        
        # Mark the source of each article
        for article in top_headlines:
            article['api_endpoint'] = 'top-headlines'
        
        for article in everything:
            article['api_endpoint'] = 'everything'
            
        return top_headlines + everything
