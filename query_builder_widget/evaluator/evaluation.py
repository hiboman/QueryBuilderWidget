from collections.abc import Awaitable, Callable
from inspect import isawaitable
from typing import Any, cast

from ..types import EvaluationResult, QueryGroup, QueryRule
from .operators import describe_failure, use_operator

FieldHandler = Callable[[Any, str], bool | Awaitable[bool | tuple[bool, str | None]]]


async def evaluate(
    node: QueryGroup | QueryRule | None, data: dict[str, Any | FieldHandler], field_labels: dict[str, str] | None = None
) -> EvaluationResult:
    if not node:
        return EvaluationResult(False, ["An internal error occured: empty node"])

    field_labels = field_labels or {}

    if "rules" in node:
        node = cast(QueryGroup, node)

        if not node["rules"]:
            return EvaluationResult(True, [])

        results = [await evaluate(rule, data, field_labels) for rule in node["rules"]]

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
    else:
        passed = use_operator(operator_name, value, expected)

    if passed:
        return EvaluationResult(True, [])

    label = field_labels.get(node["field"], node["field"])

    return EvaluationResult(False, [failure_message or describe_failure(label, operator_name, expected)])
