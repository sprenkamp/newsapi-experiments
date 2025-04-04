# NewsAPI Experiments

A Python tool for scraping cybersecurity news from DACH region (Germany, Austria, Switzerland) using NewsAPI, classifying relevance, and generating reports with OpenAI.

## Features

- Fetches cybersecurity news from NewsAPI for DACH region
- Uses multiple endpoints to maximize coverage
- Filters news by cybersecurity-related keywords
- Scrapes full article content from source websites
- Uses OpenAI to classify article relevance to cybersecurity in DACH
- Generates comprehensive reports using relevant articles
- Exports results to CSV and JSON

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure you have a `.env` file with your API keys:
   ```
   NEWS_API_KEY=your_newsapi_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```

## Usage

Run the main script:

```bash
python src/main.py
```

### Command-line arguments

#### Scraping News
- `--days`: Number of days to look back for news (default: 7)
- `--output`: Output directory for saving results (default: 'data')
- `--limit`: Number of articles to display in output (default: 5)

#### Content Scraping and Classification
- `--scrape-content`: Scrape full article content and classify relevance
- `--max-scrape`: Maximum number of articles to scrape content for (default: all)

#### Report Generation
- `--report`: Generate a report after scraping news
- `--report-only`: Only generate a report using existing data (skip scraping)
- `--input`: Path to the JSON file with articles for report generation (default: latest file in data directory)
- `--report-output`: Directory to save the report (default: 'reports')
- `--model`: OpenAI model to use for report generation (default: 'gpt-4o-mini')

### Examples

```bash
# Basic news scraping
python src/main.py

# Scrape news, fetch content, and classify relevance
python src/main.py --scrape-content

# Scrape news, classify relevance, and generate a report
python src/main.py --scrape-content --report

# Only generate a report from existing data
python src/main.py --report-only

# Use a different OpenAI model
python src/main.py --report-only --model gpt-4

# Limit the number of articles to scrape content for
python src/main.py --scrape-content --max-scrape 10
```

## Output

The scraper generates several files:
- `cybersecurity_news_TIMESTAMP.csv`: CSV file with all articles
- `cybersecurity_news_TIMESTAMP.json`: JSON file with all articles
- `cybersecurity_relevant_articles_TIMESTAMP.json`: JSON file with articles classified as relevant

The report generator creates:
- `cybersecurity_report_TIMESTAMP.md`: Comprehensive report about relevant cybersecurity incidents

## How It Works

1. **Data Collection**: The system queries the NewsAPI for cybersecurity-related news in the DACH region.
2. **Initial Processing**: It removes duplicates and formats article metadata.
3. **Content Scraping**: For each article, it visits the source URL and extracts the full article content.
4. **Relevance Classification**: OpenAI analyzes each article to determine if it's actually relevant to cybersecurity in the DACH region.
5. **Report Generation**: Using only the relevant articles, it generates a comprehensive cybersecurity report with executive summary, major incidents, emerging threats, industry impact, and recommendations.