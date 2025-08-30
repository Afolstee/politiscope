import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin, urlparse
import trafilatura
import feedparser
from typing import List, Dict

class PoliticalTextScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.rate_limit_delay = 2  # seconds between requests

    def get_website_text_content(self, url: str) -> str:
        """Extract main text content from a website using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text or ""
            return ""
        except Exception as e:
            logging.error(f"Error extracting content from {url}: {str(e)}")
            return ""

    def search_wikipedia(self, politician_name: str) -> Dict:
        """Search Wikipedia for politician information"""
        try:
            # Wikipedia search API
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
            formatted_name = politician_name.replace(' ', '_')
            
            response = self.session.get(search_url.format(formatted_name))
            time.sleep(self.rate_limit_delay)
            
            if response.status_code == 200:
                data = response.json()
                # Get full page content
                page_url = f"https://en.wikipedia.org/wiki/{formatted_name}"
                full_text = self.get_website_text_content(page_url)
                
                return {
                    'source': 'Wikipedia',
                    'title': data.get('title', politician_name),
                    'content': full_text[:5000] if full_text else data.get('extract', ''),
                    'url': page_url,
                    'word_count': len(full_text.split()) if full_text else 0
                }
        except Exception as e:
            logging.error(f"Error searching Wikipedia for {politician_name}: {str(e)}")
            return None

    def search_news_sources(self, politician_name: str) -> List[Dict]:
        """Search basic news sources"""
        news_results = []
        
        # BBC News search (using their search page)
        try:
            bbc_search_url = f"https://www.bbc.com/search?q={politician_name.replace(' ', '+')}"
            bbc_content = self.get_website_text_content(bbc_search_url)
            if bbc_content:
                news_results.append({
                    'source': 'BBC News Search',
                    'content': bbc_content[:2000],
                    'url': bbc_search_url,
                    'word_count': len(bbc_content.split())
                })
        except Exception as e:
            logging.error(f"Error searching BBC: {str(e)}")
        
        time.sleep(self.rate_limit_delay)
        
        # Reuters search
        try:
            reuters_search_url = f"https://www.reuters.com/site-search/?query={politician_name.replace(' ', '+')}"
            reuters_content = self.get_website_text_content(reuters_search_url)
            if reuters_content:
                news_results.append({
                    'source': 'Reuters Search',
                    'content': reuters_content[:2000],
                    'url': reuters_search_url,
                    'word_count': len(reuters_content.split())
                })
        except Exception as e:
            logging.error(f"Error searching Reuters: {str(e)}")
        
        return news_results

    def search_government_sources(self, politician_name: str, country: str = '') -> List[Dict]:
        """Search government websites for politician information"""
        gov_results = []
        
        # US Congress search
        if country.lower() in ['usa', 'us', 'united states', ''] or 'america' in country.lower():
            try:
                congress_search_url = f"https://www.congress.gov/search?q={politician_name.replace(' ', '+')}"
                congress_content = self.get_website_text_content(congress_search_url)
                if congress_content:
                    gov_results.append({
                        'source': 'US Congress',
                        'content': congress_content[:2000],
                        'url': congress_search_url,
                        'word_count': len(congress_content.split())
                    })
            except Exception as e:
                logging.error(f"Error searching Congress.gov: {str(e)}")
        
        time.sleep(self.rate_limit_delay)
        
        # UK Parliament search
        if country.lower() in ['uk', 'united kingdom', 'britain', 'england']:
            try:
                parliament_search_url = f"https://www.parliament.uk/search/results/?q={politician_name.replace(' ', '+')}"
                parliament_content = self.get_website_text_content(parliament_search_url)
                if parliament_content:
                    gov_results.append({
                        'source': 'UK Parliament',
                        'content': parliament_content[:2000],
                        'url': parliament_search_url,
                        'word_count': len(parliament_content.split())
                    })
            except Exception as e:
                logging.error(f"Error searching Parliament.uk: {str(e)}")
        
        return gov_results

    def collect_texts(self, politician_name: str, country: str = '') -> List[Dict]:
        """Main function to collect texts from various sources"""
        all_texts = []
        
        logging.info(f"Starting text collection for: {politician_name}")
        
        # Search Wikipedia
        wiki_result = self.search_wikipedia(politician_name)
        if wiki_result:
            all_texts.append(wiki_result)
        
        # Search news sources
        news_results = self.search_news_sources(politician_name)
        all_texts.extend(news_results)
        
        # Search government sources
        gov_results = self.search_government_sources(politician_name, country)
        all_texts.extend(gov_results)
        
        # Filter out empty results
        all_texts = [text for text in all_texts if text.get('content', '').strip()]
        
        logging.info(f"Collected {len(all_texts)} text sources")
        
        return all_texts

    def get_sample_texts(self, politician_name: str) -> List[Dict]:
        """Get sample texts for demo purposes"""
        sample_texts = {
            'Barack Obama': [
                {
                    'source': 'Sample Speech',
                    'content': 'Yes we can. That was the call to action that brought us together. Hope over fear, unity over division, sending a message that change has come to America. We are the ones we have been waiting for.',
                    'url': 'sample_data',
                    'word_count': 42
                }
            ],
            'Winston Churchill': [
                {
                    'source': 'Sample Speech', 
                    'content': 'We shall fight on the beaches, we shall fight on the landing grounds, we shall fight in the fields and in the streets, we shall fight in the hills; we shall never surrender.',
                    'url': 'sample_data',
                    'word_count': 32
                }
            ]
        }
        
        return sample_texts.get(politician_name, [])
