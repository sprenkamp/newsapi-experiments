#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Report Generator

This module converts the markdown report to a PDF document using a more reliable approach.
"""

import os
import subprocess
import tempfile
from datetime import datetime
from typing import Optional

# Simple HTML template for the report
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 40px;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #1a66c2;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #1a66c2;
            margin-top: 30px;
        }}
        h3 {{
            color: #333;
            margin-top: 25px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .title {{
            font-size: 28px;
            font-weight: bold;
        }}
        .subtitle {{
            font-size: 20px;
            color: #666;
            margin-top: 10px;
        }}
        .date {{
            font-size: 14px;
            color: #666;
            margin-top: 20px;
        }}
        .content {{
            margin-top: 30px;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
            padding-top: 10px;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        blockquote {{
            border-left: 4px solid #1a66c2;
            padding-left: 15px;
            margin-left: 0;
            color: #555;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">{title}</div>
        <div class="subtitle">Cybersecurity Intelligence Report</div>
        <div class="date">Generated on {date}</div>
    </div>
    
    <div class="content">
        {content}
    </div>
    
    <div class="footer">
        <p>Generated on {date} | Confidential</p>
    </div>
</body>
</html>
"""

def convert_markdown_to_html(markdown_text: str, title: str = "Cybersecurity Report") -> str:
    """Convert markdown to HTML with simple styling.
    
    Args:
        markdown_text: Markdown content of the report.
        title: Title of the report.
        
    Returns:
        HTML content.
    """
    try:
        # Use pandoc to convert markdown to HTML if available
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as temp_md:
            temp_md_path = temp_md.name
            temp_md.write(markdown_text)
        
        with tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.html') as temp_html:
            temp_html_path = temp_html.name
        
        try:
            subprocess.run(['pandoc', temp_md_path, '-o', temp_html_path], check=True)
            with open(temp_html_path, 'r') as f:
                html_content = f.read()
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fallback to simple conversion if pandoc isn't available
            print("Pandoc not available, using simple markdown to HTML conversion")
            html_content = simple_markdown_to_html(markdown_text)
    except Exception as e:
        print(f"Error converting markdown to HTML: {e}")
        html_content = f"<pre>{markdown_text}</pre>"  # Fallback to just showing the markdown
    finally:
        # Clean up temporary files
        if 'temp_md_path' in locals() and os.path.exists(temp_md_path):
            os.unlink(temp_md_path)
        if 'temp_html_path' in locals() and os.path.exists(temp_html_path):
            os.unlink(temp_html_path)
    
    # Format the date
    date = datetime.now().strftime("%B %d, %Y")
    
    # Insert the HTML content into the template
    full_html = HTML_TEMPLATE.format(
        title=title,
        date=date,
        content=html_content
    )
    
    return full_html

def simple_markdown_to_html(markdown_text: str) -> str:
    """Simple markdown to HTML conversion for basic formatting."""
    lines = markdown_text.split('\n')
    html_lines = []
    in_list = False
    in_code_block = False
    
    for line in lines:
        # Handle headers
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
        # Handle lists
        elif line.startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{line[2:]}</li>')
        # Handle code blocks
        elif line.startswith('```'):
            if in_code_block:
                html_lines.append('</pre>')
                in_code_block = False
            else:
                html_lines.append('<pre><code>')
                in_code_block = True
        # Handle paragraphs
        elif line.strip() == '':
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('<p></p>')
        # Regular text
        else:
            if in_code_block:
                html_lines.append(line)
            else:
                html_lines.append(f'<p>{line}</p>')
    
    # Close any open lists
    if in_list:
        html_lines.append('</ul>')
    
    # Close any open code blocks
    if in_code_block:
        html_lines.append('</pre>')
    
    return '\n'.join(html_lines)

def convert_html_to_pdf(html_content: str, output_path: str) -> Optional[str]:
    """Convert HTML to PDF using system tools (wkhtmltopdf or chrome headless)."""
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Write the HTML to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_html:
        temp_html_path = temp_html.name
        temp_html.write(html_content)
    
    try:
        # Try wkhtmltopdf
        try:
            subprocess.run(['wkhtmltopdf', temp_html_path, output_path], check=True)
            print(f"Generated PDF using wkhtmltopdf: {output_path}")
            return output_path
        except (subprocess.SubprocessError, FileNotFoundError):
            print("wkhtmltopdf not available, trying Google Chrome")
            
            # Try Chrome/Chromium headless
            try:
                for chrome_cmd in ['google-chrome', 'chrome', 'chromium', 'chromium-browser']:
                    try:
                        subprocess.run([
                            chrome_cmd,
                            '--headless',
                            '--disable-gpu',
                            f'--print-to-pdf={output_path}',
                            f'file://{os.path.abspath(temp_html_path)}'
                        ], check=True)
                        print(f"Generated PDF using {chrome_cmd}: {output_path}")
                        return output_path
                    except (subprocess.SubprocessError, FileNotFoundError):
                        continue
                
                # If we're here, Chrome/Chromium commands didn't work
                raise FileNotFoundError("Chrome/Chromium not found")
            
            except (subprocess.SubprocessError, FileNotFoundError):
                # Try using the built-in 'textutil' on macOS
                if os.path.exists('/usr/bin/textutil'):
                    print("Trying macOS textutil")
                    # Convert HTML to RTF first
                    rtf_path = output_path.replace('.pdf', '.rtf')
                    subprocess.run(['textutil', '-convert', 'rtf', '-output', rtf_path, temp_html_path], check=True)
                    
                    # Then convert RTF to PDF using automator or Preview
                    try:
                        # This is a simplified approach - not ideal but might work
                        subprocess.run(['automator', 'convert', rtf_path, 'to', 'PDF', 'saving', 'in', output_path], check=True)
                        os.unlink(rtf_path)  # Clean up the RTF file
                        return output_path
                    except (subprocess.SubprocessError, FileNotFoundError):
                        # Save as HTML and inform the user
                        html_output = output_path.replace('.pdf', '.html')
                        import shutil
                        shutil.copy2(temp_html_path, html_output)
                        print(f"Could not generate PDF. HTML saved to {html_output}")
                        return None
                else:
                    # Save as HTML and inform the user
                    html_output = output_path.replace('.pdf', '.html')
                    import shutil
                    shutil.copy2(temp_html_path, html_output)
                    print(f"Could not generate PDF. HTML saved to {html_output}")
                    return None
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
    
    finally:
        # Clean up the temporary HTML file
        if os.path.exists(temp_html_path):
            os.unlink(temp_html_path)

def convert_markdown_to_pdf(markdown_text: str, output_path: str, title: str = "Cybersecurity Report") -> Optional[str]:
    """Convert markdown report to PDF using available system tools.
    
    Args:
        markdown_text: Markdown content of the report.
        output_path: Path to save the PDF file.
        title: Title of the report.
        
    Returns:
        Path to the saved PDF file, or None if conversion failed.
    """
    try:
        # Try direct markdown to PDF conversion with pandoc if available
        try:
            # Create the output directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Create a temporary markdown file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_md:
                temp_md_path = temp_md.name
                temp_md.write(markdown_text)
            
            # Try pandoc with PDF output
            subprocess.run(['pandoc', temp_md_path, '-o', output_path], check=True)
            print(f"Generated PDF using pandoc: {output_path}")
            return output_path
        
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Pandoc PDF generation not available, trying HTML conversion first")
            
            # Convert to HTML then try to convert that to PDF
            html_content = convert_markdown_to_html(markdown_text, title)
            return convert_html_to_pdf(html_content, output_path)
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None