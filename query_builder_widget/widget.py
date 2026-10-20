import json
import re
from contextlib import suppress
from dataclasses import asdict, is_dataclass
from typing import Any, cast

from django import forms
from django.utils.safestring import mark_safe

from .script import SCRIPT
from .style import STYLE
from .types import Criterion, FieldOperators, OperatorPair, QueryBuilderField

DEFAULT_OPERATORS = [
    ("equal", "="),
    ("not_equal", "!="),
    ("contains", "contains"),
    ("not_contains", "doesn't contain"),
    ("greater", ">"),
    ("greater_or_equal", ">="),
    ("less", "<"),
    ("less_or_equal", "<="),
]
_BUILTIN_INPUTS = {"text", "number", "date", "select", "boolean"}


def _format_operators(operators: FieldOperators | list | None) -> list[OperatorPair] | None:
    if not operators:
        return None
    if isinstance(operators[0], str):
        return [cast(OperatorPair, operators)]
    return list(cast(tuple[OperatorPair, ...], operators))


def _definition_dict(key: str, definition: Criterion | dict[str, Any] | QueryBuilderField) -> dict[str, Any]:
    if isinstance(definition, Criterion):
        if definition.id != key:
            raise ValueError(f"Criterion key {key!r} does not match its id {definition.id!r}.")
        result = asdict(definition)
        result["text"] = result.pop("label")
        return result
    if is_dataclass(definition):
        return asdict(definition)
    return dict(definition)


def _parse_fields(
    definitions: dict[str, Criterion | dict[str, Any] | QueryBuilderField] | list[Criterion] | tuple[Criterion, ...],
) -> tuple[list[list[str]], dict[str, list[OperatorPair]], dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    if isinstance(definitions, (list, tuple)):
        mapped = {criterion.id: criterion for criterion in definitions}
    else:
        mapped = definitions
    choices: list[list[str]] = []
    field_operators: dict[str, list[OperatorPair]] = {}
    field_extras: dict[str, list[dict[str, Any]]] = {}
    field_inputs: dict[str, dict[str, Any]] = {}

    for key, raw_definition in mapped.items():
        value = _definition_dict(key, raw_definition)
        label = value.get("text", value.get("label", key))
        choices.append([str(key), str(label)])

        new_operators = _format_operators(value.get("operators"))
        if new_operators:
            field_operators[key] = new_operators

        extras = value.get("extra_fields", [])
        if extras:
            field_extras[key] = list(extras)

        input_type = str(value.get("input", value.get("input_type", "text")))
        options = value.get("options", value.get("choices", [])) or []
        if input_type == "boolean" and not options:
            options = [["true", "Yes"], ["false", "No"]]
        if input_type not in _BUILTIN_INPUTS:
            # Unknown types are permitted only when a custom renderer is registered.
            pass
        field_inputs[key] = {
            "type": input_type,
            "options": options,
            "placeholder": value.get("placeholder", "value"),
        }
    return choices, field_operators, field_extras, field_inputs


def _serialize_custom_renderers(renderers: dict[str, str] | None) -> str:
    """Build trusted JavaScript function map for custom input types.

    Each value must be a JavaScript function expression accepting
    ``(rule, pathAttr, escapeHtml, config)`` and returning an HTML string.
    Only use source code controlled by the application developer.
    """
    parts = []
    for name, source in (renderers or {}).items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name):
            raise ValueError(f"Invalid custom input type name: {name!r}")
        source = source.strip()
        if not source:
            raise ValueError(f"Custom renderer for {name!r} cannot be empty.")
        parts.append(f"{json.dumps(name)}: ({source})")
    return "{" + ",".join(parts) + "}"


class QueryBuilderWidget(forms.Textarea):
    """Django widget for a flat, criteria-based query editor.

    New code should pass ``criteria=[Criterion(...)]``. The older positional
    ``fields`` API remains supported and keeps the legacy ``rules`` payload.
    New ``criteria=`` usage serializes as ``{"criteria": [...]}``.
    """

    def __init__(
        self,
        fields: dict[str, QueryBuilderField] | None = None,
        *,
        criteria: list[Criterion] | tuple[Criterion, ...] | dict[str, Any] | None = None,
        operators: list[tuple[str, str]] | None = None,
        input_renderers: dict[str, str] | None = None,
        add_label: str = "Add criteria",
    ):
        if fields is not None and criteria is not None:
            raise TypeError("Pass either 'fields' (legacy API) or 'criteria', not both.")
        definitions = criteria if criteria is not None else (fields or {})
        self.criteria_mode = criteria is not None
        self.operators = operators or DEFAULT_OPERATORS
        self.fields_choices, self.field_operators, self.field_extras, self.field_inputs = _parse_fields(definitions)
        self.input_renderers = input_renderers or {}
        self.add_label = add_label
        for definition in self.field_inputs.values():
            input_type = definition["type"]
            if input_type not in _BUILTIN_INPUTS and input_type not in self.input_renderers:
                raise ValueError(
                    f"Input type {input_type!r} is not built in and has no registered custom renderer."
                )
        super().__init__()

    def render(self, name: str, value: Any, attrs=None, renderer=None):
        attrs = dict(attrs or {})
        widget_id = attrs.get("id", f"id_{name}")
        container_id = f"{widget_id}_qb"
        payload: dict[str, Any] = {"criteria": []} if self.criteria_mode else {"condition": "AND", "rules": []}

        if value:
            with suppress(TypeError, ValueError):
                parsed = value if isinstance(value, dict) else json.loads(value)
                if isinstance(parsed, dict):
                    if self.criteria_mode and isinstance(parsed.get("criteria"), list):
                        payload = {"criteria": parsed["criteria"]}
                    elif isinstance(parsed.get("rules"), list):
                        # Existing data can be edited using the new flat criteria UI.
                        if self.criteria_mode:
                            payload = {"criteria": self._legacy_rules_to_criteria(parsed["rules"])}
                        else:
                            payload = {"condition": "AND", "rules": parsed["rules"]}

        attrs["style"] = "display:none;"
        html = super().render(name, json.dumps(payload), attrs, renderer)
        formatted_script = SCRIPT.format(
            container_id=json.dumps(container_id),
            widget_id=json.dumps(widget_id),
            fields_json=json.dumps(self.fields_choices),
            operators_json=json.dumps(self.operators),
            field_operators_json=json.dumps(self.field_operators),
            field_extras_json=json.dumps(self.field_extras),
            field_inputs_json=json.dumps(self.field_inputs),
            rules_json=json.dumps(payload),
            criteria_mode="true" if self.criteria_mode else "false",
            add_label_json=json.dumps(self.add_label),
            custom_renderers_js=_serialize_custom_renderers(self.input_renderers),
        )
        return mark_safe(
            f'<div class="simple-qb" id={json.dumps(container_id)}></div>{html}'
            f"<style>{STYLE}</style>"
            f"<script>(function(){{{formatted_script}}})();</script>"
        )

    @staticmethod
    def _legacy_rules_to_criteria(rules: list[Any]) -> list[dict[str, Any]]:
        flat: list[dict[str, Any]] = []
        for item in rules:
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("rules"), list):
                flat.extend(QueryBuilderWidget._legacy_rules_to_criteria(item["rules"]))
            elif "field" in item:
                flat.append({
                    "criterion": item.get("field", ""),
                    "operator": item.get("operator", ""),
                    "value": item.get("value", ""),
                    **({"extra": item["extra"]} if isinstance(item.get("extra"), dict) else {}),
                })
        return flat
