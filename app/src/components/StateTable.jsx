import React from "react";
import Tooltip from "./Tooltip.jsx";
import { COLUMN_ORDER, formatValue, pendingReason } from "../format.js";

function Cell({ stateRow, metricKey, metricMeta }) {
  const cell = stateRow.metrics[metricKey];
  const { text, pending } = formatValue(cell, metricMeta);

  if (pending) {
    return (
      <td className="num pending" title={pendingReason(cell)}>
        {text}
      </td>
    );
  }

  const flags = stateRow.flags || {};
  let badge = null;
  if (metricKey === "snap_apt_timely" && flags.snap_below_corrective_action) {
    badge = <span className="badge below" title="Below the SNAP 90% corrective-action threshold">below 90%</span>;
  }
  if (metricKey === "ui_first_pay_14_21" && flags.ui_below_secretarys_standard) {
    badge = <span className="badge below" title="Below the UI 87% Secretary's Standard">below 87%</span>;
  }

  return (
    <td className="num">
      <span className="value">{text}</span>
      {badge}
    </td>
  );
}

export default function StateTable({ dataset, rows, sortKey, sortDir, onSort }) {
  const metrics = dataset.metrics;

  const headerSort = (key) => {
    if (sortKey !== key) return "";
    return sortDir === "asc" ? " sorted-asc" : " sorted-desc";
  };

  return (
    <div className="table-scroll">
      <table className="state-table">
        <thead>
          <tr>
            <th
              className={"state-col sortable" + headerSort("name")}
              onClick={() => onSort("name")}
            >
              State
            </th>
            {COLUMN_ORDER.map((key) => {
              const m = metrics[key];
              return (
                <th
                  key={key}
                  className={"num sortable" + headerSort(key)}
                  onClick={() => onSort(key)}
                  scope="col"
                >
                  <Tooltip label={m.short_label}>
                    <strong>{m.label}</strong>
                    <br />
                    {m.definition}
                    <br />
                    <em>Source: {m.source_label}</em>
                    {m.threshold_label ? (
                      <>
                        <br />
                        {m.threshold_label}
                      </>
                    ) : null}
                    {!m.available ? (
                      <>
                        <br />
                        <span className="pending-note">
                          Pending in this build; not yet ingested.
                        </span>
                      </>
                    ) : null}
                  </Tooltip>
                  <div className="vintage-tag">
                    {m.vintage ? m.vintage : "vintage pending"}
                  </div>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((s) => (
            <tr key={s.code} className={s.excluded_from_ranking ? "territory" : ""}>
              <td className="state-col">
                {s.name}
                {s.excluded_from_ranking ? (
                  <span className="badge territory-badge" title="Territory: shown where data exists, excluded from ranking">
                    not ranked
                  </span>
                ) : null}
              </td>
              {COLUMN_ORDER.map((key) => (
                <Cell
                  key={key}
                  stateRow={s}
                  metricKey={key}
                  metricMeta={metrics[key]}
                />
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
