import os
import logging
import json
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
import uuid

from scraper import PoliticalTextScraper
from analyzer import PoliticalAnalyzer

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///political_discourse.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    import models
    db.create_all()

# Initialize analyzer
analyzer = PoliticalAnalyzer()

@app.route('/')
def index():
    """Main page with politician input form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Start analysis process"""
    politician_name = request.form.get('politician_name', '').strip()
    country = request.form.get('country', '').strip()
    analysis_types = request.form.getlist('analysis_types')
    
    if not politician_name:
        flash('Please enter a politician name', 'error')
        return redirect(url_for('index'))
    
    if not analysis_types:
        flash('Please select at least one analysis type', 'error')
        return redirect(url_for('index'))
    
    # Create session ID for tracking
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    session['politician_name'] = politician_name
    session['country'] = country
    session['analysis_types'] = analysis_types
    
    return render_template('analysis.html', 
                         politician_name=politician_name,
                         country=country,
                         analysis_types=analysis_types,
                         session_id=session_id)

@app.route('/api/scrape_texts', methods=['POST'])
def scrape_texts():
    """API endpoint to scrape political texts"""
    try:
        data = request.get_json()
        politician_name = data.get('politician_name')
        country = data.get('country', '')
        
        scraper = PoliticalTextScraper()
        texts = scraper.collect_texts(politician_name, country)
        
        # Store in session for analysis - limit content size to avoid session cookie overflow
        limited_texts = []
        for text in texts:
            limited_text = text.copy()
            # Limit content to 1000 characters per source to avoid session overflow
            if 'content' in limited_text:
                limited_text['content'] = limited_text['content'][:1000]
            limited_texts.append(limited_text)
        
        session['collected_texts'] = limited_texts
        # Also store full texts temporarily in memory for immediate analysis
        if not hasattr(app, '_temp_texts'):
            app._temp_texts = {}
        app._temp_texts[session.get('session_id', 'default')] = texts
        
        return jsonify({
            'success': True,
            'texts': texts,
            'total_sources': len(texts),
            'total_words': sum(len(text['content'].split()) for text in texts)
        })
    
    except Exception as e:
        logging.error(f"Error in scrape_texts: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze_texts', methods=['POST'])
def analyze_texts():
    """API endpoint to analyze collected texts"""
    try:
        data = request.get_json()
        analysis_types = data.get('analysis_types', [])
        
        # Try to get full texts from temporary storage first, fallback to session
        session_id = session.get('session_id', 'default')
        texts = []
        
        if hasattr(app, '_temp_texts') and session_id in app._temp_texts:
            texts = app._temp_texts[session_id]
            logging.info(f"Using full texts from temp storage: {len(texts)} sources")
        else:
            texts = session.get('collected_texts', [])
            logging.info(f"Using texts from session: {len(texts)} sources")
            
        if not texts:
            logging.error("No texts found in session or temp storage")
            return jsonify({
                'success': False,
                'error': 'No texts found. Please scrape texts first.'
            }), 400
        
        # Combine all text content
        combined_text = ' '.join([text['content'] for text in texts])
        
        results = {}
        
        if 'sentiment' in analysis_types:
            results['sentiment'] = analyzer.analyze_sentiment(combined_text)
        
        if 'rhetorical' in analysis_types:
            results['rhetorical'] = analyzer.analyze_rhetorical_elements(combined_text)
        
        if 'word_frequency' in analysis_types:
            results['word_frequency'] = analyzer.analyze_word_frequency(combined_text)
        
        if 'linguistic' in analysis_types:
            results['linguistic'] = analyzer.analyze_linguistic_features(combined_text)
        
        # Store results in session with limited content
        session['analysis_results'] = results
        
        # Store limited source breakdown to avoid session overflow
        limited_breakdown = []
        for text in texts:
            limited_source = {
                'source': text.get('source', 'Unknown'),
                'word_count': text.get('word_count', 0),
                'url': text.get('url', '')
            }
            limited_breakdown.append(limited_source)
        session['source_breakdown'] = limited_breakdown
        
        # Clean up temp storage
        if hasattr(app, '_temp_texts') and session_id in app._temp_texts:
            del app._temp_texts[session_id]
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        logging.error(f"Error in analyze_texts: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/results')
def results():
    """Display analysis results"""
    results = session.get('analysis_results')
    politician_name = session.get('politician_name')
    source_breakdown = session.get('source_breakdown', [])
    
    if not results:
        flash('No analysis results found. Please start a new analysis.', 'error')
        return redirect(url_for('index'))
    
    return render_template('results.html',
                         results=results,
                         politician_name=politician_name,
                         source_breakdown=source_breakdown)

@app.route('/detailed_analysis')
def detailed_analysis():
    """Display detailed analysis with highlighted texts"""
    results = session.get('analysis_results')
    politician_name = session.get('politician_name')
    
    if not results:
        flash('No analysis results found. Please start a new analysis.', 'error')
        return redirect(url_for('index'))
    
    # Get the original texts for highlighting
    analyzed_texts = session.get('analyzed_texts_with_highlights', [])
    
    # If we don't have highlighted texts, generate them
    if not analyzed_texts:
        analyzed_texts = generate_highlighted_texts()
        session['analyzed_texts_with_highlights'] = analyzed_texts
    
    return render_template('detailed_analysis.html',
                         politician_name=politician_name,
                         analyzed_texts=analyzed_texts,
                         demo_mode=session.get('demo_mode', False))

def generate_highlighted_texts():
    """Generate highlighted text analysis for detailed view"""
    try:
        # Get original texts from session
        texts = session.get('collected_texts', [])
        results = session.get('analysis_results', {})
        
        analyzed_texts = []
        
        for i, text_source in enumerate(texts):
            content = text_source.get('content', '')
            
            # Apply highlighting based on analysis results
            highlighted_content = highlight_text_content(content, results)
            
            analyzed_texts.append({
                'source': text_source.get('source', f'Source {i+1}'),
                'url': text_source.get('url', ''),
                'word_count': len(content.split()),
                'highlighted_content': highlighted_content
            })
        
        return analyzed_texts
        
    except Exception as e:
        logging.error(f"Error generating highlighted texts: {str(e)}")
        return []

def highlight_text_content(content, results):
    """Apply highlighting to text content based on analysis results"""
    try:
        # Start with original content
        highlighted = content
        
        # Get keywords for highlighting
        sentiment_keywords = ['hope', 'change', 'fear', 'anger', 'love', 'hate', 'proud', 'concern']
        ethos_keywords = ['experience', 'qualified', 'trust', 'believe', 'promise', 'commitment']
        pathos_keywords = ['family', 'children', 'future', 'dream', 'struggle', 'fight']
        logos_keywords = ['evidence', 'facts', 'statistics', 'research', 'data', 'study']
        key_phrases = ['america', 'american', 'democracy', 'freedom', 'justice', 'equality']
        
        # Apply highlighting with different classes
        highlighted = apply_highlights(highlighted, sentiment_keywords, 'sentiment-positive')
        highlighted = apply_highlights(highlighted, ethos_keywords, 'rhetorical-ethos')
        highlighted = apply_highlights(highlighted, pathos_keywords, 'rhetorical-pathos')
        highlighted = apply_highlights(highlighted, logos_keywords, 'rhetorical-logos')
        highlighted = apply_highlights(highlighted, key_phrases, 'key-phrase')
        
        return highlighted
        
    except Exception as e:
        logging.error(f"Error highlighting content: {str(e)}")
        return content

def apply_highlights(text, keywords, css_class):
    """Apply highlighting to specific keywords in text"""
    for keyword in keywords:
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        replacement = f'<span class="text-highlight {css_class} annotation">{keyword}<div class="annotation-tooltip">{css_class.replace("-", " ").title()}</div></span>'
        text = pattern.sub(replacement, text)
    return text

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Handle user feedback"""
    if request.method == 'POST':
        try:
            session_id = session.get('session_id')
            politician_name = session.get('politician_name')
            
            rating = request.form.get('rating')
            comments = request.form.get('comments', '')
            helpful = request.form.get('helpful') == 'yes'
            
            # Create feedback record
            feedback_record = models.Feedback()
            feedback_record.session_id = session_id
            feedback_record.politician_name = politician_name
            feedback_record.rating = int(rating) if rating else None
            feedback_record.comments = comments
            feedback_record.helpful = helpful
            feedback_record.timestamp = datetime.utcnow()
            
            db.session.add(feedback_record)
            db.session.commit()
            
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            logging.error(f"Error saving feedback: {str(e)}")
            flash('Error saving feedback. Please try again.', 'error')
    
    return render_template('feedback.html',
                         politician_name=session.get('politician_name'))

@app.route('/api/export/<format>')
def export_results(format):
    """Export analysis results"""
    try:
        results = session.get('analysis_results')
        politician_name = session.get('politician_name')
        
        if not results:
            return jsonify({'error': 'No results to export'}), 400
        
        export_data = {
            'politician_name': politician_name,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'results': results,
            'source_breakdown': session.get('source_breakdown', [])
        }
        
        if format.lower() == 'json':
            response = app.response_class(
                response=json.dumps(export_data, indent=2),
                status=200,
                mimetype='application/json'
            )
            response.headers['Content-Disposition'] = f'attachment; filename="{politician_name}_analysis.json"'
            return response
        
        elif format.lower() == 'csv':
            # Simple CSV export for basic data
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Metric', 'Value', 'Details'])
            
            # Write sentiment data if available
            if 'sentiment' in results:
                sentiment = results['sentiment']
                writer.writerow(['Overall Sentiment', sentiment.get('overall_sentiment', 'N/A'), sentiment.get('polarity', 'N/A')])
            
            # Write word frequency data if available
            if 'word_frequency' in results:
                word_freq = results['word_frequency']
                for word, count in word_freq.get('top_words', [])[:10]:
                    writer.writerow(['Top Word', word, count])
            
            response = app.response_class(
                response=output.getvalue(),
                status=200,
                mimetype='text/csv'
            )
            response.headers['Content-Disposition'] = f'attachment; filename="{politician_name}_analysis.csv"'
            return response
        
        else:
            return jsonify({'error': 'Unsupported export format'}), 400
            
    except Exception as e:
        logging.error(f"Error exporting results: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/demo')
def demo():
    """Demo mode with real data for Barack Obama"""
    try:
        # Use real scraping and analysis for demo
        scraper = PoliticalTextScraper()
        texts = scraper.collect_texts("Barack Obama", "USA")
        
        if not texts:
            # Fallback to sample data if scraping fails
            texts = scraper.get_sample_texts("Barack Obama")
        
        if texts:
            # Combine all text content
            combined_text = ' '.join([text['content'] for text in texts])
            
            # Run real analysis
            results = {}
            results['sentiment'] = analyzer.analyze_sentiment(combined_text)
            results['rhetorical'] = analyzer.analyze_rhetorical_elements(combined_text)
            results['word_frequency'] = analyzer.analyze_word_frequency(combined_text)
            results['linguistic'] = analyzer.analyze_linguistic_features(combined_text)
            
            # Store results in session
            session['analysis_results'] = results
            session['politician_name'] = 'Barack Obama (Demo - Real Data)'
            session['source_breakdown'] = texts
            
            return render_template('results.html',
                                 results=results,
                                 politician_name='Barack Obama (Demo - Real Data)',
                                 source_breakdown=texts,
                                 demo_mode=True)
        else:
            flash('Unable to collect data for demo. Please try the manual analysis.', 'warning')
            return redirect(url_for('index'))
            
    except Exception as e:
        logging.error(f"Error in demo mode: {str(e)}")
        # Fallback to sample demo data if real analysis fails
        demo_results = {
            'sentiment': {
                'overall_sentiment': 'Positive',
                'polarity': 0.15,
                'subjectivity': 0.45,
                'sentiment_distribution': {
                    'positive': 60,
                    'neutral': 30,
                    'negative': 10
                }
            },
            'rhetorical': {
                'ethos': {
                    'count': 15,
                    'percentage': 2.1,
                    'indicators': ['experience', 'leadership', 'trust']
                },
                'pathos': {
                    'count': 22,
                    'percentage': 3.2,
                    'indicators': ['hope', 'change', 'together']
                },
                'logos': {
                    'count': 8,
                    'percentage': 1.1,
                    'indicators': ['evidence', 'statistics', 'facts']
                },
                'rhetorical_devices': ['repetition', 'metaphor', 'alliteration']
            },
            'word_frequency': {
                'top_words': [
                    ['america', 45],
                    ['people', 38],
                    ['change', 32],
                    ['hope', 28],
                    ['together', 25]
                ],
                'unique_words': 1250,
                'total_words': 5000,
                'vocabulary_richness': 0.25
            }
        }
        
        session['analysis_results'] = demo_results
        session['politician_name'] = 'Barack Obama (Demo - Fallback Data)'
        session['source_breakdown'] = [
            {'source': 'Wikipedia', 'word_count': 1500, 'url': 'https://en.wikipedia.org/wiki/Barack_Obama'},
            {'source': 'Sample Speech', 'word_count': 3500, 'url': 'Demo Data'}
        ]
        
        return render_template('results.html',
                             results=demo_results,
                             politician_name='Barack Obama (Demo - Fallback Data)',
                             source_breakdown=session['source_breakdown'],
                             demo_mode=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
