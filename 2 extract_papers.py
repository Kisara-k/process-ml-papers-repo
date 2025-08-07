"""
Extract paper data from papers.md into TSV format.
"""

import re
import csv
import sys
from pathlib import Path


def parse_markdown_papers(content):
    """
    Parse the markdown content and extract paper information.
    
    Returns a list of dictionaries with:
    - Heading: The h2 heading text
    - Paper: The paper title/description
    - All link types found dynamically (e.g., Paper-Link, Tweet-Link, Code-Link, etc.)
    """
    import json
    papers = []
    # Split content by h2 headings (lines starting with ##)
    sections = re.split(r'^## (.+?)$', content, flags=re.MULTILINE)
    for i in range(1, len(sections), 2):
        if i + 1 >= len(sections):
            break
        heading = sections[i].strip()
        section_content = sections[i + 1].strip()
        if '| **Paper**' not in section_content:
            continue
        table_lines = [line.strip() for line in section_content.split('\n')
                      if line.strip().startswith('|') and not line.strip().startswith('| **Paper**')
                      and not line.strip().startswith('| ---')]
        for line in table_lines:
            if '**Paper**' in line or '---' in line:
                continue
            columns = [col.strip() for col in line.split('|')]
            if len(columns) < 3:
                continue
            paper_column = columns[1] if len(columns) > 1 else ""
            links_column = columns[2] if len(columns) > 2 else ""
            if not paper_column.strip() or not links_column.strip():
                continue
            paper_match = re.search(r'^\d+\)\s*\*\*(.*?)\*\*', paper_column)
            if paper_match:
                paper_title = paper_match.group(1).strip()
            else:
                paper_title = re.sub(r'^\d+\)\s*', '', paper_column).strip()
                paper_title = re.split(r'\s+[-–—]\s+', paper_title)[0]
                paper_title = re.sub(r'\*\*(.*?)\*\*', r'\1', paper_title)
                paper_title = paper_title.strip()
            paper_entry = {
                'Heading': heading,
                'Paper': paper_title,
                'Paper-Link': '',
                'Tweet-Link': '',
                'Other-Links': ''
            }
            link_matches = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', links_column)
            other_links = {}
            for link_type, url in link_matches:
                if link_type == 'Paper':
                    paper_entry['Paper-Link'] = url
                elif link_type == 'Tweet':
                    paper_entry['Tweet-Link'] = url
                else:
                    other_links[link_type] = url
            if other_links:
                paper_entry['Other-Links'] = json.dumps(other_links, ensure_ascii=False)
            if paper_title:
                papers.append(paper_entry)
    return papers, ['Paper-Link', 'Tweet-Link', 'Other-Links']


def main():
    """Main function to read papers.md and create TSV output."""
    
    # Read the papers.md file
    papers_path = Path('papers.md')
    if not papers_path.exists():
        print("ERROR: papers.md not found in current directory")
        sys.exit(1)
    
    try:
        with open(papers_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: Could not read papers.md: {e}")
        sys.exit(1)
    
    # Parse the content
    papers, link_types = parse_markdown_papers(content)
    
    if not papers:
        print("WARNING: No papers found in papers.md")
        return
    
    # Create field names for TSV (Heading, Paper, Paper-Link, Tweet-Link, Other-Links)
    fieldnames = ['Heading', 'Paper'] + link_types
    
    # Write to TSV file
    output_path = Path('papers.tsv')
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(papers)
        
        print(f"SUCCESS: Extracted {len(papers)} papers to {output_path}")
        print(f"Found link types: {', '.join(link_types)}")
        
        # Print first few entries as a preview
        print("\nPreview of extracted data:")
        print("Heading\tPaper\t" + "\t".join(link_types))
        print("-" * 80)
        for i, paper in enumerate(papers[:3]):
            row_parts = [
                paper['Heading'][:30] + "..." if len(paper['Heading']) > 30 else paper['Heading'],
                paper['Paper'][:40] + "..." if len(paper['Paper']) > 40 else paper['Paper']
            ]
            for link_type in link_types:
                link_val = paper.get(link_type, "")
                row_parts.append(link_val[:30] + "..." if len(link_val) > 30 else link_val)
            print("\t".join(row_parts))
        
        if len(papers) > 3:
            print(f"... and {len(papers) - 3} more entries")
            
    except Exception as e:
        print(f"ERROR: Could not write to {output_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
