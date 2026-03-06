import os
from datetime import datetime

class MemoryManager:
    """Stores ALL posts (Auto + Manual) + Ensures Uniqueness"""
    
    def __init__(self):
        # Try MongoDB connection
        mongo_uri = os.getenv('MONGO_URI')
        
        if not mongo_uri:
            print("[MEMORY] ⚠️ MONGO_URI not found! Running in MOCK mode.")
            self.use_mock = True
            self.mock_posts = []
            self.mock_topics = []
            self.mock_performance = []
        else:
            try:
                from pymongo import MongoClient
                self.mongo = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
                self.mongo.admin.command('ping')  # Test connection
                self.db = self.mongo['ai_free_social']
                self.posts_collection = self.db['posts']
                self.performance_collection = self.db['performance']
                self.topics_collection = self.db['posted_topics']
                self.manual_uploads_collection = self.db['manual_uploads']
                self.use_mock = False
                print("[MEMORY] ✅ MongoDB connected successfully")
            except Exception as e:
                print(f"[MEMORY] ⚠️ MongoDB connection failed: {e}")
                self.use_mock = True
                self.mock_posts = []
                self.mock_topics = []
                self.mock_performance = []
    
    def check_topic_uniqueness(self, topic, platform):
        """Ensure content is unique (Not repeated)"""
        if self.use_mock:
            recent = [t for t in self.mock_topics if t['platform'] == platform][-30:]
            posted_topics = [t['topic'].lower() for t in recent]
            return topic.lower() not in posted_topics
        else:
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
        if self.use_mock:
            self.mock_topics.append({
                'topic': topic,
                'platform': platform,
                'language': language,
                'posted_at': datetime.now().isoformat()
            })
        else:
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
        if self.use_mock:
            return []
        else:
            try:
                best = list(self.performance_collection.find({
                    'platform': platform
                }).sort('views', -1).limit(5))
                return [b['topic'] for b in best]
            except:
                return []
    
    def save_auto_post(self, post_data):
        """Save AI-generated post"""
        if self.use_mock:
            post_data['upload_type'] = 'auto'
            post_data['created_at'] = datetime.now().isoformat()
            post_data['status'] = 'published'
            self.mock_posts.append(post_data)
        else:
            try:
                post_data['upload_type'] = 'auto'
                post_data['created_at'] = datetime.now().isoformat()
                post_data['status'] = 'published'
                self.posts_collection.insert_one(post_data)
            except Exception as e:
                print(f"[MEMORY] Save auto post error: {e}")
    
    def save_manual_post(self, post_data):
        """Save manually uploaded post"""
        if self.use_mock:
            post_data['upload_type'] = 'manual'
            post_data['created_at'] = datetime.now().isoformat()
            post_data['status'] = 'published'
            self.mock_posts.append(post_data)
        else:
            try:
                post_data['upload_type'] = 'manual'
                post_data['created_at'] = datetime.now().isoformat()
                post_data['status'] = 'published'
                self.manual_uploads_collection.insert_one(post_data)
                self.posts_collection.insert_one(post_data)
            except Exception as e:
                print(f"[MEMORY] Save manual post error: {e}")
    
    def update_performance(self, post_id, views, subs_gained, followers_gained):
        """Learning Loop: Track what works"""
        if self.use_mock:
            self.mock_performance.append({
                'post_id': post_id,
                'views': views,
                'subs_gained': subs_gained,
                'followers_gained': followers_gained,
                'recorded_at': datetime.now().isoformat()
            })
        else:
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
        if self.use_mock:
            total_posts = len(self.mock_posts)
            auto_posts = len([p for p in self.mock_posts if p.get('upload_type') == 'auto'])
            manual_posts = len([p for p in self.mock_posts if p.get('upload_type') == 'manual'])
            yt_posts = len([p for p in self.mock_posts if p.get('platform') == 'YouTube'])
            ig_posts = len([p for p in self.mock_posts if p.get('platform') == 'Instagram'])
            
            languages = {}
            for post in self.mock_posts:
                lang = post.get('language', 'unknown')
                languages[lang] = languages.get(lang, 0) + 1
            
            today = datetime.now().strftime('%Y-%m-%d')
            today_posts = len([p for p in self.mock_posts if p.get('created_at', '').startswith(today)])
            
            return {
                'total_posts': total_posts,
                'auto_posts': auto_posts,
                'manual_posts': manual_posts,
                'today_posts': today_posts,
                'youtube_posts': yt_posts,
                'instagram_posts': ig_posts,
                'languages': languages,
                'total_views': 0,
                'subscribers_gained': 0,
                'followers_gained': 0
            }
        else:
            try:
                total_posts = self.posts_collection.count_documents({})
                auto_posts = self.posts_collection.count_documents({'upload_type': 'auto'})
                manual_posts = self.posts_collection.count_documents({'upload_type': 'manual'})
                yt_posts = self.posts_collection.count_documents({'platform': 'YouTube'})
                ig_posts = self.posts_collection.count_documents({'platform': 'Instagram'})
                
                languages = {}
                for post in self.posts_collection.find():
                    lang = post.get('language', 'unknown')
                    languages[lang] = languages.get(lang, 
