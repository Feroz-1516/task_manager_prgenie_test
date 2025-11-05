import uuid
from datetime import datetime

# In-memory database (replace with real DB in production)
tasks_db = {}

class Task:
    def __init__(self, user_id, title, description='', priority='medium', due_date=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.priority = priority  # low, medium, high
        self.status = 'pending'  # pending, in_progress, completed
        self.due_date = due_date
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def save(self):
        tasks_db[self.id] = self
        return self
    
    def update(self, data):
        if 'title' in data:
            self.title = data['title']
        if 'description' in data:
            self.description = data['description']
        if 'priority' in data:
            self.priority = data['priority']
        if 'status' in data:
            self.status = data['status']
        if 'dueDate' in data:
            self.due_date = data['dueDate']
        
        self.updated_at = datetime.utcnow().isoformat()
        self.save()
        return self
    
    def delete(self):
        if self.id in tasks_db:
            del tasks_db[self.id]
            return True
        return False
    
    @staticmethod
    def find_by_id(task_id):
        return tasks_db.get(task_id)
    
    @staticmethod
    def get_by_user_id(user_id):
        return [task for task in tasks_db.values() if task.user_id == user_id]
    
    @staticmethod
    def get_stats(user_id):
        user_tasks = Task.get_by_user_id(user_id)
        
        stats = {
            'total': len(user_tasks),
            'pending': len([t for t in user_tasks if t.status == 'pending']),
            'in_progress': len([t for t in user_tasks if t.status == 'in_progress']),
            'completed': len([t for t in user_tasks if t.status == 'completed']),
            'high_priority': len([t for t in user_tasks if t.priority == 'high']),
            'overdue': len(Task.get_overdue_tasks(user_id))
        }
        
        # Calculate completion rate
        if stats['total'] > 0:
            stats['completion_rate'] = round((stats['completed'] / stats['total']) * 100, 2)
        else:
            stats['completion_rate'] = 0
        
        return stats
    
    @staticmethod
    def get_overdue_tasks(user_id):
        user_tasks = Task.get_by_user_id(user_id)
        now = datetime.utcnow().isoformat()
        
        overdue = []
        for task in user_tasks:
            if task.due_date and task.status != 'completed' and task.due_date < now:
                overdue.append(task)
        
        return overdue
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }