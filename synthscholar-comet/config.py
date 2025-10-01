import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # COMET Browser Configuration
    COMET_EMAIL = os.getenv('COMET_EMAIL', '')
    COMET_PASSWORD = os.getenv('COMET_PASSWORD', '')
    
    # OpenAI for content synthesis
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # App Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'synthscholar-comet-hackathon-2024')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Model Configuration
    OPENAI_MODEL = "gpt-3.5-turbo"
    
    # Browser Configuration
    BROWSER_HEADLESS = False
    RESEARCH_TIMEOUT = 30
    
    # Demo Mode
    DEMO_MODE = True
    
    # Audio Configuration
    AUDIO_SPEED = 1.0