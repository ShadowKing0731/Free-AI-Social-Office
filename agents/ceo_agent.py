import os
import json
from groq import Groq
from datetime import datetime
from memory.memory_manager import MemoryManager

class CEOAgent:
    """Growth Strategist - Maximizes Views, Subs, Followers"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.memory = MemoryManager()
    
    def plan_growth_strategy(self):
        """Decide what to post for MAXIMUM growth"""
        
        # Get past performance (Learning)
        yt_best = self.memory.get_best_performing_topics('YouTube')
        ig_best = self.memory.get_best_performing_topics('Instagram')
        
        # Get posted topics (Avoid Repetition)
        yt_posted = [t['topic'] for t in self.memory.topics_collection.find(
            {'platform': 'YouTube'}
        ).sort('posted_at', -1).limit(10)]
        
        ig_posted = [t['topic'] for t in self.memory.topics_collection.find(
            {'platform': 'Instagram'}
        ).sort('posted_at', -1).limit(10)]
        
        prompt = f"""
        You are a YouTube & Instagram Growth Expert.
        Goal: Maximize Views, Subscribers, and Followers.
        
        YouTube Best Topics: {yt_best}
        Instagram Best Topics: {ig_best}
        
        YouTube Posted Recently (DO NOT REPEAT): {yt_posted}
        Instagram Posted Recently (DO NOT REPEAT): {ig_posted}
        
        Task:
        1. Select 2 NEW YouTube topics (unique, viral potential)
        2. Select 2 NEW Instagram topics (unique, reels optimized)
        3. Choose language for each (hindi, telugu, tamil, english)
        4. Write human-like reason why this will get views
        
        Return JSON:
        {{
            "topics": [
                {{"topic": "...", "platform": "YouTube", "language": "hindi", "reason": "..."}},
                {{"topic": "...", "platform": "YouTube", "language": "telugu", "reason": "..."}},
                {{"topic": "...", "platform": "Instagram", "language": "hindi", "reason": "..."}},
                {{"topic": "...", "platform": "Instagram", "language": "telugu", "reason": "..."}}
            ]
        }}
        """
        
        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.choices[0].message.content)