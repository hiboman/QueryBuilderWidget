# QueryBuilderWidget

A Django widget for building **flat, criteria-based queries**. The widget provides the UI; the application defines the available criteria, their operators, input controls, and evaluation behavior. There are no groups and no ALL/ANY selector. Criteria use AND semantics.

## New API

```python
from query_builder_widget import Criterion, QueryBuilderWidget

criteria = [
    Criterion(
        id="ball_count",
        label="Ball count",
        input="number",
        operators=(("equals", "="), ("greater", ">"), ("less", "<")),
        placeholder="Enter a count",
    ),
    Criterion(
        id="country",
        label="Country",
        input="select",
        options=(("DK", "Denmark"), ("DE", "Germany")),
        operators=(("equals", "is"), ("not_equals", "is not")),
    ),
    Criterion(
        id="favourite",
        label="Is favourite",
        input="boolean",
        operators=(("eq", "is"),),
    ),
]

widget = QueryBuilderWidget(criteria=criteria)
```

`Criterion` accepts:

- `id`: stable application-defined identifier.
- `label`: text displayed in the criterion selector.
- `operators`: allowed `(value, label)` pairs for that criterion.
- `input`: `text` (default), `number`, `date`, `select`, `boolean`, or a registered custom input type.
- `options`: `(value, label)` choices for `select` and `boolean` inputs. Boolean defaults to Yes/No.
- `placeholder`: placeholder for text, number, or date input.
- `extra_fields`: optional auxiliary controls shown for this criterion. Each item uses `key`, `text`, `type`, and optional `placeholder` or `choices`.

The form value for the new API uses a stable, flat schema:

```json
{
  "criteria": [
    {"criterion": "ball_count", "operator": "greater", "value": "100"},
    {"criterion": "country", "operator": "equals", "value": "DK"}
  ]
}
```

Every criterion must pass. The widget only collects and serializes selections; it does not decide what `ball_count` or `country` means in your application.

## Custom input types

Applications can register a JavaScript renderer for a new scalar input type. A renderer is a trusted JavaScript function expression receiving `(criterion, pathAttr, escapeHtml, config)` and returning HTML. Its input element must have `data-role="value"` and `data-path="${pathAttr}"`; the widget listens for `input` or `change` and saves the element's `.value`.

```python
widget = QueryBuilderWidget(
    criteria=[Criterion(id="server", label="Server", input="server-picker")],
    input_renderers={
        "server-picker": "(criterion, pathAttr, escapeHtml, config) => `"
            + '<input type="text" data-role="value" data-path="${pathAttr}" '
            + 'value="${escapeHtml(criterion.value)}" placeholder="Choose a server">'
            + "`",
    },
)
```

Only register renderer source controlled by your application: it is inserted into the page as executable JavaScript. For a custom picker that needs asynchronous data loading, the renderer can return a normal HTML input and application JavaScript can enhance it separately.

## Per-criterion auxiliary controls

For criteria that need extra filters, use `extra_fields`. These values are stored under `extra` on that criterion and are passed through without interpretation.

```python
Criterion(
    id="ball_count",
    label="Ball count",
    input="number",
    operators=(("greater_or_equal", "≥"), ("less_or_equal", "≤")),
    extra_fields=[
        {"key": "ball_ids", "text": "Ball IDs", "type": "text", "placeholder": "IDs separated by commas"},
        {"key": "favourite", "text": "Favourite", "type": "select",
         "choices": [("", "Any"), ("true", "Yes"), ("false", "No")]},
    ],
)
```

Example serialized criterion:

```json
{"criterion":"ball_count","operator":"greater_or_equal","value":"10","extra":{"ball_ids":"3,4","favourite":"true"}}
```

## Evaluation

The evaluator supports the new `criteria` payload and requires every criterion to pass:

```python
from query_builder_widget import evaluate

result = await evaluate(
    {"criteria": [
        {"criterion": "ball_count", "operator": "greater", "value": "10"},
        {"criterion": "country", "operator": "equals", "value": "DK"},
    ]},
    {"ball_count": "12", "country": "DK"},
    field_labels={"ball_count": "Ball count", "country": "Country"},
)
```

Applications should validate submitted criteria against their own definitions and implement any domain-specific evaluation or database translation themselves. The generic evaluator handles scalar values and registered callable field handlers; it does not interpret `extra` values automatically.

Custom operators can be registered at evaluation time without modifying the widget package:

```python
result = await evaluate(
    {"criteria": [{"criterion": "country", "operator": "starts_with", "value": "D"}]},
    {"country": "Denmark"},
    operator_handlers={"starts_with": lambda actual, expected: str(actual).startswith(str(expected))},
)
```

An operator handler may be synchronous or asynchronous. Its operator identifier should also be included in that criterion's `operators` definition so the UI can offer it.

## Backwards compatibility

The legacy API `QueryBuilderWidget(fields, operators=...)` remains supported and emits the older `{"condition":"AND","rules":[...]}` shape. Existing `rules` payloads can also be loaded into the new flat criteria UI; nested groups are flattened and their old OR semantics are intentionally not retained. New projects should use `Criterion` and `QueryBuilderWidget(criteria=...)`.


## Custom row layout for auxiliary fields

An application can arrange `extra_fields` into explicit rows by adding a numeric `row` property to each definition. Fields with the same row number appear side by side; rows are rendered in numeric order. Definitions without `row` retain the legacy inline layout when no explicit row is used.

```python
Criterion(
    id="ball_count",
    label="Ball count",
    operators=(("gte", "≥"),),
    extra_fields=[
        {"key": "ball_ids", "text": "Ball ID", "type": "text", "row": 1},
        {"key": "country", "text": "Country", "type": "text", "row": 1},
        {"key": "special", "text": "Special", "type": "text", "row": 2},
        {"key": "has_special", "text": "Has Special", "type": "select", "choices": [("", "Any"), ("true", "Yes"), ("false", "No")], "row": 2},
        {"key": "self_caught", "text": "Self Caught", "type": "select", "choices": [("", "Any"), ("true", "Yes"), ("false", "No")], "row": 2},
    ],
)
```

Each criterion card displays its `Field`, `Operator`, and `Value` controls in the first row. Configured auxiliary fields render below them in the application-defined rows, followed by the add-criterion button.
