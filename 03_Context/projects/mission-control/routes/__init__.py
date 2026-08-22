"""Routes package for Mission Control Dashboard."""

from routes.tasks import tasks_bp
from routes.messages import messages_bp
from routes.agents import agents_bp

__all__ = ["tasks_bp", "messages_bp", "agents_bp"]