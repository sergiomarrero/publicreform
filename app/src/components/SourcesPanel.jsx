import React from "react";
import { COLUMN_ORDER } from "../format.js";

// Lists every dataset, its agency, vintage, and a link to the primary source.
// Non-negotiable for the foundation audience.
export default function SourcesPanel({ dataset }) {
  const metrics = dataset.metrics;
  const seen = new Set();
  const entries = [];
  for (const key of COLUMN_ORDER) {
    const m = metrics[key];
    const id = m.source_name + "|" + (m.vintage || "");
    if (seen.has(id)) continue;
    seen.add(id);
    entries.push(m);
  }

  return (
    <section className="panel" id="sources">
      <h2>Sources and vintages</h2>
      <p className="panel-intro">
        Every figure in the table carries the source and vintage below. Values
        are stored raw, with their units. Nothing is blended or scored in this
        version.
      </p>
      <ul className="sources-list">
        {entries.map((m) => (
          <li key={m.source_name + m.vintage}>
            <span className="source-name">{m.source_name}</span>
            <span className="source-meta">
              {m.agency}
              {m.vintage ? ", " + m.vintage : ", vintage pending"}
            </span>
            <a href={m.primary_url} target="_blank" rel="noreferrer">
              primary source
            </a>
            {!m.available ? (
              <span className="badge pending-badge">pending in this build</span>
            ) : (
              <span className="badge live-badge">live</span>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
