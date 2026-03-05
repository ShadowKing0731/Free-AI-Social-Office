import os
from groq import Groq

class ContentAgent:
    """Creates Human-Type Scripts (Natural, Not Robotic)"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    def write_script(self, topic, platform, language):
        """Write script that sounds like a REAL human"""
        
        platform_rules = {
            'YouTube': """
            YouTube Rules:
            - Strong hook in first 5 seconds
            - Detailed content (60 seconds)
            - Clear CTA: "Subscribe for more"
            - SEO-friendly description
            """,
            'Instagram': """
            Instagram Rules:
            - Fast-paced (under 60 seconds)
            - Visual cues every 3 seconds
            - Trending audio suggestion
            - CTA: "Follow for daily content"
            - Hashtags included
            """
        }
        
        language_names = {
            'hindi': 'Hindi (हिंदी)',
            'telugu': 'Telugu (తెలుగు)',
            'tamil': 'Tamil (தமிழ்)',
            'english': 'English'
        }
        
        prompt = f"""
        Write a video script for {platform}.
        Topic: {topic}
        Language: {language_names.get(language, 'English')}
        
        Tone: Natural, conversational, emotional (NOT robotic)
        
        {platform_rules.get(platform, '')}
        
        IMPORTANT:
        1. Use natural pauses (...), slang, human expressions
        2. Avoid repetitive AI phrases like "In this video"
        3. Make it unique and engaging
        4. Include visual directions [Show: ...]
        
        Format:
        [0-5s] Hook: [Visual] + [Spoken]
        [5-45s] Content: [Visual] + [Spoken]
        [45-60s] CTA: [Visual] + [Spoken]
        """
        
        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            'script': response.choices[0].message.content,
            'platform': platform,
            'language': language,
            'topic': topic
        }