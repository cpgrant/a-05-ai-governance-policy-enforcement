from typing import Any
import math


def valid_simulated_payment(parameters: dict[str, Any]) -> bool:
    """Accept only the arguments that the simulated handler consumes."""
    if not isinstance(parameters, dict) or set(parameters) != {"amount", "currency"}:
        return False
    amount = parameters["amount"]
    return (
        not isinstance(amount, bool)
        and isinstance(amount, (int, float))
        and math.isfinite(amount)
        and amount > 0
        and parameters["currency"] == "EUR"
    )


def simulated_payment(
    parameters: dict[str, Any],
) -> dict[str, Any]:

    return {
        "status": "simulated",
        "amount": parameters["amount"],
        "currency": parameters["currency"],
        "message": "No real payment was executed",
    }
