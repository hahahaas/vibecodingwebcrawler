import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        
        # Define common themes and their related keywords
        self.themes = {
            'community': ['community', 'social', 'shared', 'together', 'connect', 'interact', 'neighbors'],
            'convenience': ['convenient', 'easy', 'simple', 'quick', 'fast', 'efficient', 'hassle-free'],
            'location': ['location', 'area', 'neighborhood', 'district', 'zone', 'region', 'place'],
            'amenities': ['amenities', 'features', 'facilities', 'services', 'utilities', 'included'],
            'lifestyle': ['lifestyle', 'living', 'experience', 'quality', 'comfort', 'enjoy', 'relax'],
            'sustainability': ['sustainable', 'eco-friendly', 'green', 'environmental', 'energy', 'recycle']
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content and return various metrics and insights.
        """
        if not text:
            return {"error": "No text provided for analysis"}
        
        try:
            # Basic text statistics
            words = word_tokenize(text.lower())
            word_count = len(words)
            unique_words = len(set(words))
            
            # Remove stopwords and get word frequency
            filtered_words = [word for word in words if word.isalnum() and word not in self.stop_words]
            word_freq = Counter(filtered_words)
            
            # Theme analysis
            theme_scores = self._analyze_themes(text.lower())
            
            # Language patterns
            patterns = self._analyze_language_patterns(text)
            
            return {
                "statistics": {
                    "total_words": word_count,
                    "unique_words": unique_words,
                    "average_word_length": sum(len(word) for word in words) / word_count if word_count > 0 else 0
                },
                "themes": theme_scores,
                "language_patterns": patterns,
                "top_words": dict(word_freq.most_common(20))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return {"error": f"Error analyzing text: {str(e)}"}
    
    def _analyze_themes(self, text: str) -> Dict[str, float]:
        """
        Analyze the presence of different themes in the text.
        """
        theme_scores = {}
        total_theme_matches = 0
        
        for theme, keywords in self.themes.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            theme_scores[theme] = matches
            total_theme_matches += matches
        
        # Normalize scores
        if total_theme_matches > 0:
            theme_scores = {theme: score/total_theme_matches for theme, score in theme_scores.items()}
        
        return theme_scores
    
    def _analyze_language_patterns(self, text: str) -> Dict[str, Any]:
        """
        Analyze various language patterns in the text.
        """
        patterns = {
            "question_count": len(re.findall(r'\?', text)),
            "exclamation_count": len(re.findall(r'!', text)),
            "sentence_count": len(re.findall(r'[.!?]+', text)),
            "paragraph_count": len(re.findall(r'\n\s*\n', text)) + 1,
            "average_sentence_length": len(text.split()) / len(re.findall(r'[.!?]+', text)) if len(re.findall(r'[.!?]+', text)) > 0 else 0
        }
        
        return patterns
    
    def search_content(self, text: str, search_term: str) -> Dict[str, Any]:
        """
        Search for a term in the content and return context.
        """
        if not text or not search_term:
            return {"error": "No text or search term provided"}
        
        try:
            # Find all occurrences of the search term
            matches = list(re.finditer(r'\b' + re.escape(search_term) + r'\b', text, re.IGNORECASE))
            
            if not matches:
                return {"message": f"No exact matches found for '{search_term}'"}
            
            # Get context for each match
            contexts = []
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                contexts.append({
                    "context": context,
                    "position": match.start()
                })
            
            return {
                "total_matches": len(matches),
                "contexts": contexts
            }
            
        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            return {"error": f"Error searching content: {str(e)}"}

def main():
    # Example usage
    analyzer = TextAnalyzer()
    sample_text = """
    This is a sample text for testing the analyzer.
    It includes some words about community and lifestyle.
    The location is convenient and has great amenities.
    """
    
    analysis = analyzer.analyze_text(sample_text)
    print("Analysis Results:")
    print(json.dumps(analysis, indent=2))

if __name__ == "__main__":
    main() 