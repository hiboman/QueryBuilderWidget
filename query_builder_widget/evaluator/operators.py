from typing import Any, Callable

Operator = Callable[[Any, Any], bool]


OPERATORS: dict[str, Operator] = {
    "equals": lambda a, b: str(a) == str(b),
    "equal": lambda a, b: str(a) == str(b),
    "not_equals": lambda a, b: str(a) != str(b),
    "not_equal": lambda a, b: str(a) != str(b),
    "contains": lambda a, b: str(b) in str(a),
    "not_contains": lambda a, b: str(b) not in str(a),
    "greater": lambda a, b: float(a) > float(b),
    "greater_or_equal": lambda a, b: float(a) >= float(b),
    "less": lambda a, b: float(a) < float(b),
    "less_or_equal": lambda a, b: float(a) <= float(b),
}

FAILURE_SYMBOLS: dict[str, str] = {
    "equals": "≠",
    "equal": "≠",
    "not_equals": "=",
    "not_equal": "=",
    "contains": "does not contain",
    "not_contains": "contains",
    "greater": "≤",
    "greater_or_equal": "<",
    "less": "≥",
    "less_or_equal": ">",
}


def use_operator(operator: str, actual: Any, expected: Any) -> bool:
    return OPERATORS[operator](actual, expected)


def describe_failure(field_label: str, operator: str, expected: Any) -> str:
    symbol = FAILURE_SYMBOLS.get(operator, operator)

    return f"{field_label} {symbol} {expected}"
