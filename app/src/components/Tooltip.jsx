import React from "react";

// Accessible hover and focus tooltip. The trigger is keyboard focusable so the
// metric definition, source, and vintage are reachable without a mouse.
export default function Tooltip({ label, children }) {
  return (
    <span className="tip-wrap" tabIndex={0} aria-label={label}>
      {label}
      <span className="tip-icon" aria-hidden="true">
        i
      </span>
      <span className="tip-body" role="tooltip">
        {children}
      </span>
    </span>
  );
}
