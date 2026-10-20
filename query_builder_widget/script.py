SCRIPT = r"""
const container = document.getElementById({container_id});
const input = document.getElementById({widget_id});
const fields = {fields_json};
const operators = {operators_json};
const fieldOperators = {field_operators_json};
const fieldExtras = {field_extras_json};
const fieldInputs = {field_inputs_json};
const criteriaMode = {criteria_mode};
const addLabel = {add_label_json};
const customRenderers = {custom_renderers_js};
const initial = {rules_json};
const state = {{ rules: [] }};
const durationOperators = [['lt', '<'], ['lte', '≤'], ['eq', '='], ['gte', '≥'], ['gt', '>'], ['ne', '≠']];

function escapeHtml(value) {{
    const div = document.createElement('div');
    div.textContent = String(value ?? '');
    return div.innerHTML;
}}

function opts(list, selected) {{
    return (list || []).map(([value, label]) =>
        `<option value="${{escapeHtml(value)}}"${{String(value) === String(selected) ? ' selected' : ''}}>${{escapeHtml(label)}}</option>`
    ).join('');
}}

function sync() {{
    const criteria = state.rules.map((rule) => ({{
        criterion: rule.field,
        operator: rule.operator,
        value: rule.value ?? '',
        ...(rule.extra && Object.keys(rule.extra).length ? {{ extra: rule.extra }} : {{}}),
    }}));
    input.value = JSON.stringify(criteriaMode ? {{ criteria }} : {{ condition: 'AND', rules: state.rules }});
}}

function isValueless(operator) {{
    return operator === 'is_null' || operator === 'is_not_null';
}}

function operatorsFor(field) {{
    return fieldOperators[field] || operators;
}}

function normalizeRule(rule) {{
    return {{
        field: rule.criterion ?? rule.field ?? (fields.length ? fields[0][0] : ''),
        operator: rule.operator ?? '',
        value: rule.value ?? '',
        ...(rule.extra && typeof rule.extra === 'object' ? {{ extra: rule.extra }} : {{}}),
    }};
}}

const initialItems = criteriaMode
    ? (Array.isArray(initial.criteria) ? initial.criteria : [])
    : (Array.isArray(initial.rules) ? initial.rules : []);
state.rules = initialItems.flatMap((item) => {{
    if (item && typeof item === 'object' && Array.isArray(item.rules)) return item.rules.map(normalizeRule);
    return item && typeof item === 'object' ? [normalizeRule(item)] : [];
}});
state.rules = state.rules.map((rule) => {{
    const available = operatorsFor(rule.field);
    if (!available.some(([key]) => key === rule.operator)) rule.operator = available.length ? available[0][0] : '';
    return rule;
}});

function pathToAttr(path) {{ return path.join('.'); }}
function attrToPath(attr) {{ return attr === '' ? [] : attr.split('.').map(Number); }}
function getNode(path) {{
    if (path.length === 0) return state;
    return state.rules[path[0]];
}}

function defaultRule() {{
    const field = fields.length ? fields[0][0] : '';
    const fieldOps = operatorsFor(field);
    return {{ field, operator: fieldOps.length ? fieldOps[0][0] : '', value: '' }};
}}

function valueTemplate(rule, pathAttr) {{
    if (isValueless(rule.operator)) return '';
    const config = fieldInputs[rule.field] || {{ type: 'text', options: [], placeholder: 'value' }};
    const type = config.type || 'text';
    if (customRenderers[type]) return customRenderers[type](rule, pathAttr, escapeHtml, config);
    if (type === 'select' || type === 'boolean') {{
        return `<select class="qb-value" aria-label="Value" data-role="value" data-path="${{pathAttr}}"><option value="">${{type === 'boolean' ? 'Choose…' : 'Select…'}}</option>${{opts(config.options || [], rule.value)}}</select>`;
    }}
    const htmlType = ['number', 'date'].includes(type) ? type : 'text';
    return `<input class="qb-value" aria-label="Value" type="${{htmlType}}" data-role="value" data-path="${{pathAttr}}" value="${{escapeHtml(rule.value)}}" placeholder="${{escapeHtml(config.placeholder || 'value')}}">`;
}}

function renderExtra(extra, pathAttr, rule) {{
    const key = extra.key;
    const current = String((rule.extra || {{}})[key] ?? '');
    const label = `${{escapeHtml(extra.text)}}:`;
    const inputWidth = extra.input_width !== undefined && extra.input_width !== null && extra.input_width !== ''
        ? ` style="--qb-input-width:${{Number(extra.input_width)}}px"`
        : '';

    if (extra.type === 'duration') {{
        const match = current.match(/^([a-z]+):(.*)$/i);
        const selectedOperator = match ? match[1].toLowerCase() : (extra.default_operator || 'lt');
        const duration = match ? match[2] : '';
        const durationOpts = extra.operators || durationOperators;
        return `<label class="qb-extra-label qb-extra-duration"${{inputWidth}}><span class="qb-extra-text">${{label}}</span><span class="qb-extra-controls"><select aria-label="${{escapeHtml(extra.text)}} operator" data-role="extra-duration-op" data-extra-key="${{escapeHtml(key)}}" data-path="${{pathAttr}}">${{opts(durationOpts, selectedOperator)}}</select><input aria-label="${{escapeHtml(extra.text)}} value" type="text" data-role="extra-duration-value" data-extra-key="${{escapeHtml(key)}}" data-path="${{pathAttr}}" value="${{escapeHtml(duration)}}" placeholder="${{escapeHtml(extra.placeholder || 'e.g. 6h')}}"></span></label>`;
    }}

    if (extra.type === 'select') {{
        const choices = (extra.choices || []).map(([value, choiceLabel]) =>
            `<option value="${{escapeHtml(value)}}"${{String(value) === current ? ' selected' : ''}}>${{escapeHtml(choiceLabel)}}</option>`
        ).join('');
        return `<label class="qb-extra-label"${{inputWidth}}><span class="qb-extra-text">${{label}}</span><select aria-label="${{escapeHtml(extra.text)}}" data-role="extra" data-extra-key="${{escapeHtml(key)}}" data-path="${{pathAttr}}">${{choices}}</select></label>`;
    }}

    const htmlType = extra.type === 'number' ? 'number' : 'text';
    return `<label class="qb-extra-label"${{inputWidth}}><span class="qb-extra-text">${{label}}</span><input aria-label="${{escapeHtml(extra.text)}}" type="${{htmlType}}" data-role="extra" data-extra-key="${{escapeHtml(key)}}" data-path="${{pathAttr}}" value="${{escapeHtml(current)}}" placeholder="${{escapeHtml(extra.placeholder || '')}}"></label>`;
}}

function ruleTemplate(rule, index) {{
    const pathAttr = pathToAttr([index]);
    const fieldOps = operatorsFor(rule.field);
    const valueInput = valueTemplate(rule, pathAttr);
    const extraDefinitions = fieldExtras[rule.field] || [];
    const render = (extra) => renderExtra(extra, pathAttr, rule);

    // The consuming application can group auxiliary inputs with the public `row` key.
    // Each group stays on one horizontal line; fields without a row follow afterward.
    const hasExplicitRows = extraDefinitions.some((extra) => extra.row !== undefined && extra.row !== null);
    let extras;
    if (hasExplicitRows) {{
        const grouped = new Map();
        extraDefinitions.forEach((extra, order) => {{
            const rowKey = extra.row === undefined || extra.row === null ? '__ungrouped__' : String(extra.row);
            if (!grouped.has(rowKey)) grouped.set(rowKey, {{ order, items: [] }});
            grouped.get(rowKey).items.push(extra);
        }});
        extras = Array.from(grouped.entries())
            .sort((a, b) => {{
                if (a[0] === '__ungrouped__') return 1;
                if (b[0] === '__ungrouped__') return -1;
                const an = Number(a[0]);
                const bn = Number(b[0]);
                return Number.isFinite(an) && Number.isFinite(bn) ? an - bn : a[1].order - b[1].order;
            }})
            .map(([, group]) => {{
                const count = group.items.length;
                const configuredWidth = group.items.map((extra) => Number(extra.row_width))
                    .find((width) => Number.isFinite(width) && width > 0);
                const maxWidth = configuredWidth || (count === 2 ? 1050 : (count === 3 ? 1340 : 1050));
                const weights = group.items.map((extra) => {{
                    const weight = Number(extra.weight);
                    return Number.isFinite(weight) && weight > 0 ? weight : 1;
                }});
                const columns = weights.map((weight) => `${{weight}}fr`).join(' ');
                return `<div class="qb-extra-row" data-count="${{count}}" style="--qb-extra-count:${{count}};--qb-extra-columns:${{columns}};max-width:${{maxWidth}}px;">${{group.items.map(render).join('')}}</div>`;
            }})
            .join('');
    }} else {{
        extras = `<div class="qb-extra-row qb-extra-row-legacy">${{extraDefinitions.map(render).join('')}}</div>`;
    }}

    return `
        <div class="qb-rule" data-path="${{pathAttr}}">
            <div class="qb-main-row">
                <select class="qb-field-select" aria-label="Field" data-role="criterion" data-path="${{pathAttr}}">${{opts(fields, rule.field)}}</select>
                <select class="qb-operator-select" aria-label="Operator" data-role="operator" data-path="${{pathAttr}}">${{opts(fieldOps, rule.operator)}}</select>
                ${{valueInput}}
                <button type="button" class="qb-remove" data-role="remove-item" data-path="${{pathAttr}}" aria-label="Remove criterion">&times; Remove</button>
            </div>
            <div class="qb-extra-rows">${{extras}}</div>
        </div>
    `;
}}

function render() {{
    container.innerHTML = `<div class="qb-criteria">${{state.rules.map(ruleTemplate).join('')}}</div>
        <div class="qb-actions"><button type="button" class="qb-btn" data-role="add-criterion">+ ${{escapeHtml(addLabel)}}</button></div>`;
    attach();
    sync();
}}

function attach() {{
    const add = container.querySelector('[data-role="add-criterion"]');
    add.addEventListener('click', () => {{ state.rules.push(defaultRule()); render(); }});

    container.querySelectorAll('[data-role="remove-item"]').forEach((btn) => {{
        btn.addEventListener('click', () => {{ state.rules.splice(Number(attrToPath(btn.dataset.path)[0]), 1); render(); }});
    }});

    container.querySelectorAll('[data-role="criterion"]').forEach((sel) => {{
        sel.addEventListener('change', () => {{
            const node = getNode(attrToPath(sel.dataset.path));
            node.field = sel.value;
            node.value = '';
            node.extra = {{}};
            const fieldOps = operatorsFor(node.field);
            node.operator = fieldOps.length ? fieldOps[0][0] : '';
            render();
        }});
    }});

    container.querySelectorAll('[data-role="operator"]').forEach((sel) => {{
        sel.addEventListener('change', () => {{ getNode(attrToPath(sel.dataset.path)).operator = sel.value; render(); }});
    }});

    container.querySelectorAll('[data-role="value"]').forEach((element) => {{
        const eventName = element.tagName === 'SELECT' ? 'change' : 'input';
        element.addEventListener(eventName, () => {{
            getNode(attrToPath(element.dataset.path)).value = element.value;
            sync();
        }});
    }});

    container.querySelectorAll('[data-role="extra"]').forEach((element) => {{
        const eventName = element.tagName === 'SELECT' ? 'change' : 'input';
        element.addEventListener(eventName, () => {{
            const node = getNode(attrToPath(element.dataset.path));
            node.extra = node.extra || {{}};
            node.extra[element.dataset.extraKey] = element.value;
            sync();
        }});
    }});

    const updateDuration = (element) => {{
        const node = getNode(attrToPath(element.dataset.path));
        const key = element.dataset.extraKey;
        const controls = Array.from(container.querySelectorAll(`[data-extra-key="${{key}}"]`))
            .filter((control) => control.dataset.path === element.dataset.path);
        const operatorControl = controls.find((control) => control.dataset.role === 'extra-duration-op');
        const valueControl = controls.find((control) => control.dataset.role === 'extra-duration-value');
        node.extra = node.extra || {{}};
        node.extra[key] = valueControl && valueControl.value.trim()
            ? `${{operatorControl ? operatorControl.value : 'lt'}}:${{valueControl.value.trim()}}`
            : '';
        sync();
    }};
    container.querySelectorAll('[data-role="extra-duration-op"]').forEach((element) => {{
        element.addEventListener('change', () => updateDuration(element));
    }});
    container.querySelectorAll('[data-role="extra-duration-value"]').forEach((element) => {{
        element.addEventListener('input', () => updateDuration(element));
    }});
}}

render();
"""  # noqa: E501
