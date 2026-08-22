from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

config = context.config

# Load the database URL from the project's pyproject.toml or .env
from sqlalchemy.engine import Engine
from sqlalchemy import text

# Import your Base metadata here
from src.dashboard_mcp.core import Base

def get_database_url():
    """Get database URL from environment variables."""
    from pathlib import Path
    import os
    
    # Try to get from DATABASE_URL env var first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Try to get from .env file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    if key.strip() == "DATABASE_URL":
                        return value.strip()
    
    # Default fallback
    return "postgresql://postgres:postgres@localhost:5432/dashboard_mcp"

def include_object(object, name, type_, reflected, compare_to):
    """Exclude views from auto-generation."""
    if type_ == "view":
        return False
    else:
        return True

def get_url():
    """Get database connection URL."""
    return get_database_url()

def main(argv=None):
    """Main entry point for Alembic."""
    target_metadata = Base.metadata
    
    config.set_main_option("sqlalchemy.url", get_url())
    
    with context.begin_transaction():
        context.configure(
            url=get_url(),
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
            compare_server_default=True,
        )
        
        from alembic import command
        command.upgrade(context, 'head')

if __name__ == "__main__":
    main()