package governance.finance

import rego.v1

default decision := "DENY"

authorized if {
    input.agent_id == "finance-agent"
    input.action == "payment.create"
    input.resource == "erp.payments"
    input.context.currency == "EUR"
    is_number(input.context.amount)
    input.context.amount > 0
}

decision := "PERMIT" if {
    authorized
    input.context.amount <= 5000
}

decision := "REQUIRE_APPROVAL" if {
    authorized
    input.context.amount > 5000
    input.context.amount <= 50000
}
