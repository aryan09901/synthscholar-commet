import openai
import logging
from config import Config

logger = logging.getLogger(__name__)

class ContentSynthesizer:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL
        
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("⚠️ No OpenAI API key found. Using mock synthesis.")
    
    def create_podcast_script(self, topic, research_data):
        """Synthesize research data into an engaging podcast script"""
        try:
            # If no API key, use mock synthesis
            if not self.api_key:
                return self._mock_synthesize(topic, research_data)
            
            research_content = self._prepare_research_content(research_data)
            prompt = self._create_podcast_prompt(topic, research_content)
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional podcast scriptwriter and educational content creator. 
Create engaging, conversational podcast scripts that are informative yet easy to follow.
Structure with natural flow: engaging intro, main points with evidence, counter-arguments, and memorable conclusion.
Make it sound like a professional educational podcast with perfect pacing for audio delivery."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            script = response.choices[0].message.content.strip()
            logger.info("✅ Podcast script generated successfully")
            return script
            
        except Exception as e:
            logger.error(f"❌ Script synthesis failed: {str(e)}")
            # Fallback to mock synthesis
            return self._mock_synthesize(topic, research_data)
    
    def _prepare_research_content(self, research_data):
        """Prepare research content for synthesis"""
        content_parts = []
        
        for i, item in enumerate(research_data, 1):
            content_parts.append(f"RESEARCH AREA {i}: {item['sub_query']}\n{item['content']}\n")
        
        return "\n".join(content_parts)
    
    def _create_podcast_prompt(self, topic, research_content):
        """Create the prompt for podcast script generation"""
        return f"""
TOPIC: {topic}

RESEARCH DATA:
{research_content}

Create an engaging 5-7 minute educational podcast script.

REQUIREMENTS:
1. Start with an engaging hook that makes the listener curious
2. Present key findings in a conversational, easy-to-understand way
3. Include specific data points and examples from the research
4. Address different perspectives and counter-arguments
5. End with practical takeaways and future implications
6. Use natural pauses and conversational markers
7. Keep language accessible but informative
8. Target length: 800-1200 words for optimal audio pacing

Format with clear speaker directions and natural flow.
"""
    
    def _mock_synthesize(self, topic, research_data):
        """Mock synthesis when no API key is available"""
        logger.info("🎭 Using mock content synthesis")
        
        key_points = []
        for item in research_data:
            # Extract first few sentences as key points
            sentences = item['content'].split('.')[:3]
            key_points.extend([s.strip() + '.' for s in sentences if s.strip()])
        
        main_points = '\n'.join([f"• {point}" for point in key_points[:4]])
        
        return f"""
🎙️ WELCOME TO SYNTHSCHOLAR PODCAST
Topic: {topic}

[Upbeat intro music fades in]

HOST: "Welcome to another episode of SynthScholar, where we transform complex research into engaging conversations. I'm your host, and today we're diving deep into {topic}."

[Music fades out]

HOST: "If you've ever wondered about the real impact of {topic}, you're in the right place. We've done the research so you can get the key insights in just a few minutes."

MAIN CONTENT:
{main_points}

HOST: "But it's not all positive - there are important considerations too. Researchers have identified several challenges that need addressing..."

KEY CHALLENGES:
• Implementation complexity across different contexts
• Need for proper regulatory frameworks
• Balancing innovation with ethical considerations

HOST: "So what does this mean for the future? Well, experts suggest we're looking at significant transformations in how we approach this field. The potential is enormous, but it requires careful navigation."

CONCLUSION:
HOST: "That's all the time we have today on {topic}. Remember, the key takeaway is that while there are challenges, the opportunities for positive impact are substantial."

[Outro music fades in]

HOST: "Join us next time on SynthScholar as we explore another fascinating topic. Until then, keep learning and stay curious!"

[Music fades out]
"""