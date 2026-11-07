from typing import Any


def simulated_payment(
    parameters: dict[str, Any],
) -> dict[str, Any]:

    return {
        "status": "simulated",
        "amount": parameters["amount"],
        "currency": parameters["currency"],
        "message": "No real payment was executed",
    }
