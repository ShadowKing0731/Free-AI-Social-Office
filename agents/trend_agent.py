import os
import requests
from datetime import datetime
from groq import Groq

class TrendAgent:
    """Checks Trending Topics for Auto Video Creation"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY', '')
    
    def get_trending_topics(self, category='all', language='hindi'):
        """Get trending topics from multiple sources"""
        
        # Method 1: Use Groq AI to analyze current trends
        prompt = f"""
        You are a Trending Topics Analyst for YouTube & Instagram.
        
        Current Date: {datetime.now().strftime('%Y-%m-%d')}
        Target Audience: {language} speaking audience
        Category: {category}
        
        Task: Identify 5 TRENDING topics that are:
        1. Currently viral (last 7 days)
        2. High search volume
        3. Good for short-form video (60 seconds)
        4. Suitable for {language} audience
        
        For each topic, provide:
        - Topic name
        - Why it's trending
        - Estimated view potential
        - Competition level (low/medium/high)
        
        Return JSON format:
        {{
            "trending_topics": [
                {{
                    "topic": "...",
                    "reason": "...",
                    "view_potential": "high/medium/low",
                    "competition": "low/medium/high",
                    "category": "..."
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            import json
            trends = json.loads(response.choices[0].message.content)
            
            return {
                'status': 'success',
                'topics': trends.get('trending_topics', []),
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Fallback topics if API fails
            return {
                'status': 'fallback',
                'topics': [
                    {
                        'topic': 'Tech News Today',
                        'reason': 'Always relevant',
                        'view_potential': 'high',
                        'competition': 'medium',
                        'category': 'Technology'
                    },
                    {
                        'topic': 'Daily Motivation',
                        'reason': 'High engagement',
                        'view_potential': 'high',
                        'competition': 'high',
                        'category': 'Motivation'
                    },
                    {
                        'topic': 'Quick Tutorial',
                        'reason': 'Educational content trending',
                        'view_potential': 'medium',
                        'competition': 'low',
                        'category': 'Education'
                    }
                ],
                'fetched_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def select_best_topic(self, topics, platform='YouTube'):
        """Select best topic based on view potential vs competition"""
        
        if not topics:
            return None
        
        # Score each topic
        scored_topics = []
        for topic in topics:
            view_score = {'high': 3, 'medium': 2, 'low': 1}.get(topic.get('view_potential', 'medium'), 2)
            comp_score = {'low': 3, 'medium': 2, 'high': 1}.get(topic.get('competition', 'medium'), 2)
            total_score = view_score + comp_score
            
            scored_topics.append({
                **topic,
                'score': total_score
            })
        
        # Sort by score
        scored_topics.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_topics[0] if scored_topics else None
