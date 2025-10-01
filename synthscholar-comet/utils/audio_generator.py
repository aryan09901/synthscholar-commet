import os
import tempfile
import logging
from gtts import gTTS
import uuid
from config import Config

logger = logging.getLogger(__name__)

class AudioGenerator:
    def __init__(self):
        self.speech_rate = Config.AUDIO_SPEED
    
    def text_to_speech(self, text, topic):
        """Convert text to speech and return the file path"""
        try:
            # Clean the text for better TTS
            clean_text = self._clean_text_for_speech(text)
            
            # Generate unique filename
            filename = f"synthscholar_{uuid.uuid4().hex[:8]}.mp3"
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            
            logger.info("🔊 Generating audio...")
            
            # Create TTS with enhanced settings
            tts = gTTS(
                text=clean_text,
                lang='en',
                slow=False,
                lang_check=False
            )
            
            # Save audio file
            tts.save(temp_path)
            
            logger.info(f"✅ Audio generated: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"❌ Audio generation failed: {str(e)}")
            return None
    
    def _clean_text_for_speech(self, text):
        """Clean text for better speech synthesis"""
        # Remove markdown and special characters
        import re
        
        # Remove markdown markers
        clean_text = re.sub(r'[*#`]', '', text)
        
        # Remove excessive newlines
        clean_text = re.sub(r'\n+', '\n', clean_text)
        
        # Ensure proper sentence spacing
        clean_text = re.sub(r'\.(?=\w)', '. ', clean_text)
        
        # Remove any remaining special formatting
        clean_text = re.sub(r'\[.*?\]', '', clean_text)
        clean_text = re.sub(r'RESEARCH AREA \d+:', '', clean_text)
        
        # Add pauses after headings
        clean_text = clean_text.replace('HOST:', '\n\nHOST:')
        clean_text = clean_text.replace('CONCLUSION:', '\n\nCONCLUSION:')
        
        return clean_text.strip()