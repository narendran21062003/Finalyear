"""
Analyst Module - AI-Powered Analysis
Uses Hugging Face API to analyze customer reviews and identify pain points
"""

import requests
import json
from src.config.hf_config import HF_API_TOKEN, HF_API_URL, get_headers

class AIAnalyst:
    def __init__(self):
        self.api_token = HF_API_TOKEN
        self.headers = get_headers()
        import re
        self.re = re
        
    def analyze_reviews(self, reviews_text):
        """
        Analyze customer reviews using Hugging Face API
        
        Args:
            reviews_text: Text containing customer reviews
            
        Returns:
            Dictionary with pain_point and confidence score
        """
        if not reviews_text or reviews_text.strip() == "":
            return {
                'pain_point': 'No reviews available',
                'confidence': 0.0
            }
        
        try:
            # Use sentiment analysis model
            model_url = f"{HF_API_URL}cardiffnlp/twitter-roberta-base-sentiment"
            
            payload = {
                "inputs": reviews_text[:500]  # Limit text length
            }
            
            response = requests.post(
                model_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse the response
                if isinstance(result, list) and len(result) > 0:
                    sentiment = result[0]
                    
                    # Map sentiment to pain points
                    if isinstance(sentiment, list):
                        negative_score = next(
                            (item['score'] for item in sentiment if item['label'] == 'NEGATIVE'),
                            0.0
                        )
                        
                        if negative_score > 0.6:
                            pain_point = self._identify_pain_point(reviews_text)
                            return {
                                'pain_point': pain_point,
                                'confidence': negative_score
                            }
                
                # If API finds nothing negative, fall back to Rating-based logic
                return self._analyze_based_on_rating(reviews_text)
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return self._analyze_based_on_rating(reviews_text)
                
        except Exception as e:
            print(f"Error in analyze_reviews: {e}")
            return {
                'pain_point': 'Analysis Failed',
                'confidence': 0.0
            }
    
    def _identify_pain_point(self, text):
        """
        Identify specific pain points from negative reviews
        
        Args:
            text: Review text
            
        Returns:
            Pain point category
        """
        text_lower = text.lower()
        
        # Simple keyword-based pain point detection
        pain_points = {
            'Service Optimization': ['service', 'staff', 'rude', 'slow', 'wait', 'unprofessional'],
            'Quality Control': ['quality', 'bad', 'terrible', 'poor quality', 'broken', 'cheap'],
            'Pricing Strategy': ['expensive', 'overpriced', 'price', 'costly', 'value', 'money'],
            'Digital Presence': ['website', 'app', 'error', 'broken', 'bug', 'online', 'booking'],
            'Logistics/Delivery': ['delivery', 'shipping', 'late', 'delayed', 'tracking']
        }
        
        for pain_point, keywords in pain_points.items():
            if any(keyword in text_lower for keyword in keywords):
                return pain_point
        
        return 'Standard Review Volume'

    def _analyze_based_on_rating(self, text):
        """
        Fallback analysis using Star Rating if API fails or is neutral
        """
        # Extract Rating
        rating = 0.0
        try:
            match = self.re.search(r"Rating: (\d+\.\d+)", text)
            if match:
                rating = float(match.group(1))
        except:
            pass
            
        # Check for specific keywords in the text first (strongest signal)
        pain_point = self._identify_pain_point(text)
        if pain_point != 'Standard Review Volume':
             return {'pain_point': pain_point, 'confidence': 0.7}
             
        # Use Rating as baseline
        if rating > 0:
            if rating >= 4.7:
                return {'pain_point': 'High Service Quality', 'confidence': 0.9}
            elif rating >= 4.0:
                return {'pain_point': 'Standard Review Volume', 'confidence': 0.6}
            elif rating < 4.0:
                # Low rating but no specific keywords found -> Default to Quality/Service
                return {'pain_point': 'Service Optimization', 'confidence': 0.5}
        
        # No rating found
        return {'pain_point': 'Inconclusive Data', 'confidence': 0.0}
    
    def generate_email_draft(self, business_name, pain_point):
        """
        Generate personalized outreach email
        
        Args:
            business_name: Name of the business
            pain_point: Identified pain point
            
        Returns:
            Email draft text
        """
        templates = {
            'Poor Service': f"""
Subject: Improve Customer Experience at {business_name}

Dear {business_name} Team,

We've noticed customer feedback indicating service-related concerns. Our AI-powered customer analytics platform can help you:
- Monitor customer sentiment in real-time
- Identify service bottlenecks
- Improve customer satisfaction scores

Would you be interested in a free consultation?

Best regards,
Lead Generation Team
""",
            'Quality Issues': f"""
Subject: Quality Improvement Solutions for {business_name}

Hi {business_name},

Customer reviews suggest opportunities for quality enhancement. We specialize in:
- Quality assurance automation
- Customer feedback analysis
- Product improvement strategies

Let's discuss how we can help.

Best,
Lead Generation Team
""",
            'default': f"""
Subject: Partnership Opportunity for {business_name}

Dear {business_name},

We've identified opportunities to enhance your customer experience. Our data analytics solutions can help address {pain_point}.

Interested in learning more?

Regards,
Lead Generation Team
"""
        }
        
        return templates.get(pain_point, templates['default'])
