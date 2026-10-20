from typing import cast

import pytest  # noqa: F401

from query_builder_widget import evaluate
from query_builder_widget.types import QueryGroup

GOOD_CONDITIONS: QueryGroup = {
    "rules": [
        {"field": "server", "value": "1255250024741212262", "operator": "equals"},
        {
            "rules": [
                {"field": "completion", "value": "70", "operator": "greater_or_equal"},
                {"field": "ballcount", "value": "5", "operator": "greater_or_equal"},
            ],
            "condition": "AND",
        },
    ],
    "condition": "OR",
}

IGNORABLE_CONDITIONS_AND: QueryGroup = {"rules": [], "condition": "AND"}
IGNORABLE_CONDITIONS_OR: QueryGroup = {"rules": [], "condition": "OR"}


async def test_evaluation_good():
    data = {"server": "1255250024741212262", "completion": "50", "ballcount": "7"}

    result = await evaluate(
        GOOD_CONDITIONS,
        data,
        field_labels={"server": "Server", "completion": "Ball completion", "ballcount": "Ball count"},
    )

    assert result.passed, ", ".join(result.failures)


async def test_evaluation_ignorable_and():
    result = await evaluate(IGNORABLE_CONDITIONS_AND, {})

    assert result.passed, ", ".join(result.failures)


async def test_evaluation_ignorable_or():
    result = await evaluate(IGNORABLE_CONDITIONS_OR, {})

    assert result.passed, ", ".join(result.failures)


async def test_evaluation_empty():
    result = await evaluate(cast(QueryGroup, {}), {})

    assert not result.passed


async def test_flat_criteria_payload_uses_and_semantics():
    result = await evaluate(
        {
            "criteria": [
                {"criterion": "count", "operator": "greater", "value": "5"},
                {"criterion": "country", "operator": "equals", "value": "DK"},
            ]
        },
        {"count": "8", "country": "DK"},
    )
    assert result.passed, ", ".join(result.failures)


async def test_flat_criteria_payload_fails_if_any_criterion_fails():
    result = await evaluate(
        {
            "criteria": [
                {"criterion": "count", "operator": "greater", "value": "5"},
                {"criterion": "country", "operator": "equals", "value": "DK"},
            ]
        },
        {"count": "8", "country": "DE"},
    )
    assert not result.passed


async def test_custom_operator_handler():
    async def starts_with(actual, expected):
        return str(actual).startswith(str(expected))

    result = await evaluate(
        {"criteria": [{"criterion": "country", "operator": "starts_with", "value": "D"}]},
        {"country": "Denmark"},
        operator_handlers={"starts_with": starts_with},
    )
    assert result.passed, ", ".join(result.failures)


async def test_custom_operator_handler_failure_is_reported():
    result = await evaluate(
        {"criteria": [{"criterion": "country", "operator": "starts_with", "value": "X"}]},
        {"country": "Denmark"},
        operator_handlers={"starts_with": lambda actual, expected: str(actual).startswith(str(expected))},
    )
    assert not result.passed
    assert result.failures
