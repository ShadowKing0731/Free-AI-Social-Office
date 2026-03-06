import os
from datetime import datetime

class MemoryManager:
    """Stores ALL posts + Ensures Uniqueness + Learning (PDF Architecture)"""
    
    def __init__(self):
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
                self.mongo.admin.command('ping')
                self.db = self.mongo['ai_cloud_office']
                self.posts_collection = self.db['posts']
                self.performance_collection = self.db['performance']
                self.topics_collection = self.db['posted_topics']
                self.use_mock = False
                print("[MEMORY] ✅ MongoDB connected")
            except Exception as e:
                print(f"[MEMORY] ⚠️ MongoDB failed: {e}")
                self.use_mock = True
                self.mock_posts = []
                self.mock_topics = []
                self.mock_performance = []
    
    def check_topic_uniqueness(self, topic, platform):
        if self.use_mock:
            recent = [t for t in self.mock_topics if t['platform'] == platform][-30:]
            posted_topics = [t['topic'].lower() for t in recent]
            return topic.lower() not in posted_topics
        else:
            try:
                recent = list(self.topics_collection.find({'platform': platform}).sort('posted_at', -1).limit(30))
                posted_topics = [t['topic'].lower() for t in recent]
                return topic.lower() not in posted_topics
            except:
                return True
    
    def save_posted_topic(self, topic, platform, language):
        if self.use_mock:
            self.mock_topics.append({'topic': topic, 'platform': platform, 'language': language, 'posted_at': datetime.now().isoformat()})
        else:
            try:
                self.topics_collection.insert_one({'topic': topic, 'platform': platform, 'language': language, 'posted_at': datetime.now().isoformat()})
            except:
                pass
    
    def save_auto_post(self, post_data):
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
            except:
                pass
    
    def save_manual_post(self, post_data):
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
                self.posts_collection.insert_one(post_data)
            except:
                pass
    
    def update_performance(self, post_id, views, subs_gained):
        if self.use_mock:
            self.mock_performance.append({'post_id': post_id, 'views': views, 'subs_gained': subs_gained, 'recorded_at': datetime.now().isoformat()})
        else:
            try:
                self.performance_collection.insert_one({'post_id': post_id, 'views': views, 'subs_gained': subs_gained, 'recorded_at': datetime.now().isoformat()})
            except:
                pass
    
    def get_analytics(self):
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
            return {'total_posts': total_posts, 'auto_posts': auto_posts, 'manual_posts': manual_posts, 'today_posts': today_posts, 'youtube_posts': yt_posts, 'instagram_posts': ig_posts, 'languages': languages, 'total_views': 0, 'subscribers_gained': 0, 'followers_gained': 0}
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
                    languages[lang] = languages.get(lang, 0) + 1
                today = datetime.now().strftime('%Y-%m-%d')
                today_posts = self.posts_collection.count_documents({'created_at': {'$gte': today}})
                return {'total_posts': total_posts, 'auto_posts': auto_posts, 'manual_posts': manual_posts, 'today_posts': today_posts, 'youtube_posts': yt_posts, 'instagram_posts': ig_posts, 'languages': languages, 'total_views': 0, 'subscribers_gained': 0, 'followers_gained': 0}
            except:
                return {'total_posts': 0, 'auto_posts': 0, 'manual_posts': 0, 'today_posts': 0, 'youtube_posts': 0, 'instagram_posts': 0, 'languages': {}, 'total_views': 0, 'subscribers_gained': 0, 'followers_gained': 0}
    
    def get_all_posts(self, limit=50):
        if self.use_mock:
            posts = self.mock_posts[-limit:]
            for post in posts:
                post['_id'] = str(hash(post.get('created_at', '')))
            return posts
        else:
            try:
                posts = list(self.posts_collection.find().sort('created_at', -1).limit(limit))
                for post in posts:
                    post['_id'] = str(post['_id'])
                return posts
            except:
                return []
