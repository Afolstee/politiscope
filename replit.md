# Political Discourse Analyzer

## Overview

The Political Discourse Analyzer is a comprehensive web application that performs automated analysis of political speeches and texts using advanced natural language processing (NLP) techniques. The system allows users to input a politician's name, automatically collects relevant texts from multiple sources, and provides detailed discourse analysis across multiple dimensions including rhetorical analysis, sentiment evolution, topic modeling, and persuasion techniques.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Client-Side**: Vanilla JavaScript with progressive enhancement
- **Visualization**: Plotly.js for interactive charts and data visualization
- **UI Framework**: Bootstrap 5 with custom CSS for academic styling
- **Real-time Updates**: JavaScript-based progress tracking and status updates

### Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Application Pattern**: Blueprint-based modular architecture with separation of concerns
- **Session Management**: Flask sessions for tracking analysis progress and user interactions
- **Error Handling**: Centralized logging with graceful error recovery

### Data Processing Pipeline
- **Text Collection**: Multi-source scraping system using requests, BeautifulSoup, and trafilatura
- **NLP Processing**: spaCy and NLTK for linguistic analysis and text processing
- **Analysis Engine**: Custom PoliticalAnalyzer class implementing multiple discourse analysis methods
- **Data Validation**: Input sanitization and content filtering for reliable analysis

### Database Design
- **ORM**: SQLAlchemy with declarative base models
- **Session Tracking**: AnalysisSession model for persistent analysis state
- **User Feedback**: Feedback model for collecting user ratings and comments
- **Database Flexibility**: Configurable database URI supporting SQLite for development

### Analysis Components
- **Rhetorical Analysis**: Ethos, pathos, logos identification using keyword matching
- **Sentiment Analysis**: TextBlob integration for emotional tone tracking
- **Topic Modeling**: Pattern recognition for theme identification
- **Linguistic Features**: Readability scores and complexity metrics
- **Visualization**: Plotly integration for interactive result presentation

## External Dependencies

### NLP Libraries
- **spaCy**: Core NLP processing with en_core_web_sm model
- **NLTK**: Text tokenization, POS tagging, and stopwords
- **TextBlob**: Sentiment analysis and basic text processing

### Web Scraping
- **requests**: HTTP client for web requests
- **BeautifulSoup**: HTML parsing and content extraction
- **trafilatura**: Optimized text extraction from web pages
- **feedparser**: RSS/Atom feed processing for news sources

### Data Sources
- **Wikipedia API**: Biographical information and political content
- **Government Websites**: Official political documents and speeches
- **News APIs**: Real-time political content from major news outlets
- **YouTube**: Transcript extraction for video content analysis

### Visualization and UI
- **Plotly.js**: Interactive charts and data visualization
- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome**: Icon library for enhanced UI
- **Chart.js**: Additional charting capabilities for analysis results

### Infrastructure
- **Flask-SQLAlchemy**: Database ORM and migrations
- **Werkzeug**: WSGI utilities and development server
- **ProxyFix**: Production deployment with reverse proxy support