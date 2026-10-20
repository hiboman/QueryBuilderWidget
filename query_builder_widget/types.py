from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, NamedTuple, NotRequired, TypedDict

OperatorPair = tuple[str, str]
FieldOperators = OperatorPair | tuple[OperatorPair, ...]


@dataclass(frozen=True)
class Criterion:
    """Declarative definition of one selectable criterion.

    ``input`` can be text, number, date, select, boolean, or a custom input
    registered with ``QueryBuilderWidget(input_renderers=...)``.
    """

    id: str
    label: str
    operators: FieldOperators | None = None
    input: str = "text"
    options: list[tuple[str, str]] | list[list[str]] = field(default_factory=list)
    placeholder: str = "value"
    extra_fields: list[dict[str, Any]] = field(default_factory=list)


class QueryBuilderField(TypedDict):
    """Legacy field definition; retained for backwards compatibility."""

    text: str
    operators: NotRequired[FieldOperators]
    extra_fields: NotRequired[list[dict[str, object]]]
    input: NotRequired[str]
    options: NotRequired[list[tuple[str, str]] | list[list[str]]]
    placeholder: NotRequired[str]


class QueryRule(TypedDict):
    field: str
    value: str
    operator: str
    extra: NotRequired[dict[str, str]]


class QueryCriterion(TypedDict):
    criterion: str
    value: str
    operator: str
    extra: NotRequired[dict[str, str]]


class QueryGroup(TypedDict):
    rules: list[QueryGroup | QueryRule]
    condition: Literal["AND", "OR"]


class EvaluationResult(NamedTuple):
    passed: bool
    failures: list[str]
