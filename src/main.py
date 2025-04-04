#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cybersecurity News Scraper for DACH Region

This script fetches cybersecurity news from NewsAPI for Germany, Austria, and Switzerland,
scrapes full article content, classifies relevance, and generates reports using OpenAI.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional

# Add the src directory to the Python path to properly resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.news_api import NewsAPIWrapper
from src.utils.config import load_config
from src.utils.data_processor import DataProcessor
from src.utils.article_scraper import ArticleScraper
from src.report.generator import generate_report, save_report, load_articles, get_latest_data_file


def parse_args():
    """Parse command line arguments.
    
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Cybersecurity News Scraper and Report Generator for DACH Region"
    )
    # News scraping arguments
    parser.add_argument(
        '--days', 
        type=int, 
        default=None,
        help="Number of days to look back for news (default: from .env or 7)"
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default=None,
        help="Output directory for saving results (default: from .env or 'data')"
    )
    parser.add_argument(
        '--limit', 
        type=int, 
        default=5,
        help="Number of articles to display in output (default: 5)"
    )
    
    # Report generation arguments
    parser.add_argument(
        '--report', 
        action='store_true',
        help="Generate a report after scraping news"
    )
    parser.add_argument(
        '--report-only', 
        action='store_true',
        help="Only generate a report using existing data (skip scraping)"
    )
    parser.add_argument(
        '--scrape-content',
        action='store_true',
        help="Scrape full article content and classify relevance"
    )
    parser.add_argument(
        '--max-scrape',
        type=int,
        default=None,
        help="Maximum number of articles to scrape content for (default: all)"
    )
    parser.add_argument(
        '--input', 
        type=str, 
        default=None,
        help="Path to the JSON file with articles for report generation (default: latest file in data directory)"
    )
    parser.add_argument(
        '--report-output', 
        type=str, 
        default="reports",
        help="Directory to save the report (default: 'reports')"
    )
    parser.add_argument(
        '--model',
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use for report generation (default: 'gpt-4o-mini')"
    )
    parser.add_argument(
        '--no-pdf',
        action='store_true',
        help="Disable PDF report generation"
    )
    
    return parser.parse_args()


def run_scraper(config: Dict[str, Any], display_limit: int = 5, 
            scrape_content: bool = False, max_scrape: int = None) -> Dict[str, str]:
    """Run the cybersecurity news scraper.
    
    Args:
        config: Configuration dictionary.
        display_limit: Number of articles to display.
        scrape_content: Whether to scrape full article content and classify relevance.
        max_scrape: Maximum number of articles to scrape content for.
        
    Returns:
        Dictionary with paths to saved files.
    """
    print(f"Searching for cybersecurity news from DACH region...")
    print(f"Looking back {config['days_back']} days")
    
    # Initialize NewsAPI wrapper
    news_api = NewsAPIWrapper(config['api_key'])
    
    # Get articles
    articles_data = news_api.get_all_cybersecurity_news(days_back=config['days_back'])
    print(f"Found {len(articles_data)} articles from the API")
    
    # Process articles
    processor = DataProcessor(output_dir=config['output_dir'])
    articles = processor.process_articles(articles_data)
    print(f"After processing, {len(articles)} unique articles remain")
    
    # Save initial articles
    output_paths = {}
    if articles:
        output_paths = processor.save_articles(articles)
        if output_paths:
            print(f"\nSaved initial results to:")
            for format_type, path in output_paths.items():
                print(f"- {format_type.upper()}: {path}")
    
        # Display articles
        processor.print_top_articles(articles, limit=display_limit)
    else:
        print("No articles found matching the criteria.")
        return output_paths
    
    # Scrape full article content and classify if requested
    if scrape_content and articles:
        print("\n" + "="*80)
        print("Starting article content scraping and relevance classification...")
        print("="*80)
        
        scraper = ArticleScraper()
        article_dicts = [article.to_dict() for article in articles]
        relevant_articles = scraper.process_articles(article_dicts, max_articles=max_scrape)
        
        if relevant_articles:
            # Save relevant articles
            relevant_path = scraper.save_processed_articles(
                relevant_articles, 
                output_dir=config['output_dir']
            )
            output_paths['relevant_json'] = relevant_path
            
            print(f"\nSaved {len(relevant_articles)} relevant articles to:")
            print(f"- RELEVANT JSON: {relevant_path}")
            
            # Display relevant articles
            print(f"\nTop {min(display_limit, len(relevant_articles))} relevant cybersecurity articles:")
            for i, article in enumerate(relevant_articles[:display_limit], 1):
                published = article.get('published_at', '')
                source = article.get('source_name', '')
                title = article.get('title', '')
                url = article.get('url', '')
                reason = article.get('relevance_reason', '')
                
                print(f"\n{i}. {title}")
                print(f"   Published: {published} by {source}")
                print(f"   Relevance: {reason}")
                print(f"   {url}")
        else:
            print("No relevant cybersecurity articles found after classification.")
    
    return output_paths


def run_report_generator(input_file: str = None, output_dir: str = "reports", 
                      model: str = "gpt-4o-mini", generate_pdf: bool = True) -> Optional[str]:
    """Run the report generator.
    
    Args:
        input_file: Path to the JSON file with articles.
        output_dir: Directory to save the report.
        model: OpenAI model to use.
        generate_pdf: Whether to generate a PDF version of the report.
        
    Returns:
        Path to the saved report file.
    """
    # Get input file path if not provided
    if not input_file:
        input_file = get_latest_data_file()
        if not input_file:
            return None
    
    print(f"Using data from: {input_file}")
    
    # Load articles
    articles = load_articles(input_file)
    print(f"Loaded {len(articles)} articles")
    
    # Generate report
    print(f"Generating report using {model}...")
    report = generate_report(articles, model_name=model)
    
    # Save report
    output_path = save_report(report, output_dir=output_dir, generate_pdf=generate_pdf)
    print(f"Report saved to: {output_path}")
    
    # Print the first few lines of the report
    print("\nReport Preview:")
    print("=" * 80)
    preview_lines = report.split('\n')[:15]  # First 15 lines
    print('\n'.join(preview_lines))
    print("..." if len(report.split('\n')) > 15 else "")
    print("=" * 80)
    print(f"\nFull report available at: {output_path}")
    
    return output_path


def main():
    """Main function."""
    # Parse arguments
    args = parse_args()
    
    # Load configuration for scraping
    config = load_config()
    
    # Override config with command line arguments if provided
    if args.days is not None:
        config['days_back'] = args.days
    
    if args.output is not None:
        config['output_dir'] = args.output
    
    # Always run the complete workflow by default
    scrape_content = True
    max_scrape = args.max_scrape if args.max_scrape is not None else None
    
    # Run scraper
    output_paths = run_scraper(
        config, 
        display_limit=args.limit,
        scrape_content=scrape_content,
        max_scrape=max_scrape
    )
    
    # Always generate report 
    if output_paths:
        # Use relevant articles JSON if available, otherwise use regular JSON
        input_file = output_paths.get('relevant_json') or output_paths.get('json')
        if input_file:
            run_report_generator(
                input_file=input_file,
                output_dir=args.report_output,
                model=args.model,
                generate_pdf=True  # Enable PDF generation
            )


if __name__ == "__main__":
    main()