import React from "react";

// Visible "coming soon" placeholder for the composite index. The structure is
// present; no score is computed or shown.
export default function CompositePlaceholder({ dataset }) {
  const note = dataset.meta.composite_index && dataset.meta.composite_index.note;
  return (
    <section className="panel composite" id="composite">
      <div className="composite-head">
        <h2>Composite index</h2>
        <span className="badge soon-badge">coming soon</span>
      </div>
      <p>
        {note ||
          "A blended 0 to 100 composite index is planned for a later stage."}
      </p>
      <p className="muted">
        The composite will use percentile-rank normalization with transparent,
        equal weighting and a published weight sensitivity analysis. It is not
        computed in this version, so no score is shown.
      </p>
    </section>
  );
}
