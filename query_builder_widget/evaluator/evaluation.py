from collections.abc import Awaitable, Callable
from inspect import isawaitable
from typing import Any, cast

from ..types import EvaluationResult, QueryGroup, QueryRule
from .operators import describe_failure, use_operator

FieldHandler = Callable[[Any, str], bool | Awaitable[bool | tuple[bool, str | None]]]
OperatorHandler = Callable[[Any, Any], bool | Awaitable[bool]]


async def evaluate(
    node: QueryGroup | QueryRule | dict[str, Any] | None,
    data: dict[str, Any | FieldHandler],
    field_labels: dict[str, str] | None = None,
    operator_handlers: dict[str, OperatorHandler] | None = None,
) -> EvaluationResult:
    if not node:
        return EvaluationResult(False, ["An internal error occured: empty node"])

    field_labels = field_labels or {}
    operator_handlers = operator_handlers or {}

    if "criteria" in node:
        criteria = cast(list[dict[str, Any]], node["criteria"])
        if not criteria:
            return EvaluationResult(True, [])
        normalized = [
            {
                "field": criterion.get("criterion", criterion.get("field", "")),
                "operator": criterion.get("operator", ""),
                "value": criterion.get("value", ""),
            }
            for criterion in criteria
        ]
        results = [await evaluate(rule, data, field_labels, operator_handlers) for rule in normalized]
        if all(result.passed for result in results):
            return EvaluationResult(True, [])
        return EvaluationResult(False, [reason for result in results for reason in result.failures])

    if "rules" in node:
        node = cast(QueryGroup, node)

        if not node["rules"]:
            return EvaluationResult(True, [])

        results = [await evaluate(rule, data, field_labels, operator_handlers) for rule in node["rules"]]

        passed = (
            all(result.passed for result in results)
            if node["condition"] == "AND"
            else any(result.passed for result in results)
        )

        if passed:
            return EvaluationResult(True, [])

        return EvaluationResult(False, [reason for result in results for reason in result.failures])

    operator_name = node["operator"]
    expected = node.get("value")
    value = data.get(node["field"])
    failure_message: str | None = None

    if callable(value):
        result = value(expected, operator_name)
        final_result = await result if isawaitable(result) else (result, None)

        if isinstance(final_result, tuple):
            passed = final_result[0]
            failure_message = final_result[1]
        else:
            passed = final_result
    elif operator_name in operator_handlers:
        custom_result = operator_handlers[operator_name](value, expected)
        passed = await custom_result if isawaitable(custom_result) else custom_result
    else:
        passed = use_operator(operator_name, value, expected)

    if passed:
        return EvaluationResult(True, [])

    label = field_labels.get(node["field"], node["field"])

    return EvaluationResult(False, [failure_message or describe_failure(label, operator_name, expected)])
