from flask import Blueprint, request, jsonify
from middleware.auth import token_required
from models.task import Task

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['GET'])
@token_required
def get_tasks(current_user):
    status = request.args.get('status')
    priority = request.args.get('priority')
    sort_by = request.args.get('sortBy')
    
    tasks = Task.get_by_user_id(current_user['user_id'])
    
    # Filter by status
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    # Filter by priority
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    
    # Sort
    if sort_by == 'dueDate':
        tasks.sort(key=lambda t: t.due_date if t.due_date else '')
    elif sort_by == 'priority':
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        tasks.sort(key=lambda t: priority_order.get(t.priority, 0), reverse=True)
    
    return jsonify([t.to_dict() for t in tasks]), 200

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
    
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        user_id=current_user['user_id'],
        title=title,
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        due_date=data.get('dueDate')
    )
    task.save()
    
    return jsonify(task.to_dict()), 201

@tasks_bp.route('/<task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    task = Task.find_by_id(task_id)
    
    if not task or task.user_id != current_user['user_id']:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    task.update(data)
    
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/<task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    task = Task.find_by_id(task_id)
    
    if not task or task.user_id != current_user['user_id']:
        return jsonify({'error': 'Task not found'}), 404
    
    task.delete()
    return jsonify({'message': 'Task deleted successfully'}), 200