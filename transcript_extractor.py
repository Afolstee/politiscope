import requests
from bs4 import BeautifulSoup
import time
import logging

def get_miller_transcript(speech_url: str, session: requests.Session) -> str:
    """Extract actual transcript content from Miller Center speech page"""
    try:
        response = session.get(speech_url)
        time.sleep(0.5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            transcript_content = ""
            
            # Method 1: Look for transcript heading and extract content after it
            transcript_heading = soup.find('h3', string='Transcript')
            if transcript_heading:
                # Get all text after the transcript heading until next heading
                current = transcript_heading.find_next_sibling()
                transcript_parts = []
                
                while current and current.name not in ['h1', 'h2', 'h3', 'h4', 'footer']:
                    if current.name in ['p', 'div']:
                        text = current.get_text(separator=' ', strip=True)
                        if text and len(text) > 10:  # Skip very short lines
                            transcript_parts.append(text)
                    current = current.find_next_sibling()
                
                if transcript_parts:
                    transcript_content = '\n\n'.join(transcript_parts)
                    logging.info(f"Found transcript using heading method: {len(transcript_content)} chars")
            
            # Method 2: If no transcript heading, look for speech content patterns
            if not transcript_content or len(transcript_content) < 500:
                # Look for content that starts with typical speech openings
                speech_starters = [
                    'THE PRESIDENT:',
                    'Thank you',
                    'My fellow Americans',
                    'Ladies and gentlemen',
                    'Vice President',
                    'Thank you very much'
                ]
                
                # Find paragraphs that look like speech content
                all_paragraphs = soup.find_all('p')
                speech_paragraphs = []
                found_speech_start = False
                
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    if text:
                        # Check if this looks like the start of a speech
                        if any(starter in text for starter in speech_starters):
                            found_speech_start = True
                            speech_paragraphs.append(text)
                        elif found_speech_start:
                            # Continue collecting speech content
                            # Stop if we hit navigation or footer content
                            if any(stop_word in text.lower() for stop_word in ['navigation', 'menu', 'footer', 'copyright', 'university of virginia']):
                                break
                            speech_paragraphs.append(text)
                
                if speech_paragraphs:
                    transcript_content = '\n\n'.join(speech_paragraphs)
                    logging.info(f"Found transcript using speech pattern method: {len(transcript_content)} chars")
            
            # Clean up the transcript content
            if transcript_content:
                # Remove excessive whitespace and clean up
                lines = transcript_content.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    # Skip navigation and metadata lines
                    if (len(line) > 10 and 
                        not line.lower().startswith(('menu', 'search', 'login', 'skip to', 'help inform')) and
                        'university of virginia' not in line.lower() and
                        'miller center' not in line.lower() and
                        not line.startswith('Download')):
                        cleaned_lines.append(line)
                
                transcript_content = '\n'.join(cleaned_lines)
            
            return transcript_content
            
    except Exception as e:
        logging.debug(f"Error extracting transcript from {speech_url}: {str(e)}")
        return ""