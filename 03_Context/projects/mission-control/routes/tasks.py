"""Task routes for Mission Control Dashboard."""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from models.database import (
    get_all_tasks, get_task_events, create_task, update_task_status,
    update_task, delete_task
)
from services.task_manager import (
    create_task_with_broadcast, update_task_status_with_broadcast,
    update_task_with_broadcast, delete_task_with_broadcast
)
from routes.validation import (
    TaskCreate, TaskUpdate, TaskStatusUpdate,
    format_validation_error
)

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


@tasks_bp.route("", methods=["GET"])
def list_tasks():
    """Get all tasks."""
    tasks = get_all_tasks()
    return jsonify(tasks)


@tasks_bp.route("", methods=["POST"])
def create_task_endpoint():
    """Create a new task."""
    try:
        data = TaskCreate(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify(format_validation_error(e)), 400
    
    task_id = create_task_with_broadcast(
        data.title,
        data.description,
        data.assignee,
        data.priority,
        data.skills,
        data.model_override,
        source="manual"
    )
    return jsonify({"id": task_id, "status": "created"})


@tasks_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    """Get single task with events."""
    from models.database import get_kanban_conn
    conn = get_kanban_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = c.fetchone()
    conn.close()
    if task:
        task = dict(task)
        task["events"] = get_task_events(task_id)
        return jsonify(task)
    return jsonify({"detail": {"message": "Task not found"}}), 404


@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task_endpoint(task_id):
    """Update full task."""
    try:
        data = TaskUpdate(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify(format_validation_error(e)), 400
    
    updated = update_task_with_broadcast(
        task_id,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        assignee=data.assignee
    )
    if updated:
        return jsonify({"status": "updated"})
    return jsonify({"detail": {"message": "Task not found or no changes"}}), 400


@tasks_bp.route("/<task_id>/status", methods=["PATCH"])
def update_task_status_endpoint(task_id):
    """Update task status."""
    try:
        data = TaskStatusUpdate(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify(format_validation_error(e)), 400
    
    update_task_status_with_broadcast(task_id, data.status)
    return jsonify({"status": "updated"})


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task_endpoint(task_id):
    """Delete task."""
    deleted = delete_task_with_broadcast(task_id)
    if deleted:
        return jsonify({"status": "deleted"})
    return jsonify({"detail": {"message": "Task not found"}}), 404