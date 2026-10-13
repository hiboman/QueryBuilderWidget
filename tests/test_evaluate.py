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
