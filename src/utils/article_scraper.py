#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Article content scraper.

This module scrapes the full content of articles from their URLs
and uses OpenAI to classify if they're relevant to cybersecurity in the DACH region.
"""

import os
import time
import json
import random
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Make sure OpenAI API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables.")
    print("Article classification will not work without an OpenAI API key.")


class ArticleScraper:
    """Scraper for article content and classifier for relevance."""
    
    def __init__(self, user_agent: str = None):
        """Initialize the article scraper.
        
        Args:
            user_agent: User agent to use for requests. If None, a default one is used.
        """
        self.user_agent = user_agent or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        
        # Create a session for requests
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9,de;q=0.8"
        })
    
    def scrape_article_content(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Scrape the content of an article from its URL.
        
        Args:
            url: URL of the article.
            max_retries: Maximum number of retries if the request fails.
            
        Returns:
            Article content as string, or None if scraping failed.
        """
        if not url or not url.startswith(('http://', 'https://')):
            return None
            
        domain = urlparse(url).netloc
        
        # Add a small random delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        # Try to get the article content
        retries = 0
        while retries < max_retries:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()  # Raise exception for 4XX/5XX responses
                
                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Extract text based on domain-specific rules
                content = self._extract_content_by_domain(soup, domain)
                
                # If domain-specific extraction failed, use a generic approach
                if not content or len(content.strip()) < 100:
                    # Get all text
                    content = soup.get_text(separator=' ', strip=True)
                
                # Clean up the content
                content = self._clean_content(content)
                
                return content
                
            except requests.exceptions.RequestException as e:
                print(f"Error scraping {url}: {e}")
                retries += 1
                time.sleep(random.uniform(2, 5))  # Increasing backoff
        
        return None
    
    def _extract_content_by_domain(self, soup: BeautifulSoup, domain: str) -> Optional[str]:
        """Extract content based on domain-specific rules.
        
        Args:
            soup: BeautifulSoup object.
            domain: Domain of the article.
            
        Returns:
            Article content as string, or None if extraction failed.
        """
        content = ""
        
        # DACH news sites common patterns
        if "heise.de" in domain:
            article = soup.find("article") or soup.find("div", class_="article-content")
            if article:
                content = article.get_text(separator=' ', strip=True)
        
        elif "zeit.de" in domain:
            article = soup.find("div", class_="article-body") or soup.find("div", class_="summary")
            if article:
                content = article.get_text(separator=' ', strip=True)
        
        elif "spiegel.de" in domain:
            article = soup.find("div", class_="RichText") or soup.find("div", attrs={"data-area": "body"})
            if article:
                content = article.get_text(separator=' ', strip=True)
        
        elif "golem.de" in domain:
            article = soup.find("div", class_="formatted") or soup.find("article")
            if article:
                content = article.get_text(separator=' ', strip=True)
        
        elif "faz.net" in domain:
            article = soup.find("div", class_="atc-Text") or soup.find("div", class_="art_txt")
            if article:
                content = article.get_text(separator=' ', strip=True)
        
        elif "nzz.ch" in domain:
            article = soup.find("div", class_="articlecomponent") or soup.find("div", class_="content-body")
            if article:
                content = article.get_text(separator=' ', strip=True)
        
        elif "derstandard.at" in domain:
            article = soup.find("div", class_="article-body")
            if article:
                content = article.get_text(separator=' ', strip=True)
                
        # Generic extraction for other domains
        if not content:
            # Try common article selectors
            for selector in ["article", ".article", ".post", ".content", "main", "#main", ".main-content", ".entry-content"]:
                article = soup.select_one(selector)
                if article:
                    content = article.get_text(separator=' ', strip=True)
                    if len(content) > 300:  # Only use if content is substantial
                        break
        
        return content if content else None
    
    def _clean_content(self, content: str) -> str:
        """Clean the article content.
        
        Args:
            content: Raw article content.
            
        Returns:
            Cleaned article content.
        """
        # Replace multiple spaces with a single space
        content = ' '.join(content.split())
        
        # Replace multiple newlines with a single newline
        content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
        
        # Truncate if too long (to fit in OpenAI context)
        if len(content) > 15000:
            content = content[:15000] + "..."
        
        return content
    
    def classify_article_relevance(self, article: Dict[str, Any]) -> Tuple[bool, str]:
        """Classify if an article is relevant to cybersecurity in the DACH region.
        
        Args:
            article: Article dictionary including content.
            
        Returns:
            Tuple of (is_relevant, reason).
        """
        if not self.openai_client:
            print("Error: OpenAI client not available. Cannot classify article relevance.")
            return True, "OpenAI classification not available, including by default."
        
        # Prepare article info
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        
        # Create prompt
        prompt = f"""Analyze this news article to determine if it is relevant to cybersecurity in the DACH region (Germany, Austria, Switzerland).

Title: {title}

Description: {description}

Content excerpt:
{content[:4000] if content else "[No content available]"}

Questions to answer:
1. Is this article related to cybersecurity, information security, or digital security?
2. Is this article relevant to the DACH region (Germany, Austria, Switzerland)?

Based on your analysis, classify this article as either:
- RELEVANT: The article is about cybersecurity AND involves the DACH region
- NOT RELEVANT: The article is not about cybersecurity OR does not involve the DACH region

Provide your answer in this exact format:
Classification: [RELEVANT or NOT RELEVANT]
Reason: [1-2 sentence explanation for your decision]
"""

        try:
            # Make API call
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity analyst specializing in the DACH region."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            # Extract response
            result = response.choices[0].message.content.strip()
            
            # Parse the response
            classification_line = [line for line in result.split('\n') if line.strip().startswith('Classification:')]
            reason_line = [line for line in result.split('\n') if line.strip().startswith('Reason:')]
            
            is_relevant = False
            reason = "Classification failed"
            
            if classification_line:
                classification = classification_line[0].split(':', 1)[1].strip()
                is_relevant = "RELEVANT" in classification.upper()
            
            if reason_line:
                reason = reason_line[0].split(':', 1)[1].strip()
            
            return is_relevant, reason
            
        except Exception as e:
            print(f"Error classifying article: {e}")
            return True, f"Classification error: {str(e)}"
    
    def process_articles(self, articles: List[Dict[str, Any]], max_articles: int = None) -> List[Dict[str, Any]]:
        """Process articles by scraping content and classifying relevance.
        
        Args:
            articles: List of article dictionaries.
            max_articles: Maximum number of articles to process.
            
        Returns:
            List of processed articles.
        """
        processed_articles = []
        total = len(articles)
        
        if max_articles:
            articles = articles[:max_articles]
            
        print(f"Processing {len(articles)} articles (out of {total})...")
        
        for i, article in enumerate(articles):
            url = article.get('url', '')
            print(f"[{i+1}/{len(articles)}] Processing: {url}")
            
            # Skip articles without a URL
            if not url:
                continue
            
            # Scrape content
            content = self.scrape_article_content(url)
            if content:
                article['content'] = content
                article['content_length'] = len(content)
                print(f"  - Content scraped: {len(content)} characters")
                
                # Classify relevance
                is_relevant, reason = self.classify_article_relevance(article)
                article['is_cybersecurity_relevant'] = is_relevant
                article['relevance_reason'] = reason
                
                if is_relevant:
                    processed_articles.append(article)
                    print(f"  - RELEVANT ✓ - {reason}")
                else:
                    print(f"  - NOT RELEVANT ✗ - {reason}")
            else:
                print(f"  - Failed to scrape content")
        
        print(f"\nClassification complete: {len(processed_articles)} relevant articles identified out of {len(articles)} processed.")
        return processed_articles
    
    def save_processed_articles(self, articles: List[Dict[str, Any]], output_dir: str = "data") -> str:
        """Save processed articles to a JSON file.
        
        Args:
            articles: List of processed article dictionaries.
            output_dir: Directory to save the file.
            
        Returns:
            Path to the saved file.
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cybersecurity_relevant_articles_{timestamp}.json"
        file_path = os.path.join(output_dir, filename)
        
        # Save to JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        
        return file_path