"""Messages routes for Mission Control Dashboard."""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from models.database import get_messages, create_message
from services.task_manager import create_message_with_broadcast
from routes.validation import MessageCreate, format_validation_error

messages_bp = Blueprint("messages", __name__, url_prefix="/api/messages")


@messages_bp.route("", methods=["GET"])
def list_messages():
    """Get messages, optionally filtered by task_ref or channel."""
    task_ref = request.args.get("task_ref")
    channel = request.args.get("channel")
    if channel:
        messages = get_messages_by_channel(channel)
    else:
        messages = get_messages(task_ref)
    return jsonify(messages)


@messages_bp.route("", methods=["POST"])
def create_message_endpoint():
    """Create a new message."""
    try:
        data = MessageCreate(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify(format_validation_error(e)), 422
    
    message_id = create_message_with_broadcast(
        data.agent_id,
        data.content,
        data.task_ref,
        data.channel,
        data.agent_name,
        data.agent_color
    )
    return jsonify({"id": message_id, "status": "created"})