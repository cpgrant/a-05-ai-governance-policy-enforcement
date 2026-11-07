package governance.mcp

import rego.v1

default decision := "DENY"

customer_tools := {
    "get_customer",
    "list_customers",
    "get_customer_db",
    "list_customers_db",
}

finance_tools := {
    "list_customer_invoices_db",
    "get_customer_financial_summary_db",
}

erp_tools := {
    "get_customer_orders_db",
    "get_order_details_db",
    "get_inventory_status_db",
}

decision := "PERMIT" if {
    input.resource == "a04.mcp"
    input.action == "tool.call"
    input.tool_name in customer_tools
    "reader" in input.roles
}

decision := "PERMIT" if {
    input.resource == "a04.mcp"
    input.action == "tool.call"
    input.tool_name in erp_tools
    "reader" in input.roles
}

decision := "PERMIT" if {
    input.resource == "a04.mcp"
    input.action == "tool.call"
    input.tool_name in finance_tools
    "reader" in input.roles
}

decision := "PERMIT" if {
    input.resource == "a04.mcp"
    input.action == "tool.call"
    input.tool_name in (customer_tools | finance_tools)
    "finance_reader" in input.roles
}
