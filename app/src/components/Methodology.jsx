import React from "react";

// Plain-language methodology note. Descriptive and correlational framing only.
export default function Methodology({ dataset }) {
  const scope = dataset.meta.scope;
  const interpretation = dataset.meta.interpretation;
  return (
    <section className="panel" id="methodology">
      <h2>Methodology</h2>
      <p>
        This dashboard characterizes how state public-benefit and workforce
        systems perform across three dimensions: speed, fragmentation, and
        navigability. Version 1 leads with raw metrics from three programs:
        Unemployment Insurance, SNAP, and WIOA. Each value is shown as published
        by its agency, with a source and vintage label.
      </p>
      <p>
        <strong>Scope.</strong> {scope}
      </p>
      <p>
        <strong>Reading the data.</strong> {interpretation} Two federal
        standards are flagged for context: the SNAP corrective-action threshold
        of 90 percent timely, and the UI Secretary's Standard of 87 percent of
        first payments within 14/21 days. A flag marks a state below a standard;
        it does not assign a grade.
      </p>
      <p>
        <strong>What is not here yet.</strong> A blended 0 to 100 composite index
        is planned for a later stage and is not computed or shown in this
        version. Where a dimension is still pending a live source, its column
        shows pending rather than a number.
      </p>
    </section>
  );
}
