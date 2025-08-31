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

    def contains_speech_or_quotes(self, content: str, politician_name: str) -> bool:
        """Check if content contains speeches or quotes from the politician"""
        if not content:
            return False
            
        content_lower = content.lower()
        name_lower = politician_name.lower()
        
        # Speech indicators
        speech_indicators = [
            'said', 'says', 'stated', 'declared', 'announced', 'spoke', 'speaking',
            'remarked', 'commented', 'addressed', 'told', 'mentioned', 'explained',
            'argued', 'claimed', 'expressed', 'noted', 'emphasized', 'stressed',
            'speech', 'remarks', 'statement', 'address', 'conference', 'interview'
        ]
        
        # Quote indicators
        quote_indicators = ['"', "'", '"', '"', ''', ''']
        
        # Check if politician name appears with speech indicators
        for indicator in speech_indicators:
            if f"{name_lower} {indicator}" in content_lower or f"{indicator}" in content_lower:
                if name_lower in content_lower:
                    return True
        
        # Check for quotes in content with politician name nearby
        for quote in quote_indicators:
            if quote in content and name_lower in content_lower:
                return True
                
        return False

    def search_bbc_comprehensive(self, politician_name: str) -> List[Dict]:
        """Comprehensive BBC search that opens multiple links and filters for speeches/quotes"""
        bbc_results = []
        
        try:
            # Search BBC with multiple search terms for better coverage
            search_terms = [
                politician_name,
                f"{politician_name} speech",
                f"{politician_name} statement",
                f"{politician_name} says"
            ]
            
            all_article_links = set()  # Use set to avoid duplicates
            
            for search_term in search_terms:
                try:
                    bbc_search_url = f"https://www.bbc.com/search?q={search_term.replace(' ', '+')}"
                    response = self.session.get(bbc_search_url)
                    time.sleep(self.rate_limit_delay)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for article links in search results with better selectors
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            
                            # More comprehensive link detection
                            if any(pattern in href for pattern in ['/news/', '/politics/', '/world/', '/uk/']):
                                if href.startswith('/'):
                                    href = 'https://www.bbc.com' + href
                                elif href.startswith('http'):
                                    if 'bbc.com' in href or 'bbc.co.uk' in href:
                                        all_article_links.add(href)
                                    continue
                                else:
                                    continue
                                    
                                # Filter out non-article pages
                                if not any(skip in href for skip in ['#', 'javascript:', 'mailto:', '/search', '/topics']):
                                    all_article_links.add(href)
                        
                except Exception as e:
                    logging.error(f"Error searching BBC with term '{search_term}': {str(e)}")
                    continue
            
            logging.info(f"Found {len(all_article_links)} unique BBC article links for {politician_name}")
            
            # Process each article link (limit to first 10 to avoid overwhelming)
            processed_count = 0
            max_articles = 10
            
            for article_url in list(all_article_links)[:max_articles]:
                try:
                    article_content = self.get_website_text_content(article_url)
                    
                    if article_content and len(article_content.strip()) > 100:  # Minimum content threshold
                        # Check if this article contains speeches or quotes from the politician
                        if self.contains_speech_or_quotes(article_content, politician_name):
                            # Get article title from content or URL
                            title = f"BBC article about {politician_name}"
                            try:
                                # Try to extract title from content
                                lines = article_content.split('\n')
                                if lines and len(lines[0].strip()) < 200:  # Likely a title
                                    title = lines[0].strip()
                            except:
                                pass
                            
                            bbc_results.append({
                                'source': 'BBC News',
                                'title': title,
                                'content': article_content[:4000],  # Increased content length
                                'url': article_url,
                                'word_count': len(article_content.split()),
                                'contains_speech': True
                            })
                            processed_count += 1
                            
                            logging.info(f"Added BBC article {processed_count}: {title[:50]}...")
                    
                    time.sleep(self.rate_limit_delay)  # Rate limiting
                    
                except Exception as e:
                    logging.error(f"Error processing BBC article {article_url}: {str(e)}")
                    continue
            
            logging.info(f"Successfully processed {processed_count} BBC articles with speech content for {politician_name}")
            
        except Exception as e:
            logging.error(f"Error in comprehensive BBC search: {str(e)}")
        
        return bbc_results

    def search_news_sources(self, politician_name: str) -> List[Dict]:
        """Search news sources and extract individual article content"""
        news_results = []
        
        # Enhanced BBC search
        bbc_results = self.search_bbc_comprehensive(politician_name)
        news_results.extend(bbc_results)
        
        time.sleep(self.rate_limit_delay)
        
        # Search Reuters with speech focus
        try:
            reuters_search_terms = [
                f"{politician_name} said",
                f"{politician_name} statement",
                f"{politician_name} speech"
            ]
            
            for term in reuters_search_terms[:2]:  # Limit to 2 searches
                reuters_search_url = f"https://www.reuters.com/site-search/?query={term.replace(' ', '+')}"
                reuters_content = self.get_website_text_content(reuters_search_url)
                
                if reuters_content and self.contains_speech_or_quotes(reuters_content, politician_name):
                    news_results.append({
                        'source': 'Reuters',
                        'title': f'Reuters: {term}',
                        'content': reuters_content[:2500],
                        'url': reuters_search_url,
                        'word_count': len(reuters_content.split()),
                        'contains_speech': True
                    })
                    break  # Only add one Reuters result to avoid redundancy
                    
                time.sleep(self.rate_limit_delay)
                
        except Exception as e:
            logging.error(f"Error searching Reuters: {str(e)}")
        
        return news_results

    def search_government_sources(self, politician_name: str, country: str = '') -> List[Dict]:
        """Search government websites for politician information with speech filtering"""
        gov_results = []
        
        # US Congress search with speech-focused terms
        if country.lower() in ['usa', 'us', 'united states', ''] or 'america' in country.lower():
            try:
                congress_search_terms = [
                    f"{politician_name} speech",
                    f"{politician_name} statement",
                    f"{politician_name} remarks"
                ]
                
                for term in congress_search_terms[:2]:  # Limit searches
                    congress_search_url = f"https://www.congress.gov/search?q={term.replace(' ', '+')}"
                    congress_content = self.get_website_text_content(congress_search_url)
                    
                    if congress_content and self.contains_speech_or_quotes(congress_content, politician_name):
                        gov_results.append({
                            'source': 'US Congress',
                            'title': f'Congress: {term}',
                            'content': congress_content[:3000],
                            'url': congress_search_url,
                            'word_count': len(congress_content.split()),
                            'contains_speech': True
                        })
                        break  # Only add one result to avoid redundancy
                        
                    time.sleep(self.rate_limit_delay)
                    
            except Exception as e:
                logging.error(f"Error searching Congress.gov: {str(e)}")
        
        time.sleep(self.rate_limit_delay)
        
        # UK Parliament search with speech focus
        if country.lower() in ['uk', 'united kingdom', 'britain', 'england']:
            try:
                parliament_search_terms = [
                    f"{politician_name} speech",
                    f"{politician_name} hansard",  # UK Parliamentary records
                    f"{politician_name} statement"
                ]
                
                for term in parliament_search_terms[:2]:  # Limit searches
                    parliament_search_url = f"https://www.parliament.uk/search/results/?q={term.replace(' ', '+')}"
                    parliament_content = self.get_website_text_content(parliament_search_url)
                    
                    if parliament_content and self.contains_speech_or_quotes(parliament_content, politician_name):
                        gov_results.append({
                            'source': 'UK Parliament',
                            'title': f'Parliament: {term}',
                            'content': parliament_content[:3000],
                            'url': parliament_search_url,
                            'word_count': len(parliament_content.split()),
                            'contains_speech': True
                        })
                        break  # Only add one result to avoid redundancy
                        
                    time.sleep(self.rate_limit_delay)
                    
            except Exception as e:
                logging.error(f"Error searching Parliament.uk: {str(e)}")
        
        return gov_results

    def clean_and_improve_content(self, content: str) -> str:
        """Clean and improve extracted content quality"""
        if not content:
            return ""
            
        # Remove excessive whitespace and normalize
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip very short lines that are likely navigation/menu items
            if len(line) > 10 and not line.lower().startswith(('menu', 'search', 'login', 'subscribe')):
                cleaned_lines.append(line)
        
        # Join lines back together
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Remove duplicate paragraphs (sometimes trafilatura extracts duplicates)
        paragraphs = cleaned_content.split('\n\n')
        unique_paragraphs = []
        seen = set()
        
        for para in paragraphs:
            para_clean = para.strip().lower()[:50]  # Use first 50 chars to check for duplicates
            if para_clean not in seen and len(para.strip()) > 20:
                seen.add(para_clean)
                unique_paragraphs.append(para.strip())
        
        return '\n\n'.join(unique_paragraphs)

    def collect_texts(self, politician_name: str, country: str = '') -> List[Dict]:
        """Main function to collect texts from various sources with enhanced filtering"""
        all_texts = []
        
        logging.info(f"Starting comprehensive text collection for: {politician_name}")
        logging.info(f"Target: Find speeches, statements, and quotes from {politician_name}")
        
        # Search Wikipedia first (baseline biographical info)
        try:
            wiki_result = self.search_wikipedia(politician_name)
            if wiki_result and wiki_result.get('content'):
                wiki_result['content'] = self.clean_and_improve_content(wiki_result['content'])
                if len(wiki_result['content']) > 100:  # Ensure meaningful content
                    all_texts.append(wiki_result)
                    logging.info(f"✓ Added Wikipedia article ({len(wiki_result['content'])} chars)")
        except Exception as e:
            logging.error(f"Wikipedia search failed: {str(e)}")
        
        # Search news sources (primary focus on BBC)
        try:
            news_results = self.search_news_sources(politician_name)
            speech_articles = 0
            for result in news_results:
                if result.get('content'):
                    result['content'] = self.clean_and_improve_content(result['content'])
                    if len(result['content']) > 200:  # Minimum meaningful content
                        all_texts.append(result)
                        if result.get('contains_speech'):
                            speech_articles += 1
                            logging.info(f"✓ Added {result['source']} article with speech content ({len(result['content'])} chars)")
                        else:
                            logging.info(f"✓ Added {result['source']} article ({len(result['content'])} chars)")
            logging.info(f"Found {speech_articles} articles containing speech content from news sources")
        except Exception as e:
            logging.error(f"News sources search failed: {str(e)}")
        
        # Search government sources
        try:
            gov_results = self.search_government_sources(politician_name, country)
            gov_speech_count = 0
            for result in gov_results:
                if result.get('content'):
                    result['content'] = self.clean_and_improve_content(result['content'])
                    if len(result['content']) > 200:
                        all_texts.append(result)
                        if result.get('contains_speech'):
                            gov_speech_count += 1
                            logging.info(f"✓ Added {result['source']} document with speech content ({len(result['content'])} chars)")
            logging.info(f"Found {gov_speech_count} government documents containing speech content")
        except Exception as e:
            logging.error(f"Government sources search failed: {str(e)}")
        
        # Final filtering and quality check
        high_quality_texts = []
        total_speech_content = 0
        
        for text in all_texts:
            content = text.get('content', '')
            if content and len(content.strip()) > 50:  # Final quality threshold
                # Update word count after cleaning
                text['word_count'] = len(content.split())
                high_quality_texts.append(text)
                
                if text.get('contains_speech'):
                    total_speech_content += 1
        
        logging.info(f"Collection complete: {len(high_quality_texts)} high-quality sources")
        logging.info(f"Speech/quote content found in {total_speech_content} sources")
        logging.info(f"Total words collected: {sum(t.get('word_count', 0) for t in high_quality_texts)}")
        
        if not high_quality_texts:
            logging.warning(f"No quality content found for {politician_name}. This may indicate:")
            logging.warning("- Name spelling issues")
            logging.warning("- Limited online presence")
            logging.warning("- Website access restrictions")
        
        return high_quality_texts

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
