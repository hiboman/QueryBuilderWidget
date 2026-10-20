STYLE = """
.simple-qb {
    box-sizing: border-box;
    border: 1px solid var(--border-color, #383838);
    border-left: 6px solid var(--link-fg, #417690);
    border-radius: 8px;
    background: var(--darkened-bg, #202020);
    color: var(--body-fg, #f0f0f0);
    padding: 14px 16px 12px;
    margin: 4px 0;
}

.simple-qb .qb-criteria {
    display: flex;
    flex-direction: column;
    gap: 18px;
    margin: 0;
    padding: 0;
}

.simple-qb .qb-actions {
    display: flex;
    gap: 6px;
    margin-top: 12px;
}

.simple-qb select,
.simple-qb input[type="text"],
.simple-qb input[type="number"],
.simple-qb input[type="date"] {
    box-sizing: border-box;
    background: var(--body-bg, #111);
    color: var(--body-fg, #f0f0f0);
    border: 1px solid var(--border-color, #383838);
    border-radius: 7px;
    padding: 7px 10px;
    font-size: 14px;
    min-width: 0;
}

.simple-qb select:focus-visible,
.simple-qb input[type="text"]:focus-visible,
.simple-qb input[type="number"]:focus-visible,
.simple-qb input[type="date"]:focus-visible {
    outline: 2px solid var(--link-fg, #447e9b);
    outline-offset: 1px;
}

/* A criterion is not a nested card: keep the single outer panel from the original UI. */
.simple-qb .qb-rule {
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-width: 0;
    margin: 0;
    padding: 0;
    border: 0;
    border-radius: 0;
    background: transparent;
}

.simple-qb .qb-main-row {
    display: grid;
    grid-template-columns: minmax(220px, 33.3%) 92px 145px minmax(20px, 1fr) auto;
    align-items: center;
    gap: 10px;
    min-width: 0;
}

.simple-qb .qb-main-row .qb-field-select,
.simple-qb .qb-main-row .qb-operator-select,
.simple-qb .qb-main-row .qb-value {
    height: 50px;
    min-height: 50px;
    width: 100%;
    font-size: 16px;
}

.simple-qb .qb-main-row .qb-field-select:focus {
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--link-fg, #417690) 42%, transparent);
}

.simple-qb .qb-main-row .qb-operator-select {
    padding-left: 12px;
    padding-right: 8px;
    text-align: center;
}

.simple-qb .qb-main-row .qb-value {
    padding: 8px 12px;
}

.simple-qb .qb-extra-rows {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    min-width: 0;
}

.simple-qb .qb-extra-row {
    display: grid;
    grid-template-columns: var(--qb-extra-columns, repeat(var(--qb-extra-count, 2), minmax(0, 1fr)));
    gap: 12px;
    align-items: stretch;
    width: 100%;
    min-width: 0;
}

.simple-qb .qb-extra-row[data-count="2"] {
    width: min(100%, 1050px);
}

.simple-qb .qb-extra-row[data-count="3"] {
    width: min(100%, 1340px);
}

.simple-qb .qb-extra-row-legacy {
    display: flex;
    flex-wrap: wrap;
    width: 100%;
}

.simple-qb .qb-extra-label {
    box-sizing: border-box;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-width: 0;
    min-height: 56px;
    padding: 7px 16px;
    border: 1px solid var(--border-color, #383838);
    border-radius: 8px;
    background: var(--body-bg, #111);
    color: var(--body-quiet-color, #d0d0d0);
    font-size: 13px;
    font-weight: 700;
    line-height: 1.25;
    text-transform: uppercase;
    white-space: nowrap;
}

.simple-qb .qb-extra-text {
    display: block;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
}

.simple-qb .qb-extra-label > input {
    background: var(--darkened-bg, #202020);
    flex: 0 1 var(--qb-input-width, 176px);
    width: var(--qb-input-width, 176px);
    max-width: 60%;
    min-width: 90px;
    height: 42px;
}

.simple-qb .qb-extra-label > select {
    background: var(--darkened-bg, #202020);
    flex: 0 0 96px;
    width: 96px;
    height: 42px;
}

.simple-qb .qb-extra-controls {
    display: flex;
    flex: 0 1 184px;
    align-items: center;
    gap: 8px;
    min-width: 0;
}

.simple-qb .qb-extra-controls select {
    background: var(--darkened-bg, #202020);
    flex: 0 0 64px;
    width: 64px;
    height: 42px;
}

.simple-qb .qb-extra-controls input {
    background: var(--darkened-bg, #202020);
    flex: 1 1 112px;
    width: 112px;
    min-width: 72px;
    height: 42px;
}

.simple-qb button {
    font-size: 14px;
    cursor: pointer;
    border-radius: 7px;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}

.simple-qb button:focus-visible {
    outline: 2px solid var(--link-fg, #447e9b);
    outline-offset: 1px;
}

.simple-qb button.qb-btn {
    background: var(--button-bg, #333);
    color: var(--button-fg, #fff);
    border: 1px solid var(--border-color, #383838);
    padding: 7px 12px;
    margin-top: 0;
}

.simple-qb button.qb-btn:hover {
    background: var(--button-hover-bg, #444);
}

.simple-qb button.qb-remove {
    justify-self: end;
    white-space: nowrap;
    background: transparent;
    color: #f0202b;
    border: 1px solid #d92332;
    padding: 6px 14px;
    min-height: 34px;
}

.simple-qb button.qb-remove:hover {
    background: rgb(217 35 50 / 12%);
    border-color: #ff3b46;
}

@media (max-width: 1000px) {
    .simple-qb .qb-main-row {
        grid-template-columns: minmax(180px, 1fr) 92px 145px auto;
    }

    .simple-qb .qb-extra-row[data-count="2"],
    .simple-qb .qb-extra-row[data-count="3"] {
        width: 100%;
        max-width: 100% !important;
    }

    .simple-qb .qb-extra-label {
        white-space: normal;
        gap: 8px;
        padding: 7px 10px;
    }
}

@media (max-width: 700px) {
    .simple-qb {
        padding: 10px;
    }

    .simple-qb .qb-main-row {
        grid-template-columns: minmax(0, 1fr) minmax(88px, 0.5fr);
        gap: 8px;
    }

    .simple-qb .qb-main-row .qb-field-select {
        grid-column: 1 / -1;
        grid-row: 1;
    }

    .simple-qb .qb-main-row .qb-operator-select {
        grid-column: 1;
        grid-row: 2;
    }

    .simple-qb .qb-main-row .qb-value {
        grid-column: 2;
        grid-row: 2;
    }

    .simple-qb .qb-main-row .qb-remove {
        grid-column: 1 / -1;
        grid-row: 3;
        justify-self: end;
    }

    .simple-qb .qb-extra-row,
    .simple-qb .qb-extra-row[data-count="2"],
    .simple-qb .qb-extra-row[data-count="3"] {
        grid-template-columns: minmax(0, 1fr) !important;
        width: 100%;
        max-width: 100% !important;
    }

    .simple-qb .qb-extra-label {
        white-space: normal;
    }
}
"""
