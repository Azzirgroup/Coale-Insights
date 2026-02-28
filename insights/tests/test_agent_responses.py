# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Live agent response tester.

Usage:
    cd /Users/mac/ERPNext/gardatest
    bench execute insights.tests.test_agent_responses.run_all
    bench execute insights.tests.test_agent_responses.run_agent --args "['Sales','What are the top 5 performing products this month?']"

Each test sends a real query to the configured AI provider and prints the response.
"""

import time
import frappe

# ── Helpers ──────────────────────────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def _print_separator(char="─", width=70):
    print(char * width)


def _print_result(label, result: dict):
    """Pretty-print a single agent result."""
    _print_separator()
    success = result.get("success", False)
    status  = f"{GREEN}✓ OK{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    model   = result.get("model_used", "—")
    ms      = f"{result.get('processing_time', 0)*1000:.0f}ms"
    tokens  = result.get("tokens_used", "—")
    print(f"{BOLD}{label}{RESET}  [{status}]  model={CYAN}{model}{RESET}  {ms}  tokens={tokens}")

    if success:
        resp = result.get("response", "")
        # Wrap at 80 chars for readability
        for line in resp.split("\n"):
            print(f"  {line}")
    else:
        print(f"  {RED}{result.get('error', 'unknown error')}{RESET}")
    print()


# ── Mock contexts per dashboard type ────────────────────────────────────────

MOCK_CONTEXTS = {
    "Sales": {
        "summary": "Sales dashboard for Q1 2026",
        "total_revenue": 4_850_000,
        "total_orders": 312,
        "avg_order_value": 15_545,
        "top_customers": [
            {"name": "ABC Distributors", "revenue": 820_000},
            {"name": "XYZ Traders",      "revenue": 610_000},
            {"name": "Prime Corp",        "revenue": 490_000},
        ],
        "top_products": [
            {"name": "Product A", "units": 520, "revenue": 1_040_000},
            {"name": "Product B", "units": 380, "revenue":   760_000},
        ],
        "trends": [{"metric": "revenue", "direction": "up", "pct": 12}],
        "alerts": [{"message": "3 orders pending fulfilment > 7 days"}],
        "filters": {"date_range": "Q1 2026"},
    },
    "Financial": {
        "summary": "P&L summary for Feb 2026",
        "total_revenue": 2_100_000,
        "total_expenses": 1_620_000,
        "gross_profit": 480_000,
        "profit_margin_pct": 22.8,
        "cash_flow": 310_000,
        "receivables_overdue": 95_000,
        "payables_overdue": 42_000,
        "trends": [{"metric": "expenses", "direction": "up", "pct": 8}],
        "alerts": [{"message": "Payroll due in 3 days"}, {"message": "Overdue receivables up 15%"}],
        "filters": {"date_range": "Feb 2026"},
    },
    "Inventory": {
        "summary": "Warehouse inventory status",
        "total_sku_count": 840,
        "low_stock_count": 23,
        "low_stock_items": [
            {"item": "SKU-012", "current_qty": 5,  "reorder_point": 50},
            {"item": "SKU-045", "current_qty": 8,  "reorder_point": 40},
            {"item": "SKU-103", "current_qty": 11, "reorder_point": 60},
            {"item": "SKU-201", "current_qty": 3,  "reorder_point": 25},
            {"item": "SKU-304", "current_qty": 2,  "reorder_point": 30},
        ],
        "out_of_stock_items": [
            {"item": "SKU-007", "days_out": 4},
            {"item": "SKU-099", "days_out": 2},
            {"item": "SKU-155", "days_out": 1},
        ],
        "inventory_value": 3_200_000,
        "top_moving": [
            {"item": "SKU-001", "qty_sold_30d": 420},
            {"item": "SKU-007", "qty_sold_30d": 310},
        ],
        "dead_stock": [
            {"item": "SKU-213", "days_no_movement": 120}
        ],
        "alerts": [{"message": "7 SKUs stockout"}, {"message": "Reorder point reached for 23 items"}],
        "filters": {"date_range": "Last 30 days"},
    },
    "Risk": {
        "summary": "Risk intelligence overview",
        "high_risk_customers": 5,
        "total_exposure": 780_000,
        "overdue_invoices": 34,
        "overdue_amount": 210_000,
        "fraud_flags": 2,
        "credit_limit_breaches": 3,
        "alerts": [
            {"message": "Customer Delta Ltd exceeded credit limit by 40%"},
            {"message": "2 suspicious transactions flagged by anomaly detection"},
        ],
        "filters": {"date_range": "Last 30 days"},
    },
    "General": {
        "summary": "Overall business health snapshot — Feb 2026",
        "total_revenue": 4_850_000,
        "total_expenses": 3_940_000,
        "net_profit": 910_000,
        "profit_margin_pct": 18.8,
        "cash_on_hand": 1_200_000,
        "overdue_receivables": 210_000,
        "open_orders": 312,
        "pending_fulfilment": 3,
        "employees": 148,
        "open_positions": 6,
        "trends": [
            {"metric": "revenue",  "direction": "up",   "pct": 12},
            {"metric": "expenses", "direction": "up",   "pct": 8},
        ],
        "alerts": [
            {"message": "Payroll due in 3 days"},
            {"message": "3 orders pending > 7 days"},
            {"message": "2 fraud flags need review"},
        ],
        "filters": {"date_range": "Feb 2026"},
    },
    "HR": {
        "summary": "Human resources dashboard",
        "total_employees": 148,
        "active_employees": 143,
        "headcount_change_ytd": 4,
        "avg_tenure_years": 3.2,
        "open_positions": 6,
        "attrition_rate_pct": 8.1,
        "leaves_today": 7,
        "overdue_appraisals": 12,
        "alerts": [{"message": "12 appraisals overdue"}, {"message": "Payroll cut-off tomorrow"}],
        "filters": {"date_range": "YTD 2026"},
    },
}

# ── Queries per agent type ────────────────────────────────────────────────────

QUERIES = {
    "Sales":     "Which customers are driving the most revenue growth and what actions should I take?",
    "Financial": "Explain the profit margin trend and flag any cash-flow risks I should address.",
    "Inventory": "Which stockouts are most urgent and how should I prioritise reorders?",
    "Risk":      "What is our biggest risk exposure right now and what should we do about it?",
    "HR":        "Summarise headcount health and recommend steps to reduce attrition.",
    "General": "Based on this month's dashboard data, give me a health summary and the top 3 actions to take today.",
}


def _build_grounded_query(query: str, ctx: dict) -> str:
    """
    Prepend a compact data summary to the user query so models that have
    weak system-prompt adherence still see the numbers.
    """
    import json
    lines = ["[Dashboard context below — please use this data in your answer]"]
    if ctx.get("summary"):
        lines.append(f"Summary: {ctx['summary']}")
    # Pick up scalar KPIs
    kpi_lines = []
    for k, v in ctx.items():
        if isinstance(v, (int, float)) and k not in ("total_sku_count",):
            kpi_lines.append(f"  {k}: {v:,}" if isinstance(v, int) else f"  {k}: {v}")
    if kpi_lines:
        lines.append("Key metrics:\n" + "\n".join(kpi_lines[:8]))
    if ctx.get("alerts"):
        lines.append("Alerts: " + "; ".join(
            a.get("message", str(a)) for a in ctx["alerts"][:3]
        ))
    lines.append(f"\nUser question: {query}")
    return "\n".join(lines)




def _import_agents():
    """Import all agent modules to trigger @AgentRegistry.register decorators."""
    import insights.agents.sales_agent
    import insights.agents.financial_agent
    import insights.agents.customer_agent
    import insights.agents.inventory_agent
    import insights.agents.procurement_agent
    import insights.agents.risk_agent
    import insights.agents.tax_agent
    import insights.agents.general_agent
    import insights.agents.hr_agent
    import insights.agents.executive_agent
    import insights.agents.marketing_agent
    import insights.agents.manufacturing_agent
    import insights.agents.esg_agent


def _check_ai_enabled():
    """Verify AI provider is configured and enabled."""
    from insights.ai.provider_factory import AIProviderFactory
    client = AIProviderFactory.get_client()
    if not client.is_enabled():
        print(f"\n{RED}⚠  AI Analytics is not enabled.{RESET}")
        print("   Go to Insights Settings and add an API key (OpenRouter or Ollama).\n")
        return False
    print(f"{GREEN}✓  AI provider ready:{RESET} {CYAN}{client.provider_name}{RESET}")
    return True


def run_agent(dashboard_type: str, query: str, session_id: str = "test-session-001"):
    """
    Run a single agent and print the response.

    Args:
        dashboard_type: e.g. "Sales", "Financial", "Inventory"
        query:          The question to ask
        session_id:     Optional session identifier
    """
    _import_agents()

    from insights.agents.registry import AgentRegistry

    agent = AgentRegistry.get_agent(dashboard_type)
    if not agent:
        print(f"{RED}✗ No agent registered for '{dashboard_type}'{RESET}")
        return

    ctx = MOCK_CONTEXTS.get(dashboard_type) or MOCK_CONTEXTS.get("General", {})
    agent.set_context(ctx)

    print(f"\n{BOLD}Query:{RESET} {query}")
    grounded = _build_grounded_query(query, ctx)
    result = agent.execute(query=grounded, session_id=session_id, context=agent.compressed_context)
    _print_result(f"{dashboard_type} Agent", result)
    return result


def run_all(site: str = None):
    """
    Run responses for all configured agents sequentially and print a summary.

    Usage:
        bench --site gardatest.local execute insights.tests.test_agent_responses.run_all
    """
    _print_separator("═")
    print(f"{BOLD}  Insights AI Agent Response Tests{RESET}")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    _print_separator("═")

    if not _check_ai_enabled():
        return

    _import_agents()
    from insights.agents.registry import AgentRegistry

    results = {}
    for dtype, query in QUERIES.items():
        agent = AgentRegistry.get_agent(dtype)
        if not agent:
            print(f"{YELLOW}⚠  Skipped '{dtype}' — agent not registered{RESET}")
            continue

        ctx = MOCK_CONTEXTS.get(dtype, {})
        agent.set_context(ctx)

        print(f"\n{BOLD}[{dtype}]{RESET} {query[:80]}...")
        # Retry once on rate-limit (wait 30 s then retry)
        for attempt in range(2):
            grounded = _build_grounded_query(query, ctx)
            result = agent.execute(
                query=grounded,
                session_id=f"test-{dtype.lower()}-00{attempt+1}",
                context=agent.compressed_context,
            )
            if result.get("success"):
                break
            if "rate-limited" in result.get("error", "").lower() and attempt == 0:
                print(f"  {YELLOW}⏳ Rate-limited — waiting 60 s before retry …{RESET}")
                time.sleep(60)
            else:
                break
        results[dtype] = result
        _print_result(f"{dtype} Agent", result)

        # Pause to reduce rate-limiting for subsequent agents
        if result.get("success"):
            time.sleep(10)

    # ── Summary table ────────────────────────────────────────────────────────
    _print_separator("═")
    print(f"{BOLD}  SUMMARY{RESET}")
    _print_separator()
    passed = sum(1 for r in results.values() if r.get("success"))
    total  = len(results)
    for dtype, r in results.items():
        icon  = f"{GREEN}✓{RESET}" if r.get("success") else f"{RED}✗{RESET}"
        model = r.get("model_used", "—")[:45]
        ms    = f"{r.get('processing_time', 0)*1000:>6.0f}ms"
        print(f"  {icon}  {dtype:<16} {ms}  {CYAN}{model}{RESET}")
    _print_separator()
    colour = GREEN if passed == total else (YELLOW if passed > 0 else RED)
    print(f"  {colour}{passed}/{total} agents responded successfully{RESET}")
    _print_separator("═")

    return results


def run_quick(dashboard_type: str = "General"):
    """
    Quick one-shot test — a single agent, a single question.

    Usage:
        bench --site gardatest.local execute insights.tests.test_agent_responses.run_quick
        bench --site gardatest.local execute insights.tests.test_agent_responses.run_quick --args "['Sales']"
    """
    query = QUERIES.get(dashboard_type, "Give me a business health summary.")
    return run_agent(dashboard_type, query)


def preview(dashboard_type: str = "Sales"):
    """
    Dry-run: print the full system prompt and grounded user query that would be
    sent to the AI model — without making any API call.

    Usage:
        bench --site gardatest.local execute insights.tests.test_agent_responses.preview
        bench --site gardatest.local execute insights.tests.test_agent_responses.preview --args "['Financial']"
    """
    import json
    _import_agents()
    from insights.agents.registry import AgentRegistry

    agent = AgentRegistry.get_agent(dashboard_type)
    if not agent:
        print(f"{RED}✗ No agent for '{dashboard_type}'{RESET}")
        return

    ctx  = MOCK_CONTEXTS.get(dashboard_type, MOCK_CONTEXTS.get("General", {}))
    agent.set_context(ctx)

    query    = QUERIES.get(dashboard_type, "Give me a summary.")
    grounded = _build_grounded_query(query, ctx)
    prompt   = agent.build_system_prompt(agent.compressed_context)

    _print_separator("═")
    print(f"{BOLD}PREVIEW — {dashboard_type} Agent{RESET}")
    _print_separator()
    print(f"{BOLD}=== SYSTEM PROMPT ==={RESET}")
    print(prompt)
    _print_separator()
    print(f"{BOLD}=== USER MESSAGE ==={RESET}")
    print(grounded)
    _print_separator("═")
    print(f"{BOLD}Compressed context size:{RESET} {len(json.dumps(agent.compressed_context))} bytes")


def list_agents():
    """
    List all registered agents and their routing keywords.

    Usage:
        bench --site gardatest.local execute insights.tests.test_agent_responses.list_agents
    """
    _import_agents()
    from insights.agents.registry import AgentRegistry

    types = AgentRegistry.get_all_dashboard_types()
    _print_separator("═")
    print(f"{BOLD}  Registered Agents ({len(types)}){RESET}")
    _print_separator()
    for dtype in sorted(types):
        agent = AgentRegistry.get_agent(dtype)
        keywords = agent.get_routing_keywords()[:5] if agent else []
        kw_str   = ", ".join(keywords)
        print(f"  {CYAN}{dtype:<18}{RESET} keywords: {kw_str}")
    _print_separator("═")
