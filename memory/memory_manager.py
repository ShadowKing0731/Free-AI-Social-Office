import os
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from datetime import datetime

class MemoryManager:
    """Stores ALL posts (Auto + Manual) + Ensures Uniqueness"""
    
    def __init__(self):
        # MongoDB (Free Tier)
        self.mongo = MongoClient(os.getenv('MONGO_URI'))
        self.db = self.mongo['ai_free_social']
        self.posts_collection = self.db['posts']
        self.performance_collection = self.db['performance']
        self.topics_collection = self.db['posted_topics']
        self.manual_uploads_collection = self.db['manual_uploads']
        
        # Qdrant Vector DB (Free Tier)
        self.qdrant = QdrantClient(
            url=os.getenv('QDRANT_URL'),
            api_key=os.getenv('QDRANT_API_KEY')
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create Vector Collection
        try:
            self.qdrant.create_collection(
                collection_name="social_memory",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
        except:
            pass
    
    def check_topic_uniqueness(self, topic, platform):
        """Ensure content is unique (Not repeated)"""
        recent = list(self.topics_collection.find({
            'platform': platform
        }).sort('posted_at', -1).limit(30))
        
        posted_topics = [t['topic'] for t in recent]
        return topic not in posted_topics
    
    def save_posted_topic(self, topic, platform, language):
        """Store topic to avoid repetition"""
        self.topics_collection.insert_one({
            'topic': topic,
            'platform': platform,
            'language': language,
            'posted_at': datetime.now().isoformat()
        })
        
        # Also store in Vector DB for semantic search
        embed = self.embedding_model.encode(f"{topic} {platform}").tolist()
        self.qdrant.upsert(
            collection_name="social_memory",
            points=[PointStruct(
                id=int(datetime.now().timestamp()),
                vector=embed,
                payload={'topic': topic, 'platform': platform}
            )]
        )
    
    def get_best_performing_topics(self, platform):
        """Learning: What got most views?"""
        best = list(self.performance_collection.find({
            'platform': platform
        }).sort('views', -1).limit(5))
        return [b['topic'] for b in best]
    
    def save_auto_post(self, post_data):
        """Save AI-generated post"""
        post_data['upload_type'] = 'auto'
        post_data['created_at'] = datetime.now().isoformat()
        post_data['status'] = 'published'
        self.posts_collection.insert_one(post_data)
    
    def save_manual_post(self, post_data):
        """Save manually uploaded post"""
        post_data['upload_type'] = 'manual'
        post_data['created_at'] = datetime.now().isoformat()
        post_data['status'] = 'published'
        self.manual_uploads_collection.insert_one(post_data)
        # Also add to main posts for analytics
        self.posts_collection.insert_one(post_data)
    
    def update_performance(self, post_id, views, subs_gained, followers_gained):
        """Learning Loop: Track what works"""
        self.performance_collection.insert_one({
            'post_id': post_id,
            'views': views,
            'subs_gained': subs_gained,
            'followers_gained': followers_gained,
            'recorded_at': datetime.now().isoformat()
        })
    
    def get_analytics(self):
        """Get complete dashboard data (Auto + Manual)"""
        total_posts = self.posts_collection.count_documents({})
        auto_posts = self.posts_collection.count_documents({'upload_type': 'auto'})
        manual_posts = self.posts_collection.count_documents({'upload_type': 'manual'})
        
        # Platform breakdown
        yt_posts = self.posts_collection.count_documents({'platform': 'YouTube'})
        ig_posts = self.posts_collection.count_documents({'platform': 'Instagram'})
        
        # Language breakdown
        languages = {}
        for post in self.posts_collection.find():
            lang = post.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1
        
        # Performance totals
        total_views = sum(p.get('views', 0) for p in self.performance_collection.find())
        total_subs = sum(p.get('subs_gained', 0) for p in self.performance_collection.find())
        total_followers = sum(p.get('followers_gained', 0) for p in self.performance_collection.find())
        
        # Today's posts count
        today = datetime.now().strftime('%Y-%m-%d')
        today_posts = self.posts_collection.count_documents({
            'created_at': {'$gte': today}
        })
        
        return {
            'total_posts': total_posts,
            'auto_posts': auto_posts,
            'manual_posts': manual_posts,
            'today_posts': today_posts,
            'youtube_posts': yt_posts,
            'instagram_posts': ig_posts,
            'languages': languages,
            'total_views': total_views,
            'subscribers_gained': total_subs,
            'followers_gained': total_followers
        }
    
    def get_all_posts(self, limit=50):
        """Get all posts (Auto + Manual)"""
        posts = list(self.posts_collection.find().sort('created_at', -1).limit(limit))
        for post in posts:
            post['_id'] = str(post['_id'])
        return posts
