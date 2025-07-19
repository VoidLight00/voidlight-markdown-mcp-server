"""
Text formatting and processing utilities
"""

import re
import html
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def clean_html(html_content: str) -> str:
    """Clean and normalize HTML content"""
    if not html_content:
        return ""
    
    # Decode HTML entities
    html_content = html.unescape(html_content)
    
    # Remove script and style tags
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    html_content = re.sub(r'<[^>]+>', '', html_content)
    
    # Normalize whitespace
    html_content = re.sub(r'\s+', ' ', html_content)
    
    return html_content.strip()


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text"""
    if not text:
        return ""
    
    # Convert multiple spaces/tabs to single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Limit consecutive newlines to maximum of 2
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Strip leading and trailing whitespace
    text = text.strip()
    
    return text


def extract_title_from_content(content: str, max_length: int = 100) -> Optional[str]:
    """Extract title from content"""
    if not content:
        return None
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if line and len(line) <= max_length:
            # Remove markdown heading markers
            line = re.sub(r'^#+\s*', '', line)
            
            # Remove special characters
            line = re.sub(r'[^\w\s가-힣]', '', line)
            
            if line:
                return line
    
    return None


def format_metadata_table(metadata: Dict[str, Any]) -> str:
    """Format metadata as markdown table"""
    if not metadata:
        return ""
    
    table = "| 항목 | 값 |\n|------|-----|\n"
    
    for key, value in metadata.items():
        # Translate keys to Korean
        key_korean = {
            'filename': '파일명',
            'file_size': '파일 크기',
            'mimetype': 'MIME 타입',
            'author': '작성자',
            'title': '제목',
            'subject': '주제',
            'creation_date': '생성일',
            'modification_date': '수정일',
            'language': '언어',
            'page_count': '페이지 수',
            'word_count': '단어 수'
        }.get(key, key)
        
        # Format values
        if isinstance(value, (int, float)):
            if key == 'file_size':
                value = format_file_size(value)
            elif key in ['creation_date', 'modification_date']:
                value = format_timestamp(value)
        
        table += f"| {key_korean} | {value} |\n"
    
    return table


def format_file_size(size: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def format_timestamp(timestamp: float) -> str:
    """Format timestamp as readable date"""
    try:
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(timestamp)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing unsafe characters"""
    # Remove unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Strip leading and trailing underscores
    filename = filename.strip('_')
    
    return filename


def is_korean_text(text: str, threshold: float = 0.3) -> bool:
    """Check if text contains Korean characters above threshold"""
    if not text:
        return False
    
    korean_chars = len(re.findall(r'[가-힣]', text))
    total_chars = len(re.findall(r'[가-힣a-zA-Z]', text))
    
    if total_chars == 0:
        return False
    
    return (korean_chars / total_chars) >= threshold


def normalize_korean_spacing(text: str) -> str:
    """Normalize Korean text spacing"""
    if not text:
        return text
    
    # Korean particles that shouldn't have space before them
    particles = ['은', '는', '이', '가', '을', '를', '에', '에서', '으로', '로', 
                '와', '과', '의', '도', '만', '까지', '부터', '마저', '조차']
    
    for particle in particles:
        text = re.sub(rf'\s+{particle}\b', particle, text)
    
    # Remove space before punctuation
    text = re.sub(r'\s+([.!?,:;])', r'\1', text)
    
    # Clean parentheses spacing
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    
    # Clean number-unit spacing
    text = re.sub(r'(\d+)\s*(개|명|번|회|시|분|초|일|월|년|kg|g|km|m|cm)', r'\1\2', text)
    
    return text


def escape_markdown_special_chars(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|']
    
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    
    return text


def create_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Create markdown table from headers and rows"""
    if not headers or not rows:
        return ""
    
    # Header row
    table = "| " + " | ".join(headers) + " |\n"
    
    # Separator row
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    # Data rows
    for row in rows:
        # Adjust row length to match headers
        row_data = list(row)[:len(headers)]
        row_data.extend([""] * (len(headers) - len(row_data)))
        
        table += "| " + " | ".join(str(cell) for cell in row_data) + " |\n"
    
    return table


def extract_text_from_markdown(markdown: str) -> str:
    """Extract plain text from markdown"""
    if not markdown:
        return ""
    
    # Remove code blocks
    markdown = re.sub(r'```[^`]*```', '', markdown, flags=re.DOTALL)
    
    # Remove inline code
    markdown = re.sub(r'`[^`]*`', '', markdown)
    
    # Remove links (keep text)
    markdown = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', markdown)
    
    # Remove images
    markdown = re.sub(r'!\[([^\]]*)\]\([^\)]*\)', r'\1', markdown)
    
    # Remove heading markers
    markdown = re.sub(r'^#+\s*', '', markdown, flags=re.MULTILINE)
    
    # Remove bold/italic
    markdown = re.sub(r'\*\*([^\*]*)\*\*', r'\1', markdown)
    markdown = re.sub(r'\*([^\*]*)\*', r'\1', markdown)
    markdown = re.sub(r'__([^_]*)__', r'\1', markdown)
    markdown = re.sub(r'_([^_]*)_', r'\1', markdown)
    
    # Remove list markers
    markdown = re.sub(r'^\s*[*+-]\s*', '', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'^\s*\d+\.\s*', '', markdown, flags=re.MULTILINE)
    
    # Remove blockquotes
    markdown = re.sub(r'^\s*>\s*', '', markdown, flags=re.MULTILINE)
    
    # Normalize whitespace
    markdown = normalize_whitespace(markdown)
    
    return markdown