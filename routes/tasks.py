from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from models.task import Task
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['GET'])
@token_required
def get_tasks(current_user):
    status = request.args.get('status')
    priority = request.args.get('priority')
    sort_by = request.args.get('sortBy')
    search = request.args.get('search', '').lower()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    tasks = Task.get_by_user_id(current_user['user_id'])

    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if search:
        tasks = [task for task in tasks if search in task.title.lower() or search in task.description.lower()]
    
    if sort_by == 'dueDate':
        tasks.sort(key=lambda task: task.due_date or '')
    elif sort_by == 'priority':
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        tasks.sort(key=lambda t: priority_order.get(t.priority, 0), reverse=True)

    start, end = (page - 1) * limit, (page - 1) * limit + limit
    paginated = tasks[start:end]

    return jsonify({'tasks': [task.to_dict() for task in paginated], 'page': page, 'total': len(tasks)}), 200

@tasks_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    stats = Task.get_stats(current_user['user_id'])
    return jsonify(stats), 200

@tasks_bp.route('/overdue', methods=['GET'])
@token_required
def get_overdue(current_user):
    overdue_tasks = Task.get_overdue_tasks(current_user['user_id'])
    return jsonify([t.to_dict() for t in overdue_tasks]), 200

@tasks_bp.route('/insights', methods=['GET'])
@token_required
def get_insights(current_user):
    tasks = Task.get_by_user_id(current_user['user_id'])
    completed = [task for task in tasks if task.status == 'completed']
    avg_completion_time = None
    
    if completed:
        durations = []
        for task in completed:
            created = datetime.fromisoformat(t.created_at)
            updated = datetime.fromisoformat(t.updated_at)
            durations.append((updated - created).total_seconds())
        avg_completion_time = round(sum(durations) / len(durations) / 3600, 2)
    
    return jsonify({
        'average_completion_hours': avg_completion_time or 0,
        'total_completed': len(completed),
        'total_tasks': len(tasks)
    }), 200

@tasks_bp.route('/<task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    task = Task.find_by_id(task_id)
    if not task or task.user_id != current_user['user_id']:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/', methods=['POST'])
@token_required
def create_task(current_user):
    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    task = Task(
        user_id=current_user['user_id'],
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        due_date=data.get('dueDate'),
        recurrence=data.get('recurrence')
    ).save()
    return jsonify(task.to_dict()), 201

@tasks_bp.route('/<task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    task = Task.find_by_id(task_id)
    if not task or task.user_id != current_user['user_id']:
        return jsonify({'error': 'Task not found'}), 404
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid request: No JSON body found'}), 400
    task.update(data)
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/<task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    task = Task.find_by_id(task_id)
    if not task o
