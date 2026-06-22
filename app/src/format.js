// Formatting helpers. No number is rendered without a unit, and a missing
// value is shown as pending rather than as a fabricated figure.

export const COLUMN_ORDER = [
  "ui_first_pay_14_21",
  "snap_apt_timely",
  "wioa_adult_emp_q2",
  "wioa_adult_median_earnings_q2",
  "wioa_adult_credential",
];

export function formatValue(cell, metricMeta) {
  if (!cell || cell.value === null || cell.value === undefined) {
    return { text: "Pending", pending: true };
  }
  if (metricMeta.unit === "usd") {
    return { text: "$" + Number(cell.value).toLocaleString("en-US"), pending: false };
  }
  if (metricMeta.unit === "percent") {
    return { text: Number(cell.value).toFixed(2) + "%", pending: false };
  }
  return { text: String(cell.value), pending: false };
}

export function pendingReason(cell) {
  const reason = cell && cell.null_reason;
  switch (reason) {
    case "source_host_blocked_by_network_policy":
      return "Live source not yet ingested in this build.";
    case "source_unavailable_at_fetch_time":
      return "Source was not reachable at fetch time.";
    case "not_reported_by_source":
      return "Not reported by the source for this jurisdiction.";
    default:
      return "Pending a source.";
  }
}

// Sort comparator that always pushes pending (null) values to the bottom.
export function compareValues(a, b, dir) {
  const av = a === null || a === undefined ? null : a;
  const bv = b === null || b === undefined ? null : b;
  if (av === null && bv === null) return 0;
  if (av === null) return 1;
  if (bv === null) return -1;
  return dir === "asc" ? av - bv : bv - av;
}
