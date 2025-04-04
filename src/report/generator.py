#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cybersecurity Report Generator

This module takes NewsAPI data about cybersecurity incidents and uses OpenAI via LangChain
to generate a comprehensive report about the incidents.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Make sure OpenAI API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not found in environment variables.")
    print("Please add OPENAI_API_KEY to your .env file.")


def load_articles(file_path: str) -> List[Dict[str, Any]]:
    """Load articles from JSON file.
    
    Args:
        file_path: Path to the JSON file.
        
    Returns:
        List of article dictionaries.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        exit(1)
        
    with open(file_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    return articles


def get_latest_data_file(data_dir: str = "data", file_type: str = "json") -> Optional[str]:
    """Get the path to the most recent data file.
    
    Args:
        data_dir: Directory containing data files.
        file_type: File extension to look for.
        
    Returns:
        Path to the most recent file, or None if no files found.
    """
    if not os.path.exists(data_dir):
        print(f"Error: Directory {data_dir} not found.")
        return None
    
    # Get all files with the specified extension
    files = [f for f in os.listdir(data_dir) if f.endswith(f".{file_type}")]
    
    if not files:
        print(f"Error: No {file_type} files found in {data_dir}.")
        return None
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(data_dir, x)), reverse=True)
    
    return os.path.join(data_dir, files[0])


def generate_report(articles: List[Dict[str, Any]], model_name: str = "gpt-4o-mini") -> str:
    """Generate a cybersecurity report from articles using OpenAI.
    
    Args:
        articles: List of article dictionaries.
        model_name: OpenAI model to use.
        
    Returns:
        Generated report text.
    """
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not available. Cannot generate report."
        
    # Prepare a concise version of the articles for context
    article_summaries = []
    for i, article in enumerate(articles[:30], 1):  # Limit to top 30 articles
        published = article.get('published_at', '')
        source = article.get('source_name', '')
        title = article.get('title', '')
        description = article.get('description', '')
        url = article.get('url', '')
        
        # Include content excerpt if available (from scraping)
        content_excerpt = ""
        if article.get('content'):
            content = article['content']
            content_excerpt = f"\n   Content: {content[:200]}..." if len(content) > 200 else f"\n   Content: {content}"
        
        article_summaries.append(f"{i}. {title}\n   Published: {published} by {source}\n   {description}{content_excerpt}\n   URL: {url}\n")
    
    article_context = "\n".join(article_summaries)
    
    # Create a prompt template
    prompt_template = """
    You are a cybersecurity analyst tasked with creating a comprehensive report about recent cybersecurity incidents and trends in the DACH region (Germany, Austria, Switzerland).

    Below are recent news articles about cybersecurity from the DACH region:
    
    {article_context}
    
    Based on these articles, create a comprehensive cybersecurity report with the following sections:
    
    1. Executive Summary - A brief overview of the key findings and trends
    2. Major Incidents - Detailed analysis of significant cybersecurity incidents
    3. Emerging Threats - New and evolving cybersecurity threats in the region
    4. Industry Impact - How these incidents affect different industries
    5. Recommendations - Practical advice for organizations to protect themselves
    
    Use a professional, analytical tone. The report should be well-structured with clear headings and organized content.
    Focus on extracting valuable insights and patterns from the provided news articles.
    
    REPORT:
    """

    # Create prompt from template
    prompt = PromptTemplate.from_template(prompt_template)
    
    try:
        # Initialize the OpenAI model
        llm = ChatOpenAI(model=model_name, temperature=0.3, api_key=OPENAI_API_KEY)
        
        # Create a chain
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Generate the report
        report = chain.run(article_context=article_context)
        
        return report
    except Exception as e:
        print(f"Error generating report: {e}")
        return f"Error generating report: {str(e)}"


def save_report(report: str, output_dir: str = "reports", generate_pdf: bool = True) -> str:
    """Save the generated report to PDF file, using markdown as an intermediate format.
    
    Args:
        report: Report text.
        output_dir: Directory to save the report.
        generate_pdf: Whether to generate a PDF version.
        
    Returns:
        Path to the saved PDF file (or markdown if PDF generation fails).
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Only save markdown to a temporary location if we're going to use it for PDF
    if generate_pdf:
        try:
            from src.report.pdf_generator import convert_markdown_to_pdf
            
            pdf_filename = f"cybersecurity_report_{timestamp}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            pdf_result = convert_markdown_to_pdf(
                report, 
                pdf_path, 
                title="Cybersecurity Intelligence Report"
            )
            
            if pdf_result:
                print(f"PDF report generated successfully: {pdf_path}")
                return pdf_path
            else:
                print(f"Failed to generate PDF report, falling back to markdown")
                # Fall back to markdown if PDF generation fails
        except ImportError as e:
            print(f"PDF generation skipped: {str(e)}")
            print("Install weasyprint, markdown, and jinja2 to enable PDF generation")
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
    
    # Save markdown if PDF generation is disabled or failed
    md_filename = f"cybersecurity_report_{timestamp}.md"
    md_path = os.path.join(output_dir, md_filename)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return md_path