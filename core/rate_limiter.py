from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=30, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    def is_allowed(self, user_id):
        now = datetime.now()
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        self.requests[user_id] = [t for t in self.requests[user_id] 
                                 if now - t < timedelta(seconds=self.window)]
        
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
        return False

limiter = RateLimiter()
