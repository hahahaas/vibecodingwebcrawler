import trafilatura
import time
import logging
from pathlib import Path
from typing import Optional, Dict, List
import re
from bs4 import BeautifulSoup
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_website_text_content(self, url: str, max_retries: int = 3) -> Optional[str]:
        """
        Get text content from a website with retry mechanism
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Starting to scrape URL: {url}")
                downloaded = trafilatura.fetch_url(url, headers=self.headers)
                if downloaded:
                    text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
                    if text:
                        return text
                logger.warning(f"Attempt {attempt + 1} failed: No content extracted from {url}")
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                wait_time = attempt + 1
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        return None

    def get_text_preview(self, text: str, max_length: int = 1000) -> str:
        """
        Get a preview of the text content
        """
        if not text:
            return "No content available"
        return text[:max_length] + "..." if len(text) > max_length else text

    def save_text_to_file(self, text: str, filename: str = None) -> str:
        """
        Save text content to a file
        """
        if not text:
            return "No content to save"
        
        if not filename:
            filename = f"scraped_content_{int(time.time())}.txt"
        
        output_dir = Path("scraped_content")
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        return str(file_path)

    def scrape_list_items(self, url: str, list_selector: str = None) -> List[Dict[str, str]]:
        """
        Scrape list items from a webpage
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = []
            
            # If no specific selector is provided, try to find common list patterns
            if not list_selector:
                # Look for common list containers
                list_containers = soup.find_all(['ul', 'ol', 'div'], class_=re.compile(r'list|items|products|projects'))
                
                for container in list_containers:
                    list_items = container.find_all('li')
                    for item in list_items:
                        item_text = item.get_text().strip()
                        if item_text:  # Only add non-empty items
                            items.append({
                                'name': item_text,
                                'source': url,
                                'url': url
                            })
            else:
                # Use the provided selector
                list_items = soup.select(list_selector)
                for item in list_items:
                    item_text = item.get_text().strip()
                    if item_text:
                        items.append({
                            'name': item_text,
                            'source': url,
                            'url': url
                        })
            
            return items
            
        except Exception as e:
            logger.error(f"Error scraping list items: {str(e)}")
            return []

    def get_website_metadata(self, url: str) -> Dict[str, str]:
        """
        Get metadata from a website
        """
        try:
            downloaded = trafilatura.fetch_url(url, headers=self.headers)
            if downloaded:
                metadata = trafilatura.extract_metadata(downloaded)
                return {
                    'title': metadata.title or '',
                    'author': metadata.author or '',
                    'date': metadata.date or '',
                    'description': metadata.description or ''
                }
        except Exception as e:
            logger.error(f"Error getting metadata: {str(e)}")
        
        return {}

def main():
    # Example usage
    scraper = WebScraper()
    url = "https://example.com"
    
    # Get text content
    content = scraper.get_website_text_content(url)
    if content:
        print(f"Content length: {len(content)} characters")
        print("\nPreview:")
        print(scraper.get_text_preview(content))
    
    # Get metadata
    metadata = scraper.get_website_metadata(url)
    print("\nMetadata:")
    print(metadata)

if __name__ == "__main__":
    main() 