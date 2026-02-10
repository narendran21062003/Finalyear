import os
from dotenv import load_dotenv

load_dotenv()

# Hugging Face API Configuration
HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')
HF_API_URL = "https://router.huggingface.co/hf-inference/models/"

# Model selection (you can change this to any Hugging Face model)
HF_MODEL = "facebook/bart-large-mnli"  # For text classification
# Alternative models:
# "distilbert-base-uncased-finetuned-sst-2-english" - Sentiment analysis
# "gpt2" - Text generation

def get_headers():
    """Return authorization headers for Hugging Face API"""
    return {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }
