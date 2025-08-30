import spacy
import nltk
from textblob import TextBlob
import pandas as pd
import re
from collections import Counter
from typing import Dict, List, Tuple
import logging
import plotly.graph_objects as go
import plotly.express as px
import json

# Try to download required NLTK data, but don't fail if network is unavailable
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt')
    except Exception:
        logging.warning("Could not download NLTK punkt tokenizer")

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('stopwords')
    except Exception:
        logging.warning("Could not download NLTK stopwords")

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    try:
        nltk.download('averaged_perceptron_tagger')
    except Exception:
        logging.warning("Could not download NLTK POS tagger")

class PoliticalAnalyzer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("spaCy model not found. Some features may be limited.")
            self.nlp = None
        
        # Try to load NLTK stopwords, use fallback if not available
        try:
            self.stop_words = set(nltk.corpus.stopwords.words('english'))
        except (LookupError, OSError):
            # Fallback list of common English stopwords
            self.stop_words = {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
                'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if',
                'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
                'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more',
                'very', 'what', 'know', 'just', 'first', 'get', 'over', 'think',
                'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should',
                'after', 'being', 'now', 'made', 'before', 'here', 'through',
                'when', 'where', 'how', 'all', 'during', 'there', 'our', 'his'
            }
            logging.warning("Using fallback stopwords list")
        
        # Political rhetoric indicators
        self.ethos_words = [
            'experience', 'leadership', 'trust', 'integrity', 'credibility',
            'expertise', 'qualified', 'proven', 'record', 'accomplished'
        ]
        
        self.pathos_words = [
            'hope', 'fear', 'anger', 'love', 'hate', 'pride', 'shame',
            'joy', 'sadness', 'worry', 'concern', 'passion', 'emotion'
        ]
        
        self.logos_words = [
            'evidence', 'statistics', 'facts', 'data', 'research', 'study',
            'analysis', 'proof', 'therefore', 'because', 'thus', 'consequently'
        ]
        
        self.rhetorical_devices = {
            'alliteration': r'\b([a-zA-Z])\w*\s+\1\w*',
            'repetition': r'\b(\w+)\b.*\b\1\b',
            'metaphor': r'\b(is|are|was|were)\s+(a|an|the)?\s*\w+',
            'contrast': r'\b(but|however|although|while|whereas)\b'
        }

    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;\:]', '', text)
        return text.strip()

    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using TextBlob"""
        try:
            text = self.clean_text(text)
            blob = TextBlob(text)
            
            # Overall sentiment
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify overall sentiment
            if polarity > 0.1:
                overall_sentiment = 'Positive'
            elif polarity < -0.1:
                overall_sentiment = 'Negative'
            else:
                overall_sentiment = 'Neutral'
            
            # Sentence-level analysis
            sentences = blob.sentences
            sentence_sentiments = []
            
            for sentence in sentences[:10]:  # Limit to first 10 sentences
                sent_polarity = sentence.sentiment.polarity
                sentence_sentiments.append({
                    'text': str(sentence),
                    'polarity': sent_polarity
                })
            
            # Create sentiment distribution
            positive_count = len([s for s in sentence_sentiments if s['polarity'] > 0.1])
            negative_count = len([s for s in sentence_sentiments if s['polarity'] < -0.1])
            neutral_count = len(sentence_sentiments) - positive_count - negative_count
            
            total_sentences = len(sentence_sentiments)
            sentiment_distribution = {
                'positive': round((positive_count / total_sentences * 100), 1) if total_sentences > 0 else 0,
                'neutral': round((neutral_count / total_sentences * 100), 1) if total_sentences > 0 else 0,
                'negative': round((negative_count / total_sentences * 100), 1) if total_sentences > 0 else 0
            }
            
            # Create visualization data
            viz_data = {
                'sentiment_chart': {
                    'labels': ['Positive', 'Neutral', 'Negative'],
                    'values': [sentiment_distribution['positive'], 
                              sentiment_distribution['neutral'], 
                              sentiment_distribution['negative']],
                    'type': 'pie'
                }
            }
            
            return {
                'overall_sentiment': str(overall_sentiment),
                'polarity': float(round(polarity, 3)),
                'subjectivity': float(round(subjectivity, 3)),
                'sentiment_distribution': sentiment_distribution,
                'sample_sentences': [{'text': str(s['text']), 'polarity': float(s['polarity'])} for s in sentence_sentiments[:5]],
                'visualization': viz_data
            }
            
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {str(e)}")
            return {
                'overall_sentiment': 'Unknown',
                'polarity': 0,
                'subjectivity': 0,
                'sentiment_distribution': {'positive': 0, 'neutral': 100, 'negative': 0},
                'error': str(e)
            }

    def analyze_rhetorical_elements(self, text: str) -> Dict:
        """Analyze rhetorical elements (ethos, pathos, logos)"""
        try:
            text = self.clean_text(text.lower())
            words = text.split()
            
            # Count rhetorical indicators
            ethos_count = sum(1 for word in words if word in self.ethos_words)
            pathos_count = sum(1 for word in words if word in self.pathos_words)
            logos_count = sum(1 for word in words if word in self.logos_words)
            
            # Find specific indicators
            ethos_found = [word for word in words if word in self.ethos_words]
            pathos_found = [word for word in words if word in self.pathos_words]
            logos_found = [word for word in words if word in self.logos_words]
            
            # Detect rhetorical devices
            devices_found = []
            for device, pattern in self.rhetorical_devices.items():
                if re.search(pattern, text, re.IGNORECASE):
                    devices_found.append(device)
            
            # Calculate percentages
            total_words = len(words)
            ethos_percentage = round((ethos_count / total_words * 100), 2) if total_words > 0 else 0
            pathos_percentage = round((pathos_count / total_words * 100), 2) if total_words > 0 else 0
            logos_percentage = round((logos_count / total_words * 100), 2) if total_words > 0 else 0
            
            # Create visualization data
            viz_data = {
                'rhetorical_chart': {
                    'labels': ['Ethos', 'Pathos', 'Logos'],
                    'values': [ethos_count, pathos_count, logos_count],
                    'type': 'bar'
                }
            }
            
            return {
                'ethos': {
                    'count': int(ethos_count),
                    'percentage': float(ethos_percentage),
                    'indicators': [str(word) for word in list(set(ethos_found))[:10]]
                },
                'pathos': {
                    'count': int(pathos_count),
                    'percentage': float(pathos_percentage),
                    'indicators': [str(word) for word in list(set(pathos_found))[:10]]
                },
                'logos': {
                    'count': int(logos_count),
                    'percentage': float(logos_percentage),
                    'indicators': [str(word) for word in list(set(logos_found))[:10]]
                },
                'rhetorical_devices': [str(device) for device in devices_found],
                'visualization': viz_data
            }
            
        except Exception as e:
            logging.error(f"Error in rhetorical analysis: {str(e)}")
            return {
                'ethos': {'count': 0, 'percentage': 0, 'indicators': []},
                'pathos': {'count': 0, 'percentage': 0, 'indicators': []},
                'logos': {'count': 0, 'percentage': 0, 'indicators': []},
                'rhetorical_devices': [],
                'error': str(e)
            }

    def analyze_word_frequency(self, text: str) -> Dict:
        """Analyze word frequency and create word cloud data"""
        try:
            text = self.clean_text(text.lower())
            words = text.split()
            
            # Filter out stop words and short words
            meaningful_words = [word for word in words 
                              if word not in self.stop_words 
                              and len(word) > 2 
                              and word.isalpha()]
            
            # Count frequencies
            word_freq = Counter(meaningful_words)
            top_words = word_freq.most_common(20)
            
            # Calculate statistics
            total_words = len(words)
            unique_words = len(set(words))
            vocabulary_richness = round((unique_words / total_words), 3) if total_words > 0 else 0
            
            # Create visualization data - ensure all values are JSON serializable
            labels = [str(word) for word, count in top_words[:10]]
            values = [int(count) for word, count in top_words[:10]]
            
            viz_data = {
                'word_frequency_chart': {
                    'labels': labels,
                    'values': values,
                    'type': 'bar'
                },
                'word_cloud_data': {str(word): int(count) for word, count in top_words[:50]}
            }
            
            # Ensure all data is JSON serializable
            serializable_top_words = [(str(word), int(count)) for word, count in top_words]
            
            return {
                'top_words': serializable_top_words,
                'total_words': int(total_words),
                'unique_words': int(unique_words),
                'vocabulary_richness': float(vocabulary_richness),
                'visualization': viz_data
            }
            
        except Exception as e:
            logging.error(f"Error in word frequency analysis: {str(e)}")
            return {
                'top_words': [],
                'total_words': 0,
                'unique_words': 0,
                'vocabulary_richness': 0,
                'error': str(e)
            }

    def analyze_linguistic_features(self, text: str) -> Dict:
        """Analyze linguistic features like complexity and readability"""
        try:
            text = self.clean_text(text)
            
            # Try NLTK tokenizers, use fallback if not available
            try:
                sentences = nltk.sent_tokenize(text)
                words = nltk.word_tokenize(text)
            except (LookupError, OSError):
                # Simple fallback tokenization
                sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
                words = re.findall(r'\b\w+\b', text)
            
            # Basic statistics
            num_sentences = len(sentences)
            num_words = len(words)
            num_chars = len(text)
            
            # Average lengths
            avg_sentence_length = round(num_words / num_sentences, 2) if num_sentences > 0 else 0
            avg_word_length = round(sum(len(word) for word in words) / num_words, 2) if num_words > 0 else 0
            
            # Syllable counting (approximation)
            def count_syllables(word):
                word = word.lower()
                syllables = 0
                vowels = 'aeiouy'
                if word[0] in vowels:
                    syllables += 1
                for i in range(1, len(word)):
                    if word[i] in vowels and word[i-1] not in vowels:
                        syllables += 1
                if word.endswith('e'):
                    syllables -= 1
                if syllables == 0:
                    syllables = 1
                return syllables
            
            # Flesch Reading Ease Score
            total_syllables = sum(count_syllables(word) for word in words if word.isalpha())
            if num_sentences > 0 and num_words > 0:
                flesch_score = round(206.835 - (1.015 * avg_sentence_length) - (84.6 * (total_syllables / num_words)), 2)
            else:
                flesch_score = 0
            
            # Readability interpretation
            if flesch_score >= 90:
                readability = "Very Easy"
            elif flesch_score >= 80:
                readability = "Easy"
            elif flesch_score >= 70:
                readability = "Fairly Easy"
            elif flesch_score >= 60:
                readability = "Standard"
            elif flesch_score >= 50:
                readability = "Fairly Difficult"
            elif flesch_score >= 30:
                readability = "Difficult"
            else:
                readability = "Very Difficult"
            
            return {
                'text_statistics': {
                    'sentences': int(num_sentences),
                    'words': int(num_words),
                    'characters': int(num_chars),
                    'avg_sentence_length': float(avg_sentence_length),
                    'avg_word_length': float(avg_word_length)
                },
                'readability': {
                    'flesch_score': float(flesch_score),
                    'readability_level': str(readability),
                    'total_syllables': int(total_syllables)
                }
            }
            
        except Exception as e:
            logging.error(f"Error in linguistic analysis: {str(e)}")
            return {
                'text_statistics': {
                    'sentences': 0,
                    'words': 0,
                    'characters': 0,
                    'avg_sentence_length': 0,
                    'avg_word_length': 0
                },
                'readability': {
                    'flesch_score': 0,
                    'readability_level': 'Unknown',
                    'total_syllables': 0
                },
                'error': str(e)
            }
