# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Dashboard Chat API
API endpoints for AI-powered dashboard chat functionality
"""

import json
from typing import Any, Dict, List, Optional

import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime, time_diff_in_hours

# Import agents
from insights.agents import AgentRegistry
from insights.agents.query_router import route_query, get_query_router
from insights.agents.sales_agent import SalesIntelligenceAgent
from insights.agents.risk_agent import RiskIntelligenceAgent
from insights.agents.inventory_agent import InventoryIntelligenceAgent
from insights.agents.procurement_agent import ProcurementIntelligenceAgent
from insights.agents.financial_agent import FinancialIntelligenceAgent
from insights.agents.customer_agent import CustomerIntelligenceAgent


# Session timeout in hours (24 hours)
SESSION_TIMEOUT_HOURS = 24


def _safe_log_error(message: str, title: str = "Dashboard Chat"):
    """Safely log an error, truncating to avoid CharacterLengthExceededError"""
    try:
        safe_title = str(title)[:100] if title else "Dashboard Chat"
        safe_message = str(message)[:5000] if message else "No message"
        frappe.log_error(title=safe_title, message=safe_message)
    except Exception:
        print(f"[{title}] {message[:200]}..." if len(str(message)) > 200 else f"[{title}] {message}")

def _compress_context_minimal(context: Dict) -> Dict:
    """Aggressively compress context to minimal size"""
    if not context:
        return {}
    
    compressed = {}
    for key, value in context.items():
        if value is None:
            continue
        elif isinstance(value, (int, float, bool)):
            compressed[key] = value
        elif isinstance(value, str):
            compressed[key] = value[:200] if len(value) > 200 else value
        elif isinstance(value, list):
            # Only first 3 items, and simplify them
            compressed[key] = len(value)  # Just store count
        elif isinstance(value, dict):
            # Only numeric values from dict
            simple = {k: v for k, v in value.items() if isinstance(v, (int, float)) and len(str(k)) < 30}
            if simple:
                compressed[key] = dict(list(simple.items())[:5])
    
    return compressed


def get_agent_for_dashboard(dashboard_type: str):
    """Get the appropriate agent for a dashboard type"""
    agent = AgentRegistry.get_agent(dashboard_type)
    if agent:
        return agent
    
    # Fallback to direct instantiation
    agents = {
        "Sales": SalesIntelligenceAgent,
        "Risk": RiskIntelligenceAgent,
        "Inventory": InventoryIntelligenceAgent,
        "Procurement": ProcurementIntelligenceAgent,
        "Financial": FinancialIntelligenceAgent,
        "Customer": CustomerIntelligenceAgent
    }
    
    agent_class = agents.get(dashboard_type)
    if agent_class:
        return agent_class()
    
    frappe.throw(_(f"No agent available for dashboard type: {dashboard_type}"))


@frappe.whitelist()
def get_recent_session(dashboard_type: str) -> Dict[str, Any]:
    """
    Get the user's most recent active session for a dashboard.
    Auto-loads the session if it's within the timeout period.
    
    Args:
        dashboard_type: Type of dashboard (Sales, Risk, etc.)
        
    Returns:
        Dict with session data or empty dict if no recent session
    """
    try:
        from insights.insights.doctype.dashboard_chat_session.dashboard_chat_session import DashboardChatSession
        
        session = DashboardChatSession.get_user_recent_session(dashboard_type)
        
        if not session:
            return {
                "has_session": False,
                "session_id": None,
                "messages": [],
                "dashboard_type": dashboard_type
            }
        
        # Check if session is still valid (within timeout)
        if session.last_activity:
            hours_since_activity = time_diff_in_hours(now_datetime(), session.last_activity)
            if hours_since_activity > SESSION_TIMEOUT_HOURS:
                # Session expired, mark as inactive
                session.is_active = 0
                session.save(ignore_permissions=True)
                return {
                    "has_session": False,
                    "session_id": None,
                    "messages": [],
                    "dashboard_type": dashboard_type,
                    "expired_session": session.name
                }
        
        return {
            "has_session": True,
            "session_id": session.name,
            "messages": session.get_messages(),
            "dashboard_type": dashboard_type,
            "last_activity": session.last_activity,
            "context": session.get_compressed_context()
        }
        
    except Exception as e:
        _safe_log_error(f"Get session: {str(e)[:200]}", "Chat API")
        return {
            "has_session": False,
            "session_id": None,
            "messages": [],
            "dashboard_type": dashboard_type,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=False)
def start_new_session(dashboard_type=None):
    """Create a new chat session for a dashboard."""
    try:
        # Mark any existing sessions as inactive
        existing_sessions = frappe.get_all(
            "Dashboard Chat Session",
            filters={
                "user": frappe.session.user,
                "dashboard_type": dashboard_type,
                "is_active": 1
            },
            pluck="name"
        )
        
        for session_name in existing_sessions:
            frappe.db.set_value("Dashboard Chat Session", session_name, "is_active", 0)
        
        # Create new session - no context needed
        session = frappe.get_doc({
            "doctype": "Dashboard Chat Session",
            "dashboard_type": dashboard_type,
            "user": frappe.session.user,
            "context_snapshot": "{}",
            "compressed_context": "{}",
            "messages": "[]",
            "last_activity": now_datetime(),
            "is_active": 1
        })
        session.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Get quick actions for this dashboard
        agent = get_agent_for_dashboard(dashboard_type)
        quick_actions = agent.get_quick_actions()
        
        return {
            "success": True,
            "session_id": session.name,
            "dashboard_type": dashboard_type,
            "quick_actions": quick_actions,
            "message": f"New {dashboard_type} Intelligence chat session started"
        }
        
    except Exception as e:
        _safe_log_error(f"Start session: {str(e)[:200]}", "Chat API")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=False)
def send_message(session_id=None, query=None, context=None):
    """Send a message to the dashboard AI agent with dashboard context."""
    try:
        # Validate inputs
        if not session_id or not query:
            return {"success": False, "error": "Missing session_id or query"}
        
        # Truncate query if too long
        query = str(query)[:2000]
        
        # Parse context if provided (comes as JSON string from frontend)
        ctx = {}
        if context:
            try:
                if isinstance(context, str):
                    ctx = json.loads(context)
                elif isinstance(context, dict):
                    ctx = context
            except json.JSONDecodeError:
                ctx = {}
        
        # Get session
        if not frappe.db.exists("Dashboard Chat Session", session_id):
            return {"success": False, "error": "Session not found"}
        
        session = frappe.get_doc("Dashboard Chat Session", session_id)
        dashboard_type = session.dashboard_type
        
        # Get agent
        agent = get_agent_for_dashboard(dashboard_type)
        
        # Add user message
        session.add_message("user", query)
        
        # Get conversation history  
        history = session.build_conversation_history(max_tokens=1000)
        
        # Execute query with context
        result = agent.execute(
            query=query,
            session_id=session_id,
            context=ctx,
            conversation_history=history
        )
        
        # Add AI response
        if result.get("success"):
            session.add_message("assistant", result.get("response", ""))
        
        return {
            "success": result.get("success", False),
            "response": result.get("response"),
            "error": result.get("error"),
            "model_used": result.get("model_used"),
            "session_id": session_id,
            "dashboard_type": dashboard_type
        }
        
    except Exception as e:
        _safe_log_error(f"Send error: {str(e)[:200]}", "Chat API")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_session(session_id: str) -> Dict[str, Any]:
    """
    Get full session data including messages.
    
    Args:
        session_id: Chat session ID
        
    Returns:
        Dict with session data
    """
    try:
        if not frappe.db.exists("Dashboard Chat Session", session_id):
            return {
                "success": False,
                "error": "Session not found"
            }
        
        session = frappe.get_doc("Dashboard Chat Session", session_id)
        
        # Check ownership
        if session.user != frappe.session.user and frappe.session.user != "Administrator":
            return {
                "success": False,
                "error": "Access denied"
            }
        
        return {
            "success": True,
            "session_id": session.name,
            "dashboard_type": session.dashboard_type,
            "messages": session.get_messages(),
            "last_activity": session.last_activity,
            "is_active": session.is_active,
            "context": session.get_compressed_context()
        }
        
    except Exception as e:
        _safe_log_error(f"Get session: {str(e)[:200]}", "Chat API")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def list_sessions(dashboard_type: str, limit: int = 10) -> Dict[str, Any]:
    """
    List user's recent sessions for a dashboard.
    
    Args:
        dashboard_type: Type of dashboard
        limit: Maximum number of sessions to return
        
    Returns:
        Dict with list of sessions
    """
    try:
        from insights.insights.doctype.dashboard_chat_session.dashboard_chat_session import DashboardChatSession
        
        sessions = DashboardChatSession.get_user_sessions(
            dashboard_type=dashboard_type,
            user=frappe.session.user,
            limit=limit
        )
        
        # Enrich with message count
        for session in sessions:
            doc = frappe.get_doc("Dashboard Chat Session", session["name"])
            messages = doc.get_messages()
            session["message_count"] = len(messages)
            session["preview"] = messages[-1]["content"][:100] if messages else ""
        
        return {
            "success": True,
            "sessions": sessions,
            "dashboard_type": dashboard_type
        }
        
    except Exception as e:
        _safe_log_error(f"List error: {str(e)[:200]}", "Chat API")
        return {
            "success": False,
            "error": str(e),
            "sessions": []
        }


@frappe.whitelist()
def get_quick_actions(dashboard_type: str) -> Dict[str, Any]:
    """
    Get quick action buttons for a dashboard type.
    
    Args:
        dashboard_type: Type of dashboard
        
    Returns:
        Dict with quick actions list
    """
    try:
        agent = get_agent_for_dashboard(dashboard_type)
        actions = agent.get_quick_actions()
        
        return {
            "success": True,
            "quick_actions": actions,
            "dashboard_type": dashboard_type
        }
        
    except Exception as e:
        _safe_log_error(f"Actions error: {str(e)[:200]}", "Chat API")
        return {
            "success": False,
            "error": str(e),
            "quick_actions": []
        }


@frappe.whitelist()
def update_session_context(session_id: str, context: str) -> Dict[str, Any]:
    """
    Update the context for an existing session.
    Called when dashboard data changes.
    
    Args:
        session_id: Chat session ID
        context: JSON string of new dashboard context
        
    Returns:
        Dict with success status
    """
    try:
        if not frappe.db.exists("Dashboard Chat Session", session_id):
            return {
                "success": False,
                "error": "Session not found"
            }
        
        session = frappe.get_doc("Dashboard Chat Session", session_id)
        
        # Parse and compress context
        ctx = json.loads(context) if isinstance(context, str) else context
        agent = get_agent_for_dashboard(session.dashboard_type)
        compressed = agent.compress_context(ctx)
        
        session.set_context(ctx, compressed)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Context updated"
        }
        
    except Exception as e:
        _safe_log_error(f"Context error: {str(e)[:200]}", "Chat API")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_ai_chat_status() -> Dict[str, Any]:
    """
    Get the status of AI chat functionality.
    
    Returns:
        Dict with AI status info
    """
    try:
        settings = frappe.get_single("Insights Settings")
        
        return {
            "enabled": bool(settings.enable_ai_analytics),
            "configured": bool(settings.openrouter_api_key),
            "daily_quota": settings.daily_ai_quota or 100,
            "quota_used": settings.ai_quota_used or 0,
            "quota_remaining": max(0, (settings.daily_ai_quota or 100) - (settings.ai_quota_used or 0)),
            "available_dashboards": ["Sales", "Risk", "Inventory", "Procurement", "Financial", "Customer"]
        }
        
    except Exception as e:
        _safe_log_error(f"Status error: {str(e)[:200]}", "Chat API")
        return {
            "enabled": False,
            "configured": False,
            "error": str(e)
        }
