"""Agents routes for Mission Control Dashboard."""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from models.database import get_all_agents, create_agent, delete_agent
from services.task_manager import create_agent_with_broadcast, delete_agent_with_broadcast
from routes.validation import AgentCreate, format_validation_error

agents_bp = Blueprint("agents", __name__, url_prefix="/api/agents")


@agents_bp.route("", methods=["GET"])
def list_agents():
    """Get all agents with live status."""
    agents = get_all_agents()
    return jsonify(agents)


@agents_bp.route("", methods=["POST"])
def create_agent_endpoint():
    """Create a new agent."""
    try:
        data = AgentCreate(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify(format_validation_error(e)), 422
    
    agent_id = create_agent_with_broadcast(
        data.id,
        data.name,
        data.role,
        data.color,
        data.profile_name
    )
    return jsonify({"id": agent_id, "status": "created"})


@agents_bp.route("/<agent_id>", methods=["DELETE"])
def delete_agent_endpoint(agent_id):
    """Delete agent."""
    deleted = delete_agent_with_broadcast(agent_id)
    if deleted:
        return jsonify({"status": "deleted"})
    return jsonify({"detail": {"message": "Agent not found"}}), 404