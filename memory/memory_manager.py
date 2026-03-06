import os
from pymongo import MongoClient
from datetime import datetime

class MemoryManager:
    """Stores ALL posts (Auto + Manual) + Ensures Uniqueness"""
    
    def __init__(self):
        # MongoDB (Free Tier)
        mongo_uri = os.getenv('MONGO_URI')
        
        if not mongo_uri:
            print("[WARNING] MONGO_URI not found! Using mock mode.")
            self.mongo = None
            self.db = None
            self.posts_collection = None
            self.performance_collection = None
            self.topics_collection = None
            self.manual_uploads_collection = None
        else:
            try:
                self.mongo = MongoClient(mongo_uri)
                self.db = self.mongo['ai_free_social']
                self.posts_collection = self.db['posts']
                self.performance_collection = self.db['performance']
                self.topics_collection = self.db['posted_topics']
                self.manual_uploads_collection = self.db['manual_uploads']
                print("[MEMORY] MongoDB connected successfully")
            except Exception as e:
                print(f"[WARNING] MongoDB connection failed: {e}")
                self.mongo = None
                self.db = None
                self.posts_collection = None
                self.performance_collection = None
                self.topics_collection = None
                self.manual_uploads_collection = None
    
    def check_topic_uniqueness(self, topic, platform):
        """Ensure content is unique (Not repeated)"""
        if not self.topics_collection:
            return True  # Allow if no database
        
        try:
            recent = list(self.topics_collection.find({
                'platform': platform
            }).sort('posted_at', -1).limit(30))
            
            posted_topics = [t['topic'].lower() for t in recent]
            return topic.lower() not in posted_topics
        except:
            return True
    
    def save_posted_topic(self, topic, platform, language):
        """Store topic to avoid repetition"""
        if not self.topics_collection:
            return
        
        try:
            self.topics_collection.insert_one({
                'topic': topic,
                'platform': platform,
                'language': language,
                'posted_at': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"[MEMORY] Save topic error: {e}")
    
    def get_best_performing_topics(self, platform):
        """Learning: What got most views?"""
        if not self.performance_collection:
            return []
        
        try:
            best = list(self.performance_collection.find({
                'platform': platform
            }).sort('views', -1).limit(5))
            return [b['topic'] for b in best]
        except:
            return []
    
    def save_auto_post(self, post_data):
        """Save AI-generated post"""
        if not self.posts_collection:
            return
        
        post_data['upload_type'] = 'auto'
        post_data['created_at'] = datetime.now().isoformat()
        post_data['status'] = 'published'
        
        try:
            self.posts_collection.insert_one(post_data)
        except Exception as e:
            print(f"[MEMORY] Save auto post error: {e}")
    
    def save_manual_post(self, post_data):
        """Save manually uploaded post"""
        if not self.posts_collection:
            return
        
        post_data['upload_type'] = 'manual'
        post_data['created_at'] = datetime.now().isoformat()
        post_data['status'] = 'published'
        
        try:
            self.manual_uploads_collection.insert_one(post_data)
            self.posts_collection.insert_one(post_data)
        except Exception as e:
            print(f"[MEMORY] Save manual post error: {e}")
    
    def update_performance(self, post_id, views, subs_gained, followers_gained):
        """Learning Loop: Track what works"""
        if not self.performance_collection:
            return
        
        try:
            self.performance_collection.insert_one({
                'post_id': post_id,
                'views': views,
                'subs_gained': subs_gained,
                'followers_gained': followers_gained,
                'recorded_at': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"[MEMORY] Update performance error: {e}")
    
    def get_analytics(self):
        """Get complete dashboard data (Auto + Manual)"""
        if not self.posts_collection:
            return {
                'total_posts': 0,
                'auto_posts': 0,
                'manual_posts': 0,
                'today_posts': 0,
                'youtube_posts': 0,
                'instagram_posts': 0,
                'languages': {},
                'total_views': 0,
                'subscribers_gained': 0,
                'followers_gained': 0
            }
        
        try:
            total_posts = self.posts_collection.count_documents({})
            auto_posts = self.posts_collection.count_documents({'upload_type': 'auto'})
            manual_posts = self.posts_collection.count_documents({'upload_type': 'manual'})
            
            yt_posts = self.posts_collection.count_documents({'platform': 'YouTube'})
            ig_posts = self.posts_collection.count_documents({'platform': 'Instagram'})
            
            languages = {}
            for post in self.posts_collection.find():
                lang = post.get('language', 'unknown')
                languages[lang] = languages.get(lang, 0) + 1
            
            total_views = sum(p.get('views', 0) for p in self.performance_collection.find()) if self.performance_collection else 0
            total_subs = sum(p.get('subs_gained', 0) for p in self.performance_collection.find()) if self.performance_collection else 0
            total_followers = sum(p.get('followers_gained', 0) for p in self.performance_collection.find()) if self.performance_collection else 0
            
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
        except Exception as e:
            print(f"[MEMORY] Get analytics error: {e}")
            return {
                'total_posts': 0,
                'auto_posts': 0,
                'manual_posts': 0,
                'today_posts': 0,
                'youtube_posts': 0,
                'instagram_posts': 0,
                'languages': {},
                'total_views': 0,
                'subscribers_gained': 0,
                'followers_gained': 0
            }
    
    def get_all_posts(self, limit=50):
        """Get all posts (Auto + Manual)"""
        if not self.posts_collection:
            return []
        
        try:
            posts = list(self.posts_collection.find().sort('created_at', -1).limit(limit))
            for post in posts:
                post['_id'] = str(post['_id'])
            return posts
        except Exception as e:
            print(f"[MEMORY] Get posts error: {e}")
            return []
