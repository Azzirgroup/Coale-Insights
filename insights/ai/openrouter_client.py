# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
OpenRouter API Client for AI Analytics
Supports request queuing, model fallback, and response caching
"""

import json
import time
import frappe
import requests
from frappe import _
from frappe.utils import cint, now_datetime, get_datetime
from collections import deque
from typing import Optional, Dict, Any, List


def _safe_log_error(message: str, title: str = "AI Analytics"):
    """Safely log an error, truncating to avoid CharacterLengthExceededError"""
    try:
        # Truncate title to max 100 chars (field limit is 140)
        safe_title = str(title)[:100] if title else "AI Analytics"
        # Truncate message to prevent huge error logs
        safe_message = str(message)[:5000] if message else "No message"
        frappe.log_error(title=safe_title, message=safe_message)
    except Exception:
        # If logging itself fails, just print to console
        print(f"[{title}] {message[:200]}..." if len(str(message)) > 200 else f"[{title}] {message}")


class OpenRouterClient:
    """OpenRouter API client with queuing, fallback, and caching"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    # Free models (prioritized) - updated Dec 2025
    FREE_MODELS = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "openai/gpt-oss-120b:free",
        "google/gemini-2.0-flash-exp:free",
        "qwen/qwen3-235b-a22b:free",
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "nousresearch/hermes-3-llama-3.1-405b:free"
    ]
    
    # Paid models (fallback)
    PAID_MODELS = [
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "anthropic/claude-3.5-sonnet"
    ]
    
    def __init__(self):
        self.settings = frappe.get_single("Insights Settings")
        self.api_key = self.settings.get_password("openrouter_api_key") if self.settings.openrouter_api_key else None
        self.primary_model = self.settings.ai_model or self.FREE_MODELS[0]
        self.fallback_model = self.settings.ai_model_fallback or self.FREE_MODELS[1]
        self.request_queue = deque()
        self.rate_limit_reset = None
        
    def is_enabled(self) -> bool:
        """Check if AI analytics is enabled and configured"""
        return bool(self.settings.enable_ai_analytics and self.api_key)
    
    def check_quota(self) -> bool:
        """Check if daily quota is available"""
        daily_quota = cint(self.settings.daily_ai_quota) or 100
        quota_used = cint(self.settings.ai_quota_used) or 0
        return quota_used < daily_quota
    
    def increment_quota(self):
        """Increment the daily quota usage"""
        frappe.db.set_single_value(
            "Insights Settings", 
            "ai_quota_used", 
            cint(self.settings.ai_quota_used) + 1
        )
        frappe.db.commit()
    
    def reset_daily_quota(self):
        """Reset daily quota (called by scheduler)"""
        frappe.db.set_single_value("Insights Settings", "ai_quota_used", 0)
        frappe.db.commit()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": frappe.utils.get_url(),
            "X-Title": "Frappe Insights AI Analytics"
        }
    
    def _make_request(self, messages: List[Dict], model: str, temperature: float = 0.7) -> Optional[Dict]:
        """Make API request to OpenRouter"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self._get_headers(),
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            if response.status_code == 429:
                # Rate limited - store reset time
                retry_after = response.headers.get("Retry-After", 60)
                self.rate_limit_reset = time.time() + int(retry_after)
                _safe_log_error(f"Rate limited. Retry after {retry_after}s", "AI Rate Limit")
                return None
            
            if response.status_code != 200:
                error_text = response.text[:500] if response.text else "No response"
                _safe_log_error(f"API Error {response.status_code}: {error_text}", "AI API Error")
                return None
            
            result = response.json()
            
            # Check for error in response
            if "error" in result:
                error_msg = str(result.get('error', {}))[:500]
                _safe_log_error(f"API returned error: {error_msg}", "AI API Error")
                return None
                
            return result
            
        except requests.exceptions.RequestException as e:
            _safe_log_error(f"Request Error: {str(e)[:300]}", "AI Request Error")
            return None
        except Exception as e:
            _safe_log_error(f"Unexpected Error: {str(e)[:300]}", "AI Error")
            return None
    
    def chat(self, prompt: str, context: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Send a chat request with automatic model fallback
        
        Args:
            prompt: The user prompt
            context: Optional context data (dashboard data, metrics, etc.)
            use_cache: Whether to use cached responses
            
        Returns:
            Dict with 'response', 'model_used', 'cached', 'error' keys
        """
        if not self.is_enabled():
            return {
                "response": None,
                "model_used": None,
                "cached": False,
                "error": "AI Analytics is not enabled or API key is missing"
            }
        
        if not self.check_quota():
            return {
                "response": None,
                "model_used": None,
                "cached": False,
                "error": "Daily AI quota exceeded"
            }
        
        # Check rate limit
        if self.rate_limit_reset and time.time() < self.rate_limit_reset:
            return {
                "response": None,
                "model_used": None,
                "cached": False,
                "error": f"Rate limited. Retry after {int(self.rate_limit_reset - time.time())} seconds"
            }
        
        # Build cache key
        cache_key = f"ai_analytics:{frappe.generate_hash(prompt + (context or ''), 10)}"
        
        # Check cache
        if use_cache:
            cached_response = frappe.cache.get_value(cache_key)
            if cached_response:
                return {
                    "response": cached_response.get("response"),
                    "model_used": cached_response.get("model"),
                    "cached": True,
                    "error": None
                }
        
        # Build messages
        messages = []
        if context:
            messages.append({
                "role": "system",
                "content": f"""You are an AI analytics assistant for business intelligence. 
Analyze the following data and provide actionable insights.
Be concise, specific, and focus on business value.
Format your response with clear sections using markdown.

Context Data:
{context}"""
            })
        else:
            messages.append({
                "role": "system",
                "content": """You are an AI analytics assistant for business intelligence.
Provide concise, actionable insights focused on business value.
Format your response with clear sections using markdown."""
            })
        
        messages.append({"role": "user", "content": prompt})
        
        # Try primary model first
        models_to_try = [self.primary_model, self.fallback_model]
        
        # Add additional fallbacks if both primary and fallback fail
        for model in self.FREE_MODELS + self.PAID_MODELS:
            if model not in models_to_try:
                models_to_try.append(model)
        
        for model in models_to_try:
            result = self._make_request(messages, model)
            if result and "choices" in result:
                response_text = result["choices"][0]["message"]["content"]
                
                # Cache the response (24 hours)
                frappe.cache.set_value(
                    cache_key,
                    {"response": response_text, "model": model},
                    expires_in_sec=86400  # 24 hours
                )
                
                # Increment quota
                self.increment_quota()
                
                return {
                    "response": response_text,
                    "model_used": model,
                    "cached": False,
                    "error": None
                }
        
        return {
            "response": None,
            "model_used": None,
            "cached": False,
            "error": "All models failed to respond"
        }
    
    def analyze_data(self, data: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """
        Analyze data with AI based on analysis type
        
        Args:
            data: The data to analyze (metrics, KPIs, trends)
            analysis_type: Type of analysis (financial, sales, inventory, etc.)
            
        Returns:
            AI analysis result
        """
        prompts = {
            "financial": """Analyze this financial data and provide:
1. Key Financial Health Indicators
2. Cash Flow Analysis
3. Profitability Trends
4. Risk Areas and Recommendations
5. Actionable Next Steps""",
            
            "sales": """Analyze this sales data and provide:
1. Sales Performance Summary
2. Top Performing Products/Customers
3. Sales Trends and Patterns
4. Growth Opportunities
5. Actionable Recommendations""",
            
            "procurement": """Analyze this procurement data and provide:
1. Spending Analysis Summary
2. Supplier Performance Overview
3. Cost Optimization Opportunities
4. Risk Areas (dependency, pricing)
5. Strategic Recommendations""",
            
            "inventory": """Analyze this inventory data and provide:
1. Stock Health Summary
2. Slow Moving & Dead Stock Analysis
3. Reorder Recommendations
4. Storage Optimization Tips
5. Demand Forecasting Insights""",
            
            "production": """Analyze this production data and provide:
1. Production Efficiency Summary
2. Bottleneck Identification
3. Quality Metrics Analysis
4. Resource Utilization Insights
5. Improvement Recommendations""",
            
            "customer": """Analyze this customer data and provide:
1. Customer Segmentation Summary
2. Retention & Churn Analysis
3. Customer Lifetime Value Insights
4. Engagement Patterns
5. Growth Strategies"""
        }
        
        prompt = prompts.get(analysis_type, prompts["financial"])
        context = json.dumps(data, indent=2, default=str)
        
        return self.chat(prompt, context)


# API endpoints for frontend
@frappe.whitelist()
def get_ai_analysis(dashboard_type: str, data: str = None) -> Dict[str, Any]:
    """
    Get AI analysis for a dashboard
    
    Args:
        dashboard_type: Type of analysis (financial, sales, etc.)
        data: JSON string of data to analyze
        
    Returns:
        AI analysis result
    """
    client = OpenRouterClient()
    
    if data:
        try:
            data_dict = json.loads(data)
        except json.JSONDecodeError:
            data_dict = {}
    else:
        data_dict = {}
    
    return client.analyze_data(data_dict, dashboard_type)


@frappe.whitelist()
def chat_with_ai(prompt: str, context: str = None) -> Dict[str, Any]:
    """
    Chat with AI using dashboard context
    
    Args:
        prompt: User's question or prompt
        context: Optional JSON context data
        
    Returns:
        AI response
    """
    client = OpenRouterClient()
    return client.chat(prompt, context)


@frappe.whitelist()
def get_ai_status() -> Dict[str, Any]:
    """Get AI analytics status and quota information"""
    settings = frappe.get_single("Insights Settings")
    
    return {
        "enabled": bool(settings.enable_ai_analytics),
        "configured": bool(settings.openrouter_api_key),
        "primary_model": settings.ai_model,
        "fallback_model": settings.ai_model_fallback,
        "daily_quota": cint(settings.daily_ai_quota) or 100,
        "quota_used": cint(settings.ai_quota_used) or 0,
        "quota_remaining": max(0, (cint(settings.daily_ai_quota) or 100) - (cint(settings.ai_quota_used) or 0)),
        "last_refresh": settings.last_ai_refresh,
        "refresh_schedule": settings.refresh_schedule
    }


@frappe.whitelist()
def test_connection() -> Dict[str, Any]:
    """Test the OpenRouter API connection"""
    try:
        client = OpenRouterClient()
        
        if not client.api_key:
            return {
                "success": False,
                "error": "OpenRouter API key not configured"
            }
        
        # Make a simple test request
        response = requests.get(
            f"{client.BASE_URL}/auth/key",
            headers=client._get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message": "Connection successful",
                "data": {
                    "credits": data.get("data", {}).get("credits", 0),
                    "usage": data.get("data", {}).get("usage", 0)
                }
            }
        else:
            return {
                "success": False,
                "error": f"API returned status {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Connection timed out. Please try again."
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Connection failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
