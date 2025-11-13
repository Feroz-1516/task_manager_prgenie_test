import uuid
from datetime import datetime, timedelta

# In-memory DB
tasks_db = {}

class Task:
    def __init__(self, user_id, title, description='', priority='medium', due_date=None, recurrence=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = 'pending'
        self.due_date = due_date
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        self.recurrence = recurrence  # daily, weekly, monthly
        self.comments = []

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
        if 'recurrence' in data:
            self.recurrence = data['recurrence']
        
        # Handle recurrence auto-clone
        if self.status == 'completed' and self.recurrence:
            next_due = self._get_next_due_date()
            new_task = Task(
                user_id=self.user_id,
                title=self.title,
                description=self.description,
                priority=self.priority,
                due_date=next_due,
                recurrence=self.recurrence
            )
            new_task.save()

        self.updated_at = datetime.utcnow().isoformat()
        self.save()
        return self
    
    def _get_next_due_date(self):
        if not self.due_date:
            return None
        due_datetime = datetime.fromisoformat(self.due_date)
        if self.recurrence == 'daily':
            return (due_datetime + timedelta(days=1)).isoformat()
        elif self.recurrence == 'weekly':
            return (due_datetime + timedelta(weeks=1)).isoformat()
        elif self.recurrence == 'monthly':
            return (dt + timedelta(days=30)).isoformat()
        return None

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
        return [t for t in tasks_db.values() if t.user_id == user_id]
    
    @staticmethod
    def get_overdue_tasks(user_id):
        now = datetime.utcnow().isoformat()
        return [
            t for t in Task.get_by_user_id(user_id)
            if t.due_date and t.status != 'completed' and t.due_date < now
        ]

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
        stats['completion_rate'] = round((stats['completed'] / stats['total']) * 100, 2) if stats['total'] else 0
        return stats

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date,
            'recurrence': self.recurrence,
            'comments': self.comments,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
