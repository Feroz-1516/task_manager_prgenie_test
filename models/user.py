import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory DB
users_db = {}

class User:
    def __init__(self, email, password, name):
        self.id = str(uuid.uuid4())
        self.email = email
        self.password = generate_password_hash(password)
        self.name = name
        self.created_at = datetime.utcnow().isoformat()
    
    def save(self):
        users_db[self.id] = self
        return self
    
    def is_password_valid(self, password):
        return check_password_hash(self.password, password)
    
    @staticmethod
    def find_by_email(email):
        for user in users_db.values():
            if user.email == email:
                return user
        return None
    
    @staticmethod
    def find_by_id(user_id):
        return users_db.get(user_id)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at
        }
