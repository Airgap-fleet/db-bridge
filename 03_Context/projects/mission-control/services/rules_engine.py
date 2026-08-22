"""Rules Engine for RoE (Rules of Engagement) Enforcement."""

import json
import os
import sqlite3
import time
from typing import Callable, Dict, Any, Optional
from models.database import get_dashboard_conn, DASHBOARD_DIR


# Rule function type: takes (event_type, payload) -> {"allowed": bool, "decision": str}
RuleFunc = Callable[[str, Dict[str, Any]], Dict[str, Any]]


def default_allow(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Default rule: allow everything (fail-open)."""
    return {"allowed": True, "decision": "allow"}


def load_rules_from_json(filepath: str) -> Dict[str, RuleFunc]:
    """Load rules from JSON file. Returns dict of rule_name -> rule_function."""
    if not os.path.exists(filepath):
        return {}
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    rules = {}
    for rule_name, rule_def in data.get("rules", {}).items():
        if "function" in rule_def:
            # For now, only support built-in functions by name
            func_name = rule_def["function"]
            if func_name in BUILTIN_RULES:
                rules[rule_name] = BUILTIN_RULES[func_name]
    return rules


def load_rules_from_yaml(filepath: str) -> Dict[str, RuleFunc]:
    """Load rules from YAML file. Returns dict of rule_name -> rule_function."""
    try:
        import yaml
    except ImportError:
        return {}
    
    if not os.path.exists(filepath):
        return {}
    
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    
    rules = {}
    for rule_name, rule_def in data.get("rules", {}).items():
        if "function" in rule_def:
            func_name = rule_def["function"]
            if func_name in BUILTIN_RULES:
                rules[rule_name] = BUILTIN_RULES[func_name]
    return rules


# Built-in rule functions (can be extended)
BUILTIN_RULES: Dict[str, RuleFunc] = {}


def register_builtin(name: str, func: RuleFunc):
    """Register a built-in rule function."""
    BUILTIN_RULES[name] = func


# Example built-in rules
def rule_max_concurrent_tasks(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Block task creation if agent already has >5 active tasks."""
    if event_type != "task_created":
        return {"allowed": True, "decision": "allow"}
    
    assignee = payload.get("assignee")
    if not assignee:
        return {"allowed": True, "decision": "allow"}
    
    # Tasks are in kanban DB, not dashboard DB
    from models.database import get_kanban_conn
    conn = get_kanban_conn()
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) as cnt FROM tasks 
        WHERE assignee = ? AND status IN ('running', 'ready', 'blocked')
    """, (assignee,))
    row = c.fetchone()
    conn.close()
    
    if row and row["cnt"] >= 5:
        return {"allowed": False, "decision": "deny: agent at max concurrent tasks"}
    return {"allowed": True, "decision": "allow"}


def rule_no_self_assign(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Block tasks assigned to the creating agent (if specified)."""
    if event_type != "task_created":
        return {"allowed": True, "decision": "allow"}
    
    # This would need context about who created it
    return {"allowed": True, "decision": "allow"}


def rule_validate_status_transition(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate status transitions follow allowed flow."""
    if event_type != "task_updated" or "status" not in payload:
        return {"allowed": True, "decision": "allow"}
    
    # Would need current task status to validate transition
    # For now, allow all
    return {"allowed": True, "decision": "allow"}


# Register built-ins
register_builtin("max_concurrent_tasks", rule_max_concurrent_tasks)
register_builtin("no_self_assign", rule_no_self_assign)
register_builtin("validate_status_transition", rule_validate_status_transition)


class RulesRegistry:
    """Registry for RoE rules with evaluation engine."""
    
    def __init__(self):
        self.rules: Dict[str, RuleFunc] = {}
        # Load built-in rules by default
        self.rules.update(BUILTIN_RULES)
        self._load_from_db()
    
    def _load_from_db(self):
        """Load rules from database rules table if exists."""
        conn = get_dashboard_conn()
        c = conn.cursor()
        
        # Check if rules table exists
        c.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='roe_rules'
        """)
        if not c.fetchone():
            conn.close()
            return
        
        c.execute("SELECT name, rule_json FROM roe_rules WHERE enabled = 1")
        for row in c.fetchall():
            try:
                rule_def = json.loads(row["rule_json"])
                if "function" in rule_def:
                    func_name = rule_def["function"]
                    if func_name in BUILTIN_RULES:
                        self.rules[row["name"]] = BUILTIN_RULES[func_name]
            except Exception:
                pass
        conn.close()
    
    def load_from_file(self, filepath: str):
        """Load rules from JSON or YAML file."""
        if filepath.endswith(".json"):
            self.rules.update(load_rules_from_json(filepath))
        elif filepath.endswith((".yaml", ".yml")):
            self.rules.update(load_rules_from_yaml(filepath))
    
    def add_rule(self, name: str, func: RuleFunc):
        """Add a rule function directly."""
        self.rules[name] = func
    
    def remove_rule(self, name: str):
        """Remove a rule by name."""
        self.rules.pop(name, None)
    
    def evaluate_decision(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate all rules for an event.
        Returns {"allowed": bool, "decision": str}
        Fail-open: if no rules match or no rules exist, allow.
        """
        if not self.rules:
            return {"allowed": True, "decision": "allow (no rules)"}
        
        for rule_name, rule_func in self.rules.items():
            try:
                result = rule_func(event_type, payload)
                if not result.get("allowed", True):
                    decision = result.get("decision", f"deny: {rule_name}")
                    self._log_decision(event_type, payload, rule_name, False, decision)
                    return {"allowed": False, "decision": decision}
            except Exception as e:
                # Log error but fail-open
                self._log_decision(event_type, payload, rule_name, True, f"error: {e}")
                continue
        
        # All rules passed
        self._log_decision(event_type, payload, "all", True, "allow")
        return {"allowed": True, "decision": "allow"}
    
    def _log_decision(self, event_type: str, payload: Dict[str, Any], 
                      rule_name: str, allowed: bool, decision: str):
        """Log rule decision to gateway_events table."""
        try:
            conn = get_dashboard_conn()
            c = conn.cursor()
            c.execute("""
                INSERT INTO gateway_events (event_type, payload, timestamp)
                VALUES (?, ?, ?)
            """, (
                f"roe_decision:{rule_name}",
                json.dumps({
                    "event_type": event_type,
                    "payload": payload,
                    "allowed": allowed,
                    "decision": decision,
                    "rule": rule_name
                }),
                int(time.time())
            ))
            conn.commit()
            conn.close()
        except Exception:
            pass  # Fail silently for logging


# Global registry instance
_rules_registry: Optional[RulesRegistry] = None


def get_rules_registry() -> RulesRegistry:
    """Get or create the global rules registry."""
    global _rules_registry
    if _rules_registry is None:
        _rules_registry = RulesRegistry()
    return _rules_registry


def evaluate_decision(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to evaluate a decision using the global registry."""
    return get_rules_registry().evaluate_decision(event_type, payload)