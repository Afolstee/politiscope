import os
import json
import logging
from typing import Generator, Dict, Any
import httpx

logger = logging.getLogger(__name__)

class CriticalDiscourseAnalyzer:
    """AI-powered Critical Discourse Analysis using xAI API"""
    
    def __init__(self):
        self.api_key = os.environ.get("XAI_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        
    def validate_text(self, text: str) -> tuple[bool, str]:
        """Validate input text"""
        if not text.strip():
            return False, "Text is required"
        
        word_count = len(text.strip().split())
        if word_count > 4000:
            return False, f"Text too long ({word_count} words). Maximum 4000 words allowed."
        
        return True, ""
    
    def stream_analysis(self, text: str, api_key: str = None) -> Generator[str, None, None]:
        """Stream Critical Discourse Analysis using xAI"""
        
        # Use provided API key or environment variable
        used_api_key = api_key if api_key else self.api_key
        
        if not used_api_key:
            raise ValueError("XAI API key is required. Please provide it in settings or set XAI_API_KEY environment variable.")
        
        # Validate text
        valid, error_msg = self.validate_text(text)
        if not valid:
            raise ValueError(error_msg)
        
        prompt = f"""Conduct a comprehensive Critical Discourse Analysis of the following text using the established academic frameworks:

"{text}"

ANALYSIS PROCESS:

STEP 1: CDA MODEL SELECTION
First, scan the text to determine the most appropriate CDA framework based on text characteristics:

- **Fairclough's Three-Dimensional Model**: Best for texts requiring systematic analysis across textual, discursive practice, and sociocultural dimensions. Ideal for media texts, political discourse, institutional communication.

- **Van Dijk's Socio-Cognitive Approach**: Best for texts involving cognitive mechanisms, mental models, ideological positioning, and power internalization. Ideal for texts showing clear in-group/out-group dynamics, stereotype activation, or cognitive manipulation.

- **Wodak's Discourse-Historical Approach**: Best for texts requiring historical contextualization, social identity construction, nationalism, discrimination analysis. Ideal for political speeches, historical narratives, identity-based discourse.

Clearly state: "Selected CDA Model: [Framework Name] - [Brief rationale based on text characteristics]"

STEP 2: COMPREHENSIVE ANALYSIS USING SELECTED MODEL

Apply the selected framework systematically:

**If Fairclough's Model Selected:**
1. **Textual Analysis (Description)**:
   - Transitivity patterns (who does what to whom)
   - Modality markers (certainty, obligation, permission)
   - Lexical choices and semantic fields
   - Cohesion and textual structure
   - Presuppositions and implications

2. **Discursive Practice (Interpretation)**:
   - Production context and participant roles
   - Intertextuality and genre conventions
   - Distribution and consumption patterns
   - Meaning construction processes

3. **Social Practice (Explanation)**:
   - Power relations and social structures
   - Ideological implications
   - Social identity construction
   - Hegemonic discourse patterns

**If Van Dijk's Approach Selected:**
1. **Cognitive Schema Analysis**:
   - Mental models activated by the text
   - Cognitive categorization patterns
   - Knowledge structures employed

2. **Social Cognition Examination**:
   - Ideological square patterns (us vs them)
   - In-group favoritism and out-group derogation
   - Stereotype activation and reinforcement

3. **Discourse-Cognition-Society Interface**:
   - How individual cognition mediates social structures
   - Power internalization mechanisms
   - Ideology reproduction through cognitive processes

**If Wodak's DHA Selected:**
1. **Historical Contextualization**:
   - Background conditions and historical context
   - Political, social, economic influences
   - Temporal development of discourse themes

2. **Social Actor Analysis**:
   - Identity construction strategies
   - Inclusion/exclusion mechanisms
   - Group categorization patterns

3. **Discursive Strategies**:
   - Argumentation patterns
   - Legitimization and delegitimization
   - Representation strategies

EVIDENCE REQUIREMENTS:
- Provide specific text excerpts for each analytical point
- Explain the discourse significance of each excerpt
- Connect micro-level linguistic features to macro-level social implications

EDUCATIONAL APPROACH:
- Explain concepts clearly for students learning CDA
- Break down complex theoretical points
- Show how analysis connects to broader social understanding

Provide thorough academic analysis following the selected framework systematically."""

        system_message = """You are a Critical Discourse Analysis expert with deep knowledge of the three major CDA frameworks:

**Fairclough's Three-Dimensional Model**: Comprehensive approach spanning textual analysis (linguistic features, grammar, vocabulary, cohesion), discourse practice (production, distribution, consumption contexts, intertextuality), and sociocultural practice (power relations, ideologies, social structures). Emphasizes the dynamic relationship between text and social context.

**Van Dijk's Socio-Cognitive Approach**: Focuses on cognitive mechanisms connecting discourse, cognition, and society. Key concepts include:
- Cognitive schemas: Mental structures for categorizing information
- Mental models: Dynamic, personalized representations during discourse processing
- Ideological square: In-group favoritism vs out-group derogation patterns
- Social cognition: How societal ideologies are internalized and reproduced

**Wodak's Discourse-Historical Approach**: Emphasizes historical contextualization with focus on:
- Interdisciplinary methodology (linguistics, sociology, history, political science)
- Social identity construction and power relations
- Nationalism, racism, and discrimination analysis
- Systematic contextual analysis of discourse conditions

ANALYSIS PRINCIPLES:
- First determine the most suitable framework based on text characteristics
- Apply the selected framework systematically and comprehensively
- Provide specific textual evidence for all analytical claims
- Connect micro-linguistic features to macro-social implications
- Maintain academic rigor while ensuring educational clarity
- Never indicate this analysis is AI-generated
- Avoid bold formatting in responses
- Focus on bridging individual language use with broader social structures"""

        headers = {
            "Authorization": f"Bearer {used_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "stream": True,
            "max_tokens": 4000,
            "temperature": 0.3
        }
        
        try:
            with httpx.stream(
                "POST", 
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            ) as response:
                
                if response.status_code != 200:
                    # Read the response content properly for error handling
                    error_content = ""
                    try:
                        for chunk in response.iter_bytes():
                            error_content += chunk.decode('utf-8', errors='ignore')
                    except:
                        error_content = "Unable to read error response"
                    
                    error_msg = f"API Error {response.status_code}: {error_content}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data == "[DONE]":
                            break
                            
                        try:
                            chunk = json.loads(data)
                            if chunk.get("choices") and len(chunk["choices"]) > 0:
                                choice = chunk["choices"][0]
                                if choice.get("delta") and choice["delta"].get("content"):
                                    content = choice["delta"]["content"]
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Error in stream_analysis: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    def analyze_text(self, text: str, api_key: str = None) -> str:
        """Non-streaming analysis for simple use cases"""
        chunks = []
        try:
            for chunk in self.stream_analysis(text, api_key):
                chunks.append(chunk)
            return "".join(chunks)
        except Exception as e:
            logger.error(f"Error in analyze_text: {str(e)}")
            raise e